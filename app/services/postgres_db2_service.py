from sqlalchemy.orm import Session
from app.models.postgres_db2 import SystemEvent, PerformanceMetric
from app.core.database import get_postgres_db2
from typing import Optional, Dict, Any, List


async def create_system_event(
    event_type: str,
    severity: str,
    message: str,
    event_metadata: Optional[Dict[str, Any]] = None,
    db: Session = None
) -> SystemEvent:
    """Create system event in PostgreSQL Database 2"""
    if db is None:
        db = next(get_postgres_db2())
    
    system_event = SystemEvent(
        event_type=event_type,
        severity=severity,
        message=message,
        event_metadata=event_metadata
    )
    
    db.add(system_event)
    db.commit()
    db.refresh(system_event)
    return system_event


async def create_performance_metric(
    metric_name: str,
    metric_value: float,
    unit: Optional[str] = None,
    tags: Optional[Dict[str, Any]] = None,
    db: Session = None
) -> PerformanceMetric:
    """Create performance metric in PostgreSQL Database 2"""
    if db is None:
        db = next(get_postgres_db2())
    
    performance_metric = PerformanceMetric(
        metric_name=metric_name,
        metric_value=metric_value,
        unit=unit,
        tags=tags
    )
    
    db.add(performance_metric)
    db.commit()
    db.refresh(performance_metric)
    return performance_metric


async def get_system_events(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    limit: int = 100,
    db: Session = None
) -> List[SystemEvent]:
    """Get system events from PostgreSQL Database 2"""
    if db is None:
        db = next(get_postgres_db2())
    
    query = db.query(SystemEvent)
    if event_type:
        query = query.filter(SystemEvent.event_type == event_type)
    if severity:
        query = query.filter(SystemEvent.severity == severity)
    
    return query.order_by(SystemEvent.created_at.desc()).limit(limit).all()


async def get_performance_metrics(
    metric_name: Optional[str] = None,
    limit: int = 100,
    db: Session = None
) -> List[PerformanceMetric]:
    """Get performance metrics from PostgreSQL Database 2"""
    if db is None:
        db = next(get_postgres_db2())
    
    query = db.query(PerformanceMetric)
    if metric_name:
        query = query.filter(PerformanceMetric.metric_name == metric_name)
    
    return query.order_by(PerformanceMetric.recorded_at.desc()).limit(limit).all()
