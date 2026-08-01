from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.grammar_topic import GrammarTopicOut


# =============================================
# Schema cho grammar_lessons
# topic_id: FK đến grammar_topics (curriculum).
# Nếu null tức bài học custom (không trong curriculum).
# is_reviewed: đánh dấu đã ôn tập.
# =============================================


class GrammarLessonBase(BaseModel):
    topic_id: Optional[int] = None
    topic: str
    level: str
    explanation: str
    examples: List[dict] = []
    exercises: List[dict] = []
    generated_date: date


class GrammarLessonCreate(GrammarLessonBase):
    user_id: int


class GrammarLessonUpdate(BaseModel):
    is_completed: Optional[bool] = None
    is_reviewed: Optional[bool] = None
    is_quiz_taken: Optional[bool] = None
    score: Optional[float] = None


class GrammarLesson(GrammarLessonBase):
    id: int
    user_id: int
    is_completed: bool = False
    is_reviewed: bool = False
    is_quiz_taken: bool = False
    score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class TodayPlan(BaseModel):
    """Kế hoạch học hôm nay: review bài cũ + học bài mới"""
    review: Optional[GrammarLesson] = None
    new: Optional[GrammarTopicOut] = None
    message: str = ""
