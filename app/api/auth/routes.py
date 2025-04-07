from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import timedelta
from typing import Annotated
import uuid
from datetime import datetime

from .models import UserCreate, UserLogin, UserResponse, Token
from .security import (
    verify_password, 
    get_password_hash, 
    create_access_token, 
    decode_token,
    ACCESS_TOKEN_EXPIRE_DAYS
)

# This would be replaced with a database in production
# For now, we'll use an in-memory store for demonstration
USERS_DB = {}

router = APIRouter(prefix="/api/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """Get the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None or user_id not in USERS_DB:
        raise credentials_exception
    
    return USERS_DB[user_id]


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new user."""
    # Check if email already exists
    for existing_user in USERS_DB.values():
        if existing_user["email"] == user.email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
    
    # Create new user
    user_id = str(uuid.uuid4())
    created_at = datetime.utcnow().isoformat()
    
    USERS_DB[user_id] = {
        "id": user_id,
        "email": user.email,
        "hashed_password": get_password_hash(user.password),
        "created_at": created_at
    }
    
    return {
        "id": user_id,
        "email": user.email,
        "created_at": created_at
    }


@router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login a user and return an access token."""
    user = None
    
    # Find user by email
    for u in USERS_DB.values():
        if u["email"] == form_data.username:  # OAuth2 form uses 'username' field for email
            user = u
            break
    
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    access_token = create_access_token(
        data={"sub": user["id"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout():
    """Logout a user (client-side only in this implementation)."""
    # In a JWT-based auth system, logout is typically handled client-side
    # by removing the token from storage
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: Annotated[dict, Depends(get_current_user)]):
    """Get information about the currently logged in user."""
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "created_at": current_user["created_at"]
    }
