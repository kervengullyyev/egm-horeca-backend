from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
import jwt
from datetime import datetime, timedelta, timezone
import os
import secrets
import logging
from sqlalchemy.orm import Session
from app import crud, database
from app.utils import hash_password, verify_password
from app.schemas import ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse
from app.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter()

# Database dependency
def get_db():
    SessionLocal = database.get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



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



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



@router.post("/signup", response_model=AuthResponse)
async def signup(user_data: UserSignUp, db: Session = Depends(get_db)):
    try:
        # Check if user already exists in database
        existing_user = crud.get_user_by_email(db, email=user_data.email)
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")
        
        # Check if username already exists
        existing_username = crud.get_user_by_username(db, username=user_data.email.split('@')[0])  # Use email prefix as username
        if existing_username:
            raise HTTPException(status_code=400, detail="Username already taken")
        
        # Create user in database
        from app.schemas import UserCreate
        db_user_data = UserCreate(
            email=user_data.email,
            username=user_data.email.split('@')[0],  # Use email prefix as username
            full_name=f"{user_data.firstName} {user_data.lastName}",
            phone=user_data.phone,
            role="customer",
            password=user_data.password
        )
        
        db_user = crud.create_user(db, db_user_data)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email}, expires_delta=access_token_expires
        )
        
        # Return user data (without password)
        user_response = UserResponse(
            id=str(db_user.id),
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
async def signin(user_data: UserSignIn, db: Session = Depends(get_db)):
    try:
        # Check if user exists in database
        db_user = crud.get_user_by_email(db, email=user_data.email)
        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Verify password (using the hashed password from database)
        if not verify_password(user_data.password, db_user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.email}, expires_delta=access_token_expires
        )
        
        # Return user data (without password)
        user_response = UserResponse(
            id=str(db_user.id),
            firstName=db_user.full_name.split()[0] if db_user.full_name else "",
            lastName=" ".join(db_user.full_name.split()[1:]) if db_user.full_name and len(db_user.full_name.split()) > 1 else "",
            email=db_user.email,
            phone=db_user.phone or ""
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
async def sso_login(sso_data: SSORequest, db: Session = Depends(get_db)):
    try:
        # Check if user already exists in database
        existing_user = crud.get_user_by_email(db, email=sso_data.email)
        
        if existing_user:
            # User exists, just log them in
            db_user = existing_user
        else:
            # Create new user from SSO data in database
            from app.schemas import UserCreate
            db_user_data = UserCreate(
                email=sso_data.email,
                username=sso_data.email.split('@')[0],  # Use email prefix as username
                full_name=f"{sso_data.firstName or 'SSO'} {sso_data.lastName or 'User'}",
                phone="",
                role="customer",
                is_active=True,
                password="sso_user_no_password"  # Dummy password for SSO users
            )
            
            db_user = crud.create_user(db, db_user_data)
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": sso_data.email}, expires_delta=access_token_expires
        )
        
        # Return user data
        user_response = UserResponse(
            id=str(db_user.id),
            firstName=db_user.full_name.split()[0] if db_user.full_name else "",
            lastName=" ".join(db_user.full_name.split()[1:]) if db_user.full_name and len(db_user.full_name.split()) > 1 else "",
            email=db_user.email,
            phone=db_user.phone or ""
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
async def get_all_users(db: Session = Depends(get_db)):
    """Get all registered users (for admin purposes)"""
    try:
        db_users = crud.get_users(db, skip=0, limit=1000, active_only=False)
        users = []
        for db_user in db_users:
            # Split full_name into firstName and lastName
            name_parts = db_user.full_name.split() if db_user.full_name else ["", ""]
            firstName = name_parts[0] if name_parts else ""
            lastName = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""
            
            users.append(UserResponse(
                id=str(db_user.id),
                firstName=firstName,
                lastName=lastName,
                email=db_user.email,
                phone=db_user.phone or ""
            ))
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/forgot-password", response_model=PasswordResetResponse)
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset email to user"""
    try:
        # Check if user exists
        db_user = crud.get_user_by_email(db, email=request.email)
        if not db_user:
            # Return success even if user doesn't exist for security reasons
            return PasswordResetResponse(
                success=True,
                message="If an account with that email exists, a password reset link has been sent."
            )
        
        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Set token expiration (1 hour from now)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=1)
        
        # Save reset token to database
        crud.set_password_reset_token(db, db_user.id, reset_token, expires_at)
        
        # Send reset email
        user_name = db_user.full_name.split()[0] if db_user.full_name else None
        email_sent = await email_service.send_password_reset_email(
            email=db_user.email,
            reset_token=reset_token,
            user_name=user_name
        )
        
        if not email_sent:
            # Log the error but don't fail the request
            logger.error(f"Failed to send password reset email to {db_user.email}")
            # Still return success to prevent email enumeration
            return PasswordResetResponse(
                success=True,
                message="If an account with that email exists, a password reset link has been sent."
            )
        
        return PasswordResetResponse(
            success=True,
            message="If an account with that email exists, a password reset link has been sent."
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/reset-password", response_model=PasswordResetResponse)
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset user password using reset token"""
    try:
        # Find user by reset token
        db_user = crud.get_user_by_reset_token(db, request.token)
        if not db_user:
            raise HTTPException(status_code=400, detail="Invalid or expired reset token")
        
        # Check if token is expired
        if db_user.reset_token_expires and datetime.now(timezone.utc) > db_user.reset_token_expires:
            # Clear expired token
            crud.clear_password_reset_token(db, db_user.id)
            raise HTTPException(status_code=400, detail="Reset token has expired")
        
        # Update password
        crud.update_user_password(db, db_user.id, request.new_password)
        
        # Send confirmation email
        user_name = db_user.full_name.split()[0] if db_user.full_name else None
        await email_service.send_password_reset_confirmation(
            email=db_user.email,
            user_name=user_name
        )
        
        return PasswordResetResponse(
            success=True,
            message="Password has been reset successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
