# from datetime import datetime, timedelta
# from fastapi import HTTPException, Depends
# from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
# from pydantic import BaseModel, EmailStr
# import jwt
# import bcrypt
# from core.db import get_db
# from config import settings

# security = HTTPBearer()

# class RegisterRequest(BaseModel):
#     email: str
#     password: str
#     name: str

# class LoginRequest(BaseModel):
#     email: str
#     password: str

# def hash_password(password: str) -> str:
#     return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

# def verify_password(password: str, hashed: str) -> bool:
#     return bcrypt.checkpw(password.encode(), hashed.encode())

# def create_token(user_id: str, email: str) -> str:
#     payload = {
#         "user_id": user_id,
#         "email": email,
#         "exp": datetime.utcnow() + timedelta(days=30)
#     }
#     return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

# async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
#     token = credentials.credentials
#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
#         return payload
#     except jwt.ExpiredSignatureError:
#         raise HTTPException(status_code=401, detail="Token expired")
#     except jwt.InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")







import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import jwt
import bcrypt

from database import get_db
from models.sql_models import User, Organization
from config import settings

security = HTTPBearer()


# ---------- Request schemas ----------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str          # user ka naam
    org_name: str       # organization ka naam


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ---------- Password helpers ----------

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


# ---------- Token helpers ----------

def create_token(user_id: str, email: str, org_id: str, role: str) -> str:
    payload = {
        "user_id": user_id,
        "email": email,
        "org_id": org_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(days=30),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    return user


# ---------- Core auth logic (register / login) ----------

async def register_user(payload: RegisterRequest, db: AsyncSession) -> dict:
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    org = Organization(id=uuid.uuid4(), name=payload.org_name)
    db.add(org)
    await db.flush()  # org.id ready ho jaye commit se pehle

    user = User(
        id=uuid.uuid4(),
        email=payload.email,
        hashed_password=hash_password(payload.password),
        org_id=org.id,
        role="admin",  # signup karne wala apne org ka pehla admin
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(str(user.id), user.email, str(user.org_id), user.role.value)
    return {"access_token": token, "token_type": "bearer"}


async def login_user(payload: LoginRequest, db: AsyncSession) -> dict:
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")

    token = create_token(str(user.id), user.email, str(user.org_id), user.role.value)
    return {"access_token": token, "token_type": "bearer"}