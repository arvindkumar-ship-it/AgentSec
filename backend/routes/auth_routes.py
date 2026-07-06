from fastapi import APIRouter, HTTPException
from auth import RegisterRequest, LoginRequest, hash_password, verify_password, create_token
from core.db import get_db
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
async def register(req: RegisterRequest):
    db = get_db()
    
    # Check existing user
    existing = await db.users.find_one({"email": req.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    user = {
        "email": req.email,
        "name": req.name,
        "password": hash_password(req.password),
        "created_at": __import__('datetime').datetime.utcnow().isoformat()
    }
    result = await db.users.insert_one(user)
    user_id = str(result.inserted_id)
    
    token = create_token(user_id, req.email)
    return {"token": token, "user": {"id": user_id, "email": req.email, "name": req.name}}

@router.post("/login")
async def login(req: LoginRequest):
    db = get_db()
    
    user = await db.users.find_one({"email": req.email})
    if not user or not verify_password(req.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    user_id = str(user["_id"])
    token = create_token(user_id, req.email)
    return {"token": token, "user": {"id": user_id, "email": user["email"], "name": user["name"]}}

@router.get("/me")
async def get_me(credentials = __import__('fastapi').Depends(__import__('auth').get_current_user)):
    return credentials