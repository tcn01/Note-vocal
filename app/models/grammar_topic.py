from sqlalchemy import Boolean, Column, Integer, String, Text

from app.core.database import Base


# =============================================
# Model: grammar_topics (curriculum)
# Đây là bảng curriculum — danh sách tất cả
# các chủ điểm ngữ pháp theo thứ tự học.
# Được seed từ file data/grammar_curriculum.yaml
# và dùng làm nguồn sự thật cho lộ trình học.
# =============================================

class GrammarTopic(Base):
    __tablename__ = "grammar_topics"

    id = Column(Integer, primary_key=True, index=True)
    order_num = Column(Integer, nullable=False, comment="Thứ tự học (1-48)")
    topic = Column(String, nullable=False, comment="Tên chủ điểm ngữ pháp")
    level = Column(String(2), nullable=False, comment="Trình độ: A1, A2, B1, B2")
    category = Column(String(50), nullable=False, comment="Nhóm: Tenses, Sentence Structure, Vocabulary & Grammar")
    description = Column(Text, default="", comment="Mô tả ngắn nội dung bài học")
    is_active = Column(Boolean, default=True, comment="Còn sử dụng trong curriculum không")
