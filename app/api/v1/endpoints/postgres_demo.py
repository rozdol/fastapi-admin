from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_sqlite_db, get_postgres_db1, get_postgres_db2
from app.services.postgres_db1_service import (
    create_analytics_event,
    create_user_log,
    get_user_analytics,
    get_user_logs
)
from app.services.postgres_db2_service import (
    create_system_event,
    create_performance_metric,
    get_system_events,
    get_performance_metrics
)
from app.models.user import User
from typing import Optional
from pydantic import BaseModel

router = APIRouter()


class AnalyticsEventCreate(BaseModel):
    user_id: int
    event_type: str
    event_data: Optional[dict] = None


class UserLogCreate(BaseModel):
    user_id: int
    action: str
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None


class SystemEventCreate(BaseModel):
    event_type: str
    severity: str
    message: str
    event_metadata: Optional[dict] = None


class PerformanceMetricCreate(BaseModel):
    metric_name: str
    metric_value: float
    unit: Optional[str] = None
    tags: Optional[dict] = None


@router.post("/analytics")
async def create_analytics(
    analytics: AnalyticsEventCreate,
    sqlite_db: Session = Depends(get_sqlite_db),
    postgres_db1: Session = Depends(get_postgres_db1)
):
    """Create analytics event - demonstrates cross-database operation"""
    # First, verify user exists in SQLite database
    user = sqlite_db.query(User).filter(User.id == analytics.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Then create analytics event in PostgreSQL Database 1
    analytics_event = await create_analytics_event(
        user_id=analytics.user_id,
        event_type=analytics.event_type,
        event_data=analytics.event_data,
        db=postgres_db1
    )
    
    return {"message": "Analytics event created", "event_id": analytics_event.id}


@router.post("/user-log")
async def create_user_log_entry(
    user_log: UserLogCreate,
    sqlite_db: Session = Depends(get_sqlite_db),
    postgres_db1: Session = Depends(get_postgres_db1)
):
    """Create user log entry - demonstrates cross-database operation"""
    # Verify user exists in SQLite database
    user = sqlite_db.query(User).filter(User.id == user_log.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create log entry in PostgreSQL Database 1
    log_entry = await create_user_log(
        user_id=user_log.user_id,
        action=user_log.action,
        ip_address=user_log.ip_address,
        user_agent=user_log.user_agent,
        db=postgres_db1
    )
    
    return {"message": "User log created", "log_id": log_entry.id}


@router.post("/system-event")
async def create_system_event_entry(
    system_event: SystemEventCreate,
    postgres_db2: Session = Depends(get_postgres_db2)
):
    """Create system event in PostgreSQL Database 2"""
    event = await create_system_event(
        event_type=system_event.event_type,
        severity=system_event.severity,
        message=system_event.message,
        event_metadata=system_event.event_metadata,
        db=postgres_db2
    )
    
    return {"message": "System event created", "event_id": event.id}


@router.post("/performance-metric")
async def create_performance_metric_entry(
    metric: PerformanceMetricCreate,
    postgres_db2: Session = Depends(get_postgres_db2)
):
    """Create performance metric in PostgreSQL Database 2"""
    performance_metric = await create_performance_metric(
        metric_name=metric.metric_name,
        metric_value=metric.metric_value,
        unit=metric.unit,
        tags=metric.tags,
        db=postgres_db2
    )
    
    return {"message": "Performance metric created", "metric_id": performance_metric.id}


@router.get("/analytics")
async def get_analytics_events(
    user_id: Optional[int] = None,
    event_type: Optional[str] = None,
    limit: int = 100,
    postgres_db1: Session = Depends(get_postgres_db1)
):
    """Get analytics events from PostgreSQL Database 1"""
    events = await get_user_analytics(
        user_id=user_id,
        event_type=event_type,
        limit=limit,
        db=postgres_db1
    )
    return events


@router.get("/user-logs")
async def get_user_log_entries(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    limit: int = 100,
    postgres_db1: Session = Depends(get_postgres_db1)
):
    """Get user logs from PostgreSQL Database 1"""
    logs = await get_user_logs(
        user_id=user_id,
        action=action,
        limit=limit,
        db=postgres_db1
    )
    return logs


@router.get("/system-events")
async def get_system_event_entries(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    postgres_db2: Session = Depends(get_postgres_db2)
):
    """Get system events from PostgreSQL Database 2"""
    events = await get_system_events(
        event_type=event_type,
        severity=severity,
        limit=limit,
        db=postgres_db2
    )
    return events


@router.get("/performance-metrics")
async def get_performance_metric_entries(
    metric_name: Optional[str] = None,
    limit: int = 100,
    postgres_db2: Session = Depends(get_postgres_db2)
):
    """Get performance metrics from PostgreSQL Database 2"""
    metrics = await get_performance_metrics(
        metric_name=metric_name,
        limit=limit,
        db=postgres_db2
    )
    return metrics
