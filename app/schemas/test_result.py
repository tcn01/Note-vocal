from datetime import date
from typing import Optional

from pydantic import BaseModel


class TestResultBase(BaseModel):
    test_type: str
    start_date: date
    end_date: Optional[date] = None
    total_questions: int
    correct_answers: int
    score: Optional[float] = None


class TestResultCreate(TestResultBase):
    pass


class TestResultUpdate(BaseModel):
    end_date: Optional[date] = None
    score: Optional[float] = None


class TestResult(TestResultBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
