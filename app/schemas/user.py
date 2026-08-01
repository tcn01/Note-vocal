from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    name: str
    preferred_language: str = "vi"
    role: str = "user"
    grammar_level: Optional[str] = None


class UserCreate(UserBase):
    password: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "name": "Nguyen Van A",
                "password": "securepassword123",
                "preferred_language": "vi",
                "role": "user",
            }
        }
    )


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    preferred_language: Optional[str] = None
    role: Optional[str] = None
    grammar_level: Optional[str] = None


class UserGrammarLevelUpdate(BaseModel):
    """Cập nhật trình độ ngữ pháp đầu vào"""
    grammar_level: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
