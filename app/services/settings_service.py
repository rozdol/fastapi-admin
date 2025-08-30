from sqlalchemy.orm import Session
from app.models.settings import Settings
from app.schemas.settings import SettingsCreate, SettingsUpdate
from typing import List, Optional


class SettingsService:
    def __init__(self, db: Session):
        self.db = db

    def get_settings(self, sort: str = None, order: str = "asc") -> List[Settings]:
        """Get all settings with optional sorting"""
        query = self.db.query(Settings)
        
        if sort:
            column = getattr(Settings, sort, None)
            if column:
                if order.lower() == "desc":
                    query = query.order_by(column.desc())
                else:
                    query = query.order_by(column.asc())
        
        return query.all()

    def get_setting(self, setting_name: str) -> Optional[Settings]:
        """Get a specific setting by name"""
        return self.db.query(Settings).filter(Settings.setting_name == setting_name).first()

    def create_setting(self, setting: SettingsCreate) -> Settings:
        """Create a new setting"""
        db_setting = Settings(
            setting_name=setting.setting_name,
            value=setting.value
        )
        self.db.add(db_setting)
        self.db.commit()
        self.db.refresh(db_setting)
        return db_setting

    def update_setting(self, setting_name: str, setting: SettingsUpdate) -> Optional[Settings]:
        """Update an existing setting"""
        db_setting = self.get_setting(setting_name)
        if not db_setting:
            return None
        
        db_setting.value = setting.value
        self.db.commit()
        self.db.refresh(db_setting)
        return db_setting

    def delete_setting(self, setting_name: str) -> bool:
        """Delete a setting"""
        db_setting = self.get_setting(setting_name)
        if not db_setting:
            return False
        
        self.db.delete(db_setting)
        self.db.commit()
        return True
