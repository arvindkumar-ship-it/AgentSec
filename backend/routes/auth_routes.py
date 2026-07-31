# from fastapi import APIRouter, HTTPException
# from auth import RegisterRequest, LoginRequest, hash_password, verify_password, create_token
# from core.db import get_db
# from bson import ObjectId

# router = APIRouter(prefix="/auth", tags=["Auth"])

# @router.post("/register")
# async def register(req: RegisterRequest):
#     db = get_db()
    
#     # Check existing user
#     existing = await db.users.find_one({"email": req.email})
#     if existing:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     # Create user
#     user = {
#         "email": req.email,
#         "name": req.name,
#         "password": hash_password(req.password),
#         "created_at": __import__('datetime').datetime.utcnow().isoformat()
#     }
#     result = await db.users.insert_one(user)
#     user_id = str(result.inserted_id)
    
#     token = create_token(user_id, req.email)
#     return {"token": token, "user": {"id": user_id, "email": req.email, "name": req.name}}

# @router.post("/login")
# async def login(req: LoginRequest):
#     db = get_db()
    
#     user = await db.users.find_one({"email": req.email})
#     if not user or not verify_password(req.password, user["password"]):
#         raise HTTPException(status_code=401, detail="Invalid email or password")
    
#     user_id = str(user["_id"])
#     token = create_token(user_id, req.email)
#     return {"token": token, "user": {"id": user_id, "email": user["email"], "name": user["name"]}}

# @router.get("/me")
# async def get_me(credentials = __import__('fastapi').Depends(__import__('auth').get_current_user)):
#     return credentials






# from fastapi import APIRouter, Depends
# from sqlalchemy.ext.asyncio import AsyncSession

# from database import get_db
# from auth import RegisterRequest, LoginRequest, register_user, login_user, get_current_user
# from models.sql_models import User

# router = APIRouter(prefix="/auth", tags=["Auth"])


# @router.post("/register")
# async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
#     return await register_user(payload, db)


# @router.post("/login")
# async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
#     return await login_user(payload, db)


# @router.get("/me")
# async def get_me(current_user: User = Depends(get_current_user)):
#     return {
#         "id": str(current_user.id),
#         "email": current_user.email,
#         "role": current_user.role.value,
#         "org_id": str(current_user.org_id),
#     }


from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from auth import RegisterRequest, LoginRequest, register_user, login_user, get_current_user
from models.sql_models import User
from models.quota_models import OrganizationPlan, Plan

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register")
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    return await register_user(payload, db)


@router.post("/login")
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    return await login_user(payload, db)


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Plan.name)
        .join(OrganizationPlan, OrganizationPlan.plan_id == Plan.id)
        .where(OrganizationPlan.org_id == current_user.org_id, OrganizationPlan.status == "active")
    )
    plan_name = result.scalar_one_or_none() or "free"

    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "role": current_user.role.value,
        "org_id": str(current_user.org_id),
        "plan_name": plan_name,
    }