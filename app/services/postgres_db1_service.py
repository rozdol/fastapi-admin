from sqlalchemy.orm import Session
from app.models.postgres_db1 import Analytics, UserLog
from app.core.database import get_postgres_db1
from typing import Optional, Dict, Any, List


async def create_analytics_event(
    user_id: int,
    event_type: str,
    event_data: Optional[Dict[str, Any]] = None,
    db: Session = None
) -> Analytics:
    """Create analytics event in PostgreSQL Database 1"""
    if db is None:
        db = next(get_postgres_db1())
    
    analytics = Analytics(
        user_id=user_id,
        event_type=event_type,
        event_data=event_data
    )
    
    db.add(analytics)
    db.commit()
    db.refresh(analytics)
    return analytics


async def create_user_log(
    user_id: int,
    action: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    db: Session = None
) -> UserLog:
    """Create user log entry in PostgreSQL Database 1"""
    if db is None:
        db = next(get_postgres_db1())
    
    user_log = UserLog(
        user_id=user_id,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    db.add(user_log)
    db.commit()
    db.refresh(user_log)
    return user_log


async def get_user_analytics(
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    db: Session = None
) -> List[Analytics]:
    """Get analytics events from PostgreSQL Database 1"""
    if db is None:
        db = next(get_postgres_db1())
    
    query = db.query(Analytics)
    if user_id:
        query = query.filter(Analytics.user_id == user_id)
    if event_type:
        query = query.filter(Analytics.event_type == event_type)
    
    return query.order_by(Analytics.timestamp.desc()).limit(limit).all()


async def get_user_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = 100,
    db: Session = None
) -> List[UserLog]:
    """Get user logs from PostgreSQL Database 1"""
    if db is None:
        db = next(get_postgres_db1())
    
    query = db.query(UserLog)
    if user_id:
        query = query.filter(UserLog.user_id == user_id)
    if action:
        query = query.filter(UserLog.action == action)
    
    return query.order_by(UserLog.created_at.desc()).limit(limit).all()
