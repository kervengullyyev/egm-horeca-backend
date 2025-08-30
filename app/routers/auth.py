from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import jwt
from datetime import datetime, timedelta
import os
import hashlib
import secrets

router = APIRouter()

# Simple password hashing (fallback if bcrypt fails)
def hash_password(password: str) -> str:
    """Hash password using SHA-256 with salt"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}${hash_obj.hexdigest()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    try:
        salt, hash_value = hashed_password.split('$')
        hash_obj = hashlib.sha256((plain_password + salt).encode())
        return hash_obj.hexdigest() == hash_value
    except:
        return False

# JWT settings
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class UserSignUp(BaseModel):
    firstName: str
    lastName: str
    email: str
    phone: str
    password: str

class UserSignIn(BaseModel):
    email: str
    password: str

class SSORequest(BaseModel):
    provider: str
    token: str
    email: str
    firstName: Optional[str] = None
    lastName: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    firstName: str
    lastName: str
    email: str
    phone: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    token: Optional[str] = None
    user: Optional[UserResponse] = None

# Mock user database (replace with real database)
users_db = {}

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserSignUp):
    try:
        # Check if user already exists
        if user_data.email in users_db:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Create user ID
        user_id = f"user_{len(users_db) + 1}"
        
        # Hash password
        hashed_password = hash_password(user_data.password)
        
        # Store user
        users_db[user_data.email] = {
            "id": user_id,
            "firstName": user_data.firstName,
            "lastName": user_data.lastName,
            "email": user_data.email,
            "phone": user_data.phone,
            "hashed_password": hashed_password
        }
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email}, expires_delta=access_token_expires
        )
        
        # Return user data (without password)
        user_response = UserResponse(
            id=user_id,
            firstName=user_data.firstName,
            lastName=user_data.lastName,
            email=user_data.email,
            phone=user_data.phone
        )
        
        return AuthResponse(
            success=True,
            message="User created successfully",
            token=access_token,
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signin", response_model=AuthResponse)
async def signin(user_data: UserSignIn):
    try:
        # Check if user exists
        if user_data.email not in users_db:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        user = users_db[user_data.email]
        
        # Verify password
        if not verify_password(user_data.password, user["hashed_password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email}, expires_delta=access_token_expires
        )
        
        # Return user data (without password)
        user_response = UserResponse(
            id=user["id"],
            firstName=user["firstName"],
            lastName=user["lastName"],
            email=user["email"],
            phone=user["phone"]
        )
        
        return AuthResponse(
            success=True,
            message="Login successful",
            token=access_token,
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sso", response_model=AuthResponse)
async def sso_login(sso_data: SSORequest):
    try:
        # For now, we'll create a mock user for SSO
        # In production, you would verify the SSO token with the provider
        
        user_id = f"user_{len(users_db) + 1}"
        
        # Check if user already exists
        if sso_data.email in users_db:
            user = users_db[sso_data.email]
        else:
            # Create new user from SSO data
            user = {
                "id": user_id,
                "firstName": sso_data.firstName or "SSO",
                "lastName": sso_data.lastName or "User",
                "email": sso_data.email,
                "phone": "",
                "hashed_password": ""  # SSO users don't have passwords
            }
            users_db[sso_data.email] = user
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": sso_data.email}, expires_delta=access_token_expires
        )
        
        # Return user data
        user_response = UserResponse(
            id=user["id"],
            firstName=user["firstName"],
            lastName=user["lastName"],
            email=user["email"],
            phone=user["phone"]
        )
        
        return AuthResponse(
            success=True,
            message=f"{sso_data.provider.title()} SSO login successful",
            token=access_token,
            user=user_response
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/signout")
async def signout():
    # In a real implementation, you might want to blacklist the token
    # For now, we'll just return success
    return {"success": True, "message": "Logged out successfully"}

@router.get("/users", response_model=List[UserResponse])
async def get_all_users():
    """Get all registered users (for admin purposes)"""
    try:
        users = []
        for email, user_data in users_db.items():
            users.append(UserResponse(
                id=user_data["id"],
                firstName=user_data["firstName"],
                lastName=user_data["lastName"],
                email=user_data["email"],
                phone=user_data["phone"]
            ))
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
