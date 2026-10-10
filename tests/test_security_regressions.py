import asyncio
import base64
import json
import socket
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock

import httpx
import pytest
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from agents import verifier
from agents.report_generator import generate_scan_report
from agentsec_client import AgentShieldClient
from auth import require_platform_admin
from config import settings
from core.http_safety import AsyncClient, TargetPolicyError
from core.request_templates import render_payload
from layers import eval_layer, shield
from layers.scan import check_source_code, run_attack_on_endpoint
from models.sql_models import Organization, User, RoleEnum
from models.quota_models import OrganizationUsageDaily
from database import Base
from services.agent_access import ensure_agent_access
from services.quota_service import _reserve_work
from routes.billing_routes import change_plan, PlanChangeRequest


@pytest.fixture
async def db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
    async with async_sessionmaker(engine, expire_on_commit=False)() as session:
        yield session
    await engine.dispose()


async def add_user(db, email):
    org = Organization(id=uuid.uuid4(), name=email, state="active")
    user = User(id=uuid.uuid4(), org_id=org.id, email=email, hashed_password="unused", role=RoleEnum.admin)
    db.add_all([org, user])
    await db.commit()
    return user


def empty_mongo():
    collection = lambda: SimpleNamespace(find=lambda *a, **kw: SimpleNamespace(to_list=AsyncMock(return_value=[])), find_one=AsyncMock(return_value=None))
    return SimpleNamespace(scan_reports=collection(), shield_logs=collection(), checkpoints=collection(), eval_results=collection())


@pytest.mark.parametrize("value", ["false", "true", 0, 1, None])
async def test_judge_rejects_non_boolean(monkeypatch, value):
    async def llm(*a, **kw):
        return json.dumps({"success": value, "confidence": 80, "reason": "fixture"})
    monkeypatch.setattr(verifier, "call_llm", llm)
    assert await verifier._llm_judge_pass("x", "x", "prompt_injection", 0) is None


@pytest.mark.parametrize("decision", [{"safe": "false", "action": "ALLOW"}, {"safe": False, "action": "ALLOW"}, {}, []])
async def test_outbound_malformed_decision_blocks(monkeypatch, decision):
    async def llm(*a, **kw):
        return json.dumps(decision)
    monkeypatch.setattr(verifier, "call_llm", llm)
    result = await verifier.check_response_safety("fixture response")
    assert result["safe"] is False and result["action"] == "BLOCK"


@pytest.mark.parametrize("payload", ["rm -rf /tmp/fixture", "r\u200bm -rf /tmp/fixture", base64.b64encode(b"rm -rf /tmp/fixture").decode(), "rm%20-rf%20/tmp/fixture"])
async def test_shield_checks_full_argument_before_execution(monkeypatch, payload):
    monkeypatch.setattr(shield, "get_db", lambda: None)
    control = shield.AgentShield("fixture")
    effect = AsyncMock()
    wrapped = control.protect(effect)
    with pytest.raises(shield.SecurityException):
        await wrapped({"nested": "harmless " * 300 + payload})
    effect.assert_not_awaited()


async def test_shield_enforces_iteration_budget(monkeypatch):
    monkeypatch.setattr(shield, "get_db", lambda: None)
    control = shield.AgentShield("fixture", {"max_iterations": 1})
    async def tool():
        return "ok"
    protected = control.protect(tool)
    assert await protected() == "ok"
    with pytest.raises(shield.SecurityException):
        await protected()


def test_sdk_sends_auth_and_blocks_http_errors(monkeypatch):
    seen = []
    def send(method, url, **kwargs):
        seen.append(kwargs)
        return httpx.Response(401, json={"detail": "unauthorized"}, request=httpx.Request(method, url))
    monkeypatch.setattr(httpx, "request", send)
    result = AgentShieldClient("fixture", access_token="fixture-token").check_outbound("raw output")
    assert seen[0]["headers"] == {"Authorization": "Bearer fixture-token"}
    assert result["safe"] is False and result["action"] == "BLOCK"
    assert result["response"] != "raw output"


async def test_registered_unscanned_agent_cannot_be_claimed(db):
    first = await add_user(db, "first@example.com")
    second = await add_user(db, "second@example.com")
    mongo = empty_mongo()
    await ensure_agent_access(db, mongo, "unique-agent", first, create=True)
    with pytest.raises(HTTPException) as error:
        await ensure_agent_access(db, mongo, "unique-agent", second, create=True)
    assert error.value.status_code == 403


async def test_unknown_agent_read_does_not_grant_ownership(db):
    user = await add_user(db, "first@example.com")
    with pytest.raises(HTTPException) as error:
        await ensure_agent_access(db, empty_mongo(), "unknown", user)
    assert error.value.status_code == 404


