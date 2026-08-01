from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String
from sqlalchemy.sql import func

from app.core.database import Base


# =============================================
# Model: users
# grammar_level: Trình độ ngữ pháp đầu vào
# (A1/A2/B1/B2). Dùng để khởi tạo lộ trình
# học cá nhân hoá cho từng người dùng.
# =============================================

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    preferred_language = Column(Enum("vi", "en", "zh", name="preferred_language"), default="vi")
    role = Column(Enum("admin", "user", name="user_role"), default="user")
    grammar_level = Column(String(2), nullable=True, comment="Trình độ ngữ pháp: A1/A2/B1/B2")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
