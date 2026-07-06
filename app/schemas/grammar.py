from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class GrammarLessonBase(BaseModel):
    topic: str
    level: str
    explanation: str
    examples: List[str] = []
    exercises: List[dict] = []
    generated_date: date


class GrammarLessonCreate(GrammarLessonBase):
    pass


class GrammarLessonUpdate(BaseModel):
    is_completed: Optional[bool] = None
    is_quiz_taken: Optional[bool] = None
    score: Optional[float] = None


class GrammarLesson(GrammarLessonBase):
    id: int
    user_id: int
    is_completed: bool = False
    is_quiz_taken: bool = False
    score: Optional[float] = None

    class Config:
        from_attributes = True
