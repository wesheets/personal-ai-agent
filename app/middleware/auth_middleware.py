from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from typing import Annotated

from app.api.auth.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def require_auth(token: Annotated[str, Depends(oauth2_scheme)]):
    """Middleware to require authentication for protected routes."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": "Unauthorized"},
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    return user_id


# Usage example:
# @router.get("/protected-route")
# async def protected_route(current_user_id: Annotated[str, Depends(require_auth)]):
#     return {"message": "This is a protected route", "user_id": current_user_id}
