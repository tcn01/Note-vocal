from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


# =============================================
# Model: user_grammar_settings
# Lưu trạng thái học ngữ pháp cá nhân hoá cho
# từng người dùng:
# - start_level: trình độ đầu vào (A1/A2/B1/B2)
# - current_order: topic hiện tại (tham chiếu order_num)
# - daily_limit: số bài mới tối đa mỗi ngày
# - last_study_date: ngày học gần nhất
# - lessons_today: số bài đã học hôm nay
# =============================================

class UserGrammarSettings(Base):
    __tablename__ = "user_grammar_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="FK → users.id")
    start_level = Column(String(2), default="A1", comment="Trình độ đầu vào: A1/A2/B1/B2")
    current_order = Column(Integer, default=1, comment="Thứ tự topic đang học (order_num)")
    daily_limit = Column(Integer, default=1, comment="Số bài mới tối đa mỗi ngày")
    last_study_date = Column(Date, nullable=True, comment="Ngày học gần nhất (reset lessons_today)")
    lessons_today = Column(Integer, default=0, comment="Số bài đã học hôm nay")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="Ngày tạo")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="Ngày cập nhật")

    user = relationship("User", backref="grammar_settings")
