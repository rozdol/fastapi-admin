from typing import List, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.security import get_password_hash
from app.core.email import EmailService


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def get_users(self, skip: int = 0, limit: int = 100, sort: str = None, order: str = "asc") -> List[User]:
        query = self.db.query(User)
        
        if sort:
            column = getattr(User, sort, None)
            if column:
                if order.lower() == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        
        return query.offset(skip).limit(limit).all()

    def get_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == username).first()

    def create_user(self, user: UserCreate) -> User:
        hashed_password = get_password_hash(user.password)
        
        # Generate activation token
        email_service = EmailService()
        activation_token = email_service.generate_activation_token()
        activation_expires = datetime.utcnow() + timedelta(hours=24)
        
        db_user = User(
            email=user.email,
            username=user.username,
            hashed_password=hashed_password,
            full_name=user.full_name,
            is_active=False,  # Users are inactive by default
            activation_token=activation_token,
            activation_token_expires=activation_expires
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Send activation email
        email_service.send_activation_email(user.email, user.username, activation_token)
        
        return db_user

    def get_user_by_activation_token(self, activation_token: str) -> Optional[User]:
        return self.db.query(User).filter(User.activation_token == activation_token).first()

    def activate_user(self, activation_token: str) -> Optional[User]:
        """Activate user account using activation token"""
        user = self.get_user_by_activation_token(activation_token)
        if not user:
            return None
        
        # Check if token is expired
        if user.activation_token_expires and user.activation_token_expires < datetime.utcnow():
            return None
        
        # Activate user
        user.is_active = True
        user.activation_token = None
        user.activation_token_expires = None
        
        self.db.commit()
        self.db.refresh(user)
        
        # Send welcome email
        email_service = EmailService()
        email_service.send_welcome_email(user.email, user.username)
        
        return user

    def update_user(self, user_id: int, user: UserUpdate) -> Optional[User]:
        db_user = self.get_user(user_id)
        if not db_user:
            return None
        
        update_data = user.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def delete_user(self, user_id: int) -> bool:
        db_user = self.get_user(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True
