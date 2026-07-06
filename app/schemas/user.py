from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr

from app.core.database import Base


class UserBase(BaseModel):
    email: EmailStr
    name: str
    preferred_language: str = "vi"
    role: str = "user"


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    password: Optional[str] = None
    preferred_language: Optional[str] = None
    role: Optional[str] = None


class User(UserBase):
    id: int
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
