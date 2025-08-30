from typing import Optional
from fastapi import Request, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.config import settings
from app.core.database import get_db
from app.services.user_service import UserService


def get_current_user(request: Request) -> Optional[dict]:
    """Get current user from session or JWT token"""
    # Check session first
    user = request.session.get("user")
    if user:
        return user
    
    # Check JWT token
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            email = payload.get("sub")
            if email:
                db = next(get_db())
                user_service = UserService(db)
                user = user_service.get_user_by_email(email)
                if user:
                    return {
                        "id": user.id,
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name,
                        "is_active": user.is_active,
                        "is_superuser": user.is_superuser
                    }
        except JWTError:
            pass
    
    return None


def require_auth(request: Request) -> dict:
    """Require authentication - redirect to login if not authenticated"""
    user = get_current_user(request)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER,
            detail="Not authenticated",
            headers={"Location": "/login"}
        )
    return user


def require_admin(request: Request) -> dict:
    """Require admin authentication"""
    user = require_auth(request)
    if not user.get("is_superuser"):
        from app.core.exceptions import AdminAccessDeniedException
        raise AdminAccessDeniedException()
    return user
