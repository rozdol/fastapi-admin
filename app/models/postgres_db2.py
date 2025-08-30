from sqlalchemy import Column, Integer, String, DateTime, JSON, Text, Float
from sqlalchemy.sql import func
from app.core.database import PostgresDB2Base


class SystemEvent(PostgresDB2Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, nullable=False)
    severity = Column(String, nullable=False)  # INFO, WARNING, ERROR, CRITICAL
    message = Column(Text, nullable=False)
    event_metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PerformanceMetric(PostgresDB2Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String, nullable=True)
    tags = Column(JSON, nullable=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now())

