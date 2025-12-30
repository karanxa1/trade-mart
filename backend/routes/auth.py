# Authentication Routes
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
import uuid
from datetime import datetime, timedelta
from jose import jwt

from ..config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, firebase_auth
from ..models.user import UserModel

from ..models.user import UserModel
import logging

router = APIRouter(prefix="/api/auth", tags=["auth"])
logger = logging.getLogger(__name__)

class LoginRequest(BaseModel):
    email: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    phone: Optional[str] = ""
    address: Optional[str] = ""
    user_type: str = "buyer"

class GoogleLoginRequest(BaseModel):
    id_token: str
    user_type: str = "buyer"

class VerifyRequest(BaseModel):
    user_id: str
    verification_code: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/login")
async def login(request: LoginRequest):
    user = UserModel.get_by_email(request.email)
    if not user:
        user = UserModel.get_by_username(request.email)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email/username or password")
    
    stored_hash = user.get('password_hash')
    if not stored_hash or not UserModel.verify_password(request.password, stored_hash):
        logger.warning(f"Failed login attempt for email: {request.email}")
        raise HTTPException(status_code=401, detail="Invalid email/username or password")
    
    logger.info(f"User logged in: {user.get('username')} ({user.get('id')})")
    token = create_access_token({
        "sub": user['id'],
        "username": user.get('username'),
        "user_type": user.get('user_type')
    })
    
    return TokenResponse(
        access_token=token,
        user={
            "id": user['id'],
            "username": user.get('username'),
            "email": user.get('email'),
            "user_type": user.get('user_type'),
            "is_verified": user.get('is_verified', False),
            "identity_verified": user.get('identity_verified', False)
        }
    )

@router.post("/register")
async def register(request: RegisterRequest):
    if UserModel.get_by_username(request.username):
        raise HTTPException(status_code=400, detail="Username already exists")
    
    if UserModel.get_by_email(request.email):
        raise HTTPException(status_code=400, detail="Email already exists")
    
    try:
        try:
            firebase_user = firebase_auth.create_user(
                email=request.email,
                password=request.password,
                display_name=request.username
            )
            uid = firebase_user.uid
        except Exception:
            uid = str(uuid.uuid4())
        
        password_hash = UserModel.hash_password(request.password)
        user = UserModel.create_user(
            uid=uid,
            username=request.username,
            email=request.email,
            phone=request.phone,
            address=request.address,
            user_type=request.user_type,
            password_hash=password_hash
        )
        
        token = create_access_token({
            "sub": uid,
            "username": request.username,
            "user_type": request.user_type
        })
        
        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": uid,
                "username": request.username,
                "email": request.email,
                "user_type": request.user_type,
                "is_verified": False,
                "verification_code": user.get('verification_code')
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/google-login")
async def google_login(request: GoogleLoginRequest):
    try:
        decoded_token = firebase_auth.verify_id_token(request.id_token)
        uid = decoded_token['uid']
        email = decoded_token.get('email', '')
        name = decoded_token.get('name', email.split('@')[0] if email else 'User')
        
        user = UserModel.get_by_id(uid)
        
        if not user:
            user = UserModel.get_by_email(email)
            if user:
                uid = user['id']
            else:
                user = UserModel.create_user(
                    uid=uid,
                    username=name.replace(' ', '_').lower(),
                    email=email,
                    phone='',
                    address='',
                    user_type=request.user_type,
                    password_hash=''
                )
                UserModel.update(uid, {'is_verified': True})
                user['id'] = uid
                user['is_verified'] = True
        
        token = create_access_token({
            "sub": user.get('id', uid),
            "username": user.get('username', name),
            "user_type": user.get('user_type', request.user_type)
        })
        
        return {
            "success": True,
            "access_token": token,
            "token_type": "bearer",
            "user": {
                "id": user.get('id', uid),
                "username": user.get('username', name),
                "email": user.get('email', email),
                "user_type": user.get('user_type', request.user_type),
                "is_verified": user.get('is_verified', True)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/verify")
async def verify_account(request: VerifyRequest):
    user = UserModel.get_by_id(request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.get('is_verified'):
        return {"success": True, "message": "Account already verified"}
    
    if request.verification_code == user.get('verification_code'):
        UserModel.update(request.user_id, {'is_verified': True})
        return {"success": True, "message": "Account verified successfully"}
    else:
        raise HTTPException(status_code=400, detail="Invalid verification code")

@router.get("/user/{user_id}")
async def get_user(user_id: str):
    user = UserModel.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user['id'],
        "username": user.get('username'),
        "email": user.get('email'),
        "user_type": user.get('user_type'),
        "is_verified": user.get('is_verified', False),
        "identity_verified": user.get('identity_verified', False),
        "avg_rating": user.get('avg_rating', 0),
        "total_ratings": user.get('total_ratings', 0)
    }
