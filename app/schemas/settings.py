from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class SettingsBase(BaseModel):
    setting_name: str
    value: str


class SettingsCreate(SettingsBase):
    pass


class SettingsUpdate(BaseModel):
    value: str


class Settings(SettingsBase):
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