def test_tenant_admin_is_not_platform_admin(monkeypatch):
    monkeypatch.setattr(settings, "PLATFORM_ADMIN_EMAILS", "operator@example.com")
    with pytest.raises(HTTPException):
        require_platform_admin(SimpleNamespace(role="admin", email="tenant@example.com"))
    require_platform_admin(SimpleNamespace(role="admin", email="operator@example.com"))


async def test_paid_plan_cannot_be_granted_by_direct_api():
    user = SimpleNamespace(role=SimpleNamespace(value="admin"))
    with pytest.raises(HTTPException) as error:
        await change_plan(PlanChangeRequest(plan_name="enterprise"), user, None)
    assert error.value.status_code == 403


async def test_unjudged_and_static_only_do_not_get_score():
    for rows in ([], [{"verdict": {"success": False, "needs_review": True}, "severity": "HIGH"}]):
        result = await generate_scan_report("fixture", {}, [], rows)
        assert result["security_score"] is None
        assert result["statistics"]["failed_attacks"] == 0
        assert result["risk_level"] == "UNKNOWN"


def test_import_aliases_and_comments():
    names = {row["name"] for row in check_source_code("import os as operating\nfrom subprocess import run as launch\noperating.system('fixture')\nlaunch(['fixture'])\n# eval('not a call')")}
    assert "os.system" in names and "subprocess.run" in names and "eval" not in names


def test_payload_template_preserves_quotes_and_replaces_nested_values():
    template = {"messages": [{"content": "{{PAYLOAD}}"}], "stream": False}
    payload = 'different "payload"\nline'
    assert render_payload(template, payload)["messages"][0]["content"] == payload
    assert template["messages"][0]["content"] == "{{PAYLOAD}}"
    with pytest.raises(ValueError):
        render_payload({"prompt": "neutral only"}, payload)


@pytest.mark.parametrize("ip", ["127.0.0.1", "10.0.0.1", "169.254.169.254", "::1"])
async def test_scanner_rejects_non_public_addresses(monkeypatch, ip):
    monkeypatch.setenv("SCAN_ALLOWED_ORIGINS", "https://fixture.example")
    async def resolve(*a, **kw):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", (ip, 443))]
    monkeypatch.setattr(asyncio.get_running_loop(), "getaddrinfo", resolve)
    async with AsyncClient(transport=httpx.MockTransport(lambda r: httpx.Response(200))) as client:
        with pytest.raises(TargetPolicyError):
            await client.get("https://fixture.example/path")


async def test_scanner_pins_validated_ip_and_preserves_tls_identity(monkeypatch):
    monkeypatch.setenv("SCAN_ALLOWED_ORIGINS", "https://fixture.example")
    async def resolve(*a, **kw):
        return [(socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443))]
    monkeypatch.setattr(asyncio.get_running_loop(), "getaddrinfo", resolve)
    def receive(request):
        assert request.url.host == "8.8.8.8"
        assert request.headers["host"] == "fixture.example"
        assert request.extensions["sni_hostname"] == "fixture.example"
        return httpx.Response(200, json={"ok": True})
    async with AsyncClient(transport=httpx.MockTransport(receive)) as client:
        assert (await client.get("https://fixture.example/path")).status_code == 200


async def test_daily_and_active_reservations_release_once(db):
    user = await add_user(db, "quota@example.com")
    first = await _reserve_work(db, user.org_id, "scans_count", "max_scans_per_day")
    second = await _reserve_work(db, user.org_id, "scans_count", "max_scans_per_day")
    with pytest.raises(HTTPException) as error:
        await _reserve_work(db, user.org_id, "scans_count", "max_scans_per_day")
    assert error.value.status_code == 429
    second.complete()
    await second.close()
    await first.close()
    await first.close()
    db.expire_all()
    usage = (await db.execute(select(OrganizationUsageDaily))).scalar_one()
    assert usage.scans_count == 1


@pytest.mark.parametrize("case", ["foreign", "replay"])
async def test_payment_rejects_foreign_and_replayed_server_orders(db, case):
    import datetime
    from models.billing_models import BillingOrder
    from routes.billing_routes import verify_payment, VerifyPaymentRequest
    user = await add_user(db, "payer@example.test")
    other = await add_user(db, "other@example.test")
    db.add(BillingOrder(id="order_fixture", org_id=other.org_id if case == "foreign" else user.org_id,
                        plan_name="pro", amount=99900, currency="INR",
                        paid_at=datetime.datetime.now() if case == "replay" else None))
    await db.commit()
    payload = VerifyPaymentRequest(razorpay_order_id="order_fixture", razorpay_payment_id="payment_fixture",
                                   razorpay_signature="invalid", plan_name="pro")
    with pytest.raises(HTTPException) as exc:
        await verify_payment(payload, user, db)
    assert exc.value.status_code == (400 if case == "foreign" else 409)
