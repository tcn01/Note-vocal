from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


# =============================================
# Schemas cho Test Engine
# =============================================


class TestQuestion(BaseModel):
    """1 câu hỏi trong đề"""
    id: int
    type: str  # multiple_choice, fill_in_blank, listening
    question: str
    options: Optional[List[str]] = None
    word_audio: Optional[str] = None
    answer: str


class TestGenerateRequest(BaseModel):
    """Yêu cầu sinh đề kiểm tra"""
    start_date: date
    end_date: date


class TestSubmitRequest(BaseModel):
    """Nộp bài — map question_id → câu trả lời của user"""
    answers: Dict[str, str]


class TestResultBase(BaseModel):
    __test__ = False
    test_type: str
    start_date: date
    end_date: Optional[date] = None
    questions: List[dict] = []
    total_questions: int
    correct_answers: int = 0
    score: Optional[float] = None


class TestResultCreate(BaseModel):
    __test__ = False
    user_id: int
    test_type: str
    start_date: date
    end_date: Optional[date] = None
    questions: List[dict]
    answers: Optional[dict] = None
    total_questions: int
    correct_answers: int = 0
    score: Optional[float] = None


class TestResultUpdate(BaseModel):
    __test__ = False
    end_date: Optional[date] = None
    answers: Optional[dict] = None
    correct_answers: Optional[int] = None
    score: Optional[float] = None


class TestResult(BaseModel):
    id: int
    user_id: int
    test_type: str
    start_date: date
    end_date: Optional[date] = None
    questions: List[dict] = []
    answers: Optional[dict] = None
    total_questions: int
    correct_answers: int = 0
    score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)


class TestResultDetail(TestResult):
    """Kết quả chi tiết sau khi nộp bài:
    - questions: danh sách câu hỏi gốc (có đáp án đúng)
    - answers: câu trả lời của user
    - results: map question_id → { correct, user_answer, correct_answer }
    """
    results: Optional[Dict[str, Any]] = None


class TestResultOut(BaseModel):
    """DTO trả về khi sinh đề — ẩn đáp án đúng"""
    id: int
    test_type: str
    start_date: date
    end_date: Optional[date] = None
    total_questions: int
    questions: List[dict] = []
    score: Optional[float] = None

    model_config = ConfigDict(from_attributes=True)
