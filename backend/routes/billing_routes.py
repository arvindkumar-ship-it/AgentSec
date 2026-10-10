from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
import uuid, datetime, os, hmac, hashlib
import razorpay

from auth import get_current_user
from models.sql_models import User
from models.quota_models import Plan, OrganizationPlan, OrganizationQuota, OrgPlanStatusEnum
from models.billing_models import SSOConfig, BillingOrder
from database import get_db as get_pg_db
from services.audit_service import write_audit

router = APIRouter(prefix="/billing", tags=["Billing"])

def payment_client():
    key, secret = os.getenv("RAZORPAY_KEY_ID"), os.getenv("RAZORPAY_KEY_SECRET")
    if not key or not secret:
        raise HTTPException(503, "Payment gateway is not configured")
    return razorpay.Client(auth=(key, secret))

PLAN_QUOTA_MAP = {
    "free": {"max_scans_per_day": 5, "max_evals_per_day": 5, "max_concurrent_scans": 2, "max_storage_mb": 500, "max_users": 3, "max_targets": 5},
    "pro": {"max_scans_per_day": 50, "max_evals_per_day": 50, "max_concurrent_scans": 10, "max_storage_mb": 5000, "max_users": 15, "max_targets": 50},
    "enterprise": {"max_scans_per_day": 500, "max_evals_per_day": 500, "max_concurrent_scans": 50, "max_storage_mb": 50000, "max_users": 100, "max_targets": 500},
}

# Paise (INR smallest unit) — adjust to your actual pricing
PLAN_PRICE_MAP = {
    "free": 0,
    "pro": 99900,        # ₹999
    "enterprise": 499900,  # ₹4999
}


class PlanChangeRequest(BaseModel):
    plan_name: str


async def apply_plan_change(pg_db: AsyncSession, current_user: User, plan_name: str):
    result = await pg_db.execute(select(Plan).where(Plan.name == plan_name))
    plan = result.scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not seeded yet")

    current = await pg_db.execute(select(OrganizationPlan).where(OrganizationPlan.org_id == current_user.org_id, OrganizationPlan.status == OrgPlanStatusEnum.active))
    current_row = current.scalar_one_or_none()
    if current_row:
        current_row.status = OrgPlanStatusEnum.cancelled
        current_row.effective_to = datetime.datetime.utcnow()
    pg_db.add(OrganizationPlan(id=uuid.uuid4(), org_id=current_user.org_id, plan_id=plan.id))

    quota_result = await pg_db.execute(select(OrganizationQuota).where(OrganizationQuota.org_id == current_user.org_id))
    quota = quota_result.scalar_one_or_none()
    new_limits = PLAN_QUOTA_MAP[plan_name]
    if quota:
        for k, v in new_limits.items(): setattr(quota, k, v)
        quota.plan_id = plan.id
    else:
        pg_db.add(OrganizationQuota(id=uuid.uuid4(), org_id=current_user.org_id, plan_id=plan.id, **new_limits))

    await pg_db.commit()
    return new_limits


