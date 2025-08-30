from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from app.core.config import settings
from app.core.security import verify_password
from app.models.user import User
from app.schemas.auth import UserLogin


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def authenticate_user(self, email_or_username: str, password: str) -> Optional[User]:
        # Try to find user by email first, then by username
        user = self.db.query(User).filter(User.email == email_or_username).first()
        if not user:
            # If not found by email, try username
            user = self.db.query(User).filter(User.username == email_or_username).first()
        
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    def create_access_token(self, data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
        return encoded_jwt

    def create_user(self, user_data: UserLogin) -> Optional[User]:
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            return None
        
        # Create new user (simplified - you might want to add more fields)
        from app.core.security import get_password_hash
        from app.services.user_service import UserService
        from app.schemas.user import UserCreate
        
        user_service = UserService(self.db)
        user_create = UserCreate(
            email=user_data.email,
            username=user_data.email.split('@')[0],  # Simple username generation
            password=user_data.password
        )
        return user_service.create_user(user_create)
