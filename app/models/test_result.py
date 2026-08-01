from sqlalchemy import JSON, Column, Date, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.core.database import Base


# =============================================
# Model: test_results
# Lưu kết quả bài kiểm tra hỗn hợp.
# questions: JSON chứa danh sách câu hỏi (có đáp án)
# answers:   JSON chứa câu trả lời của user (nullable)
# score:     Điểm số tính sau khi submit (0-100)
# =============================================

class TestResult(Base):
    __test__ = False
    __tablename__ = "test_results"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    test_type = Column(String, nullable=False, comment="Loại bài kiểm tra: mixed, vocabulary, grammar")
    start_date = Column(Date, nullable=False, comment="Ngày bắt đầu (khoảng học)")
    end_date = Column(Date, nullable=True, comment="Ngày kết thúc (khoảng học)")
    questions = Column(JSON, default=list, comment="Danh sách câu hỏi (có đáp án đúng)")
    answers = Column(JSON, nullable=True, comment="Câu trả lời của user {question_id: answer}")
    total_questions = Column(Integer, nullable=False, comment="Tổng số câu hỏi")
    correct_answers = Column(Integer, nullable=False, default=0, comment="Số câu đúng")
    score = Column(Float, nullable=True, comment="Điểm số 0-100")

    user = relationship("User", backref="test_results")
