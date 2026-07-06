from sqlalchemy import Boolean, Column, Date, Enum, Float, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class GrammarLesson(Base):
    __tablename__ = "grammar_lessons"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    topic = Column(String, nullable=False)
    level = Column(Enum("A1", "A2", "B1", "B2", name="grammar_level"), nullable=False)
    explanation = Column(Text, nullable=False)
    examples = Column(JSON, default=list)
    exercises = Column(JSON, default=list)
    generated_date = Column(Date, nullable=False)
    is_completed = Column(Boolean, default=False)
    is_quiz_taken = Column(Boolean, default=False)
    score = Column(Float, nullable=True)

    user = relationship("User", backref="grammar_lessons")