@router.post("/plan-change")
async def change_plan(payload: PlanChangeRequest, current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if payload.plan_name not in PLAN_QUOTA_MAP:
        raise HTTPException(status_code=400, detail="Invalid plan name")

    if payload.plan_name != "free":
        raise HTTPException(403, "Paid plans require a verified captured payment")
    new_limits = await apply_plan_change(pg_db, current_user, payload.plan_name)
    await write_audit(pg_db, org_id=current_user.org_id, user_id=current_user.id, action="plan_change", target_id=payload.plan_name, metadata=new_limits)
    return {"status": "plan_updated", "plan": payload.plan_name, "quotas": new_limits}


class CreateOrderRequest(BaseModel):
    plan_name: str


@router.post("/create-order")
async def create_order(payload: CreateOrderRequest, current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if payload.plan_name not in PLAN_PRICE_MAP:
        raise HTTPException(status_code=400, detail="Invalid plan name")

    amount = PLAN_PRICE_MAP[payload.plan_name]
    if amount == 0:
        raise HTTPException(status_code=400, detail="Free plan does not require payment")

    order = payment_client().order.create({
        "amount": amount,
        "currency": "INR",
        "notes": {"org_id": str(current_user.org_id), "plan_name": payload.plan_name},
    })

    pg_db.add(BillingOrder(id=order["id"], org_id=current_user.org_id,
                           plan_name=payload.plan_name, amount=amount, currency="INR"))
    await pg_db.commit()

    return {
        "order_id": order["id"],
        "amount": amount,
        "currency": "INR",
        "key_id": os.environ["RAZORPAY_KEY_ID"],
        "plan_name": payload.plan_name,
    }


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str
    plan_name: str


@router.post("/verify-payment")
async def verify_payment(payload: VerifyPaymentRequest, current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if payload.plan_name not in PLAN_QUOTA_MAP:
        raise HTTPException(status_code=400, detail="Invalid plan name")

    result = await pg_db.execute(select(BillingOrder).where(
        BillingOrder.id == payload.razorpay_order_id,
        BillingOrder.org_id == current_user.org_id,
        BillingOrder.plan_name == payload.plan_name).with_for_update())
    stored_order = result.scalar_one_or_none()
    if stored_order is None:
        raise HTTPException(400, "Order was not issued for this organisation and plan")
    if stored_order.paid_at is not None:
        raise HTTPException(409, "Order has already been applied")
    client = payment_client()
    generated_signature = hmac.new(
        os.environ["RAZORPAY_KEY_SECRET"].encode(),
        f"{stored_order.id}|{payload.razorpay_payment_id}".encode(),
        hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(generated_signature, payload.razorpay_signature):
        raise HTTPException(status_code=400, detail="Payment signature verification failed")

    order = client.order.fetch(payload.razorpay_order_id)
    payment = client.payment.fetch(payload.razorpay_payment_id)
    notes = order.get("notes") or {}
    expected = PLAN_PRICE_MAP[payload.plan_name]
    if (expected <= 0 or notes.get("org_id") != str(current_user.org_id)
            or notes.get("plan_name") != payload.plan_name
            or stored_order.amount != expected or stored_order.currency != "INR"
            or order.get("amount") != expected or order.get("currency") != "INR"
            or payment.get("order_id") != payload.razorpay_order_id
            or payment.get("amount") != expected or payment.get("currency") != "INR"
            or payment.get("status") != "captured"):
        raise HTTPException(400, "Payment does not match this organisation and plan")

    stored_order.payment_id = payload.razorpay_payment_id
    stored_order.paid_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
    new_limits = await apply_plan_change(pg_db, current_user, payload.plan_name)
    await write_audit(pg_db, org_id=current_user.org_id, user_id=current_user.id, action="plan_change_paid", target_id=payload.plan_name, metadata=new_limits)
    return {"status": "payment_verified_plan_updated", "plan": payload.plan_name, "quotas": new_limits}


@router.post("/webhook")
async def gateway_webhook(request: Request):
    """STUB — real webhook signature verify baad me webhook-secret milne par (dashboard → Settings → Webhooks)."""
    raise HTTPException(501, "Webhook processing is not implemented; use verify-payment")


class SSOConfigRequest(BaseModel):
    provider: str
    client_id: str
    client_secret: str = ""
    redirect_uri: str
    issuer: str | None = None
    sso_only: bool = False


@router.post("/sso-config")
async def set_sso_config(payload: SSOConfigRequest, current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    if current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    if payload.client_secret:
        raise HTTPException(409, "SSO credential storage is not implemented; do not submit client secrets")
    if payload.sso_only:
        raise HTTPException(409, "SSO login is not implemented; sso_only cannot be enforced")
    result = await pg_db.execute(select(SSOConfig).where(SSOConfig.org_id == current_user.org_id))
    existing = result.scalar_one_or_none()
    if existing:
        for k, v in payload.model_dump().items(): setattr(existing, k, v)
    else:
        pg_db.add(SSOConfig(id=uuid.uuid4(), org_id=current_user.org_id, **payload.model_dump()))
    await pg_db.commit()
    await write_audit(pg_db, org_id=current_user.org_id, user_id=current_user.id, action="sso_config_update")
    return {"status": "sso_config_saved"}


@router.get("/sso-config")
async def get_sso_config(current_user: User = Depends(get_current_user), pg_db: AsyncSession = Depends(get_pg_db)):
    result = await pg_db.execute(select(SSOConfig).where(SSOConfig.org_id == current_user.org_id))
    cfg = result.scalar_one_or_none()
    if not cfg:
        return {"configured": False}
    return {"configured": True, "provider": cfg.provider, "redirect_uri": cfg.redirect_uri, "sso_only": cfg.sso_only, "client_id": cfg.client_id}