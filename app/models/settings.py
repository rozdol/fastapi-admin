from sqlalchemy import Column, String, DateTime
from sqlalchemy.sql import func
from app.core.database import SQLiteBase


class Settings(SQLiteBase):
    __tablename__ = "settings"

    setting_name = Column(String, primary_key=True, index=True)
    value = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
