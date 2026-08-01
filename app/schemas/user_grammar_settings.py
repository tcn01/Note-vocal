from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


# =============================================
# Schema cho user_grammar_settings
# Dùng để quản lý trạng thái học ngữ pháp
# cá nhân hoá cho từng user.
# =============================================


class UserGrammarSettingsBase(BaseModel):
    """Cài đặt lộ trình học ngữ pháp của user"""
    start_level: str = "A1"
    current_order: int = 1
    daily_limit: int = 1
    last_study_date: Optional[date] = None
    lessons_today: int = 0


class UserGrammarSettingsCreate(UserGrammarSettingsBase):
    """Tạo mới settings — gắn với user_id"""
    user_id: int


class UserGrammarSettingsUpdate(BaseModel):
    """Cập nhật settings — tất cả field đều optional"""
    start_level: Optional[str] = None
    daily_limit: Optional[int] = None


class UserGrammarSettingsOut(UserGrammarSettingsBase):
    """Settings response"""
    id: int
    user_id: int
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
