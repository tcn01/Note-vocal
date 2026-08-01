from typing import List, Optional

from pydantic import BaseModel


class Definition(BaseModel):
    partOfSpeech: str
    meaning: str
    example: str
    memory_tip: Optional[str] = None
    notes: Optional[str] = None


class LookupWordRequest(BaseModel):
    word: str
    language: str


class LookupWordResponse(BaseModel):
    ipa: str = ""
    definitions: List[Definition] = []
    examples: List[str] = []
    synonyms: List[str] = []
    memory_tip: str = ""


class GrammarExample(BaseModel):
    sentence: str
    translation: str


class GrammarExercise(BaseModel):
    question: str
    options: List[str]
    answer: str


class GrammarRequest(BaseModel):
    topic: str
    level: str


class GrammarGenerateRequest(BaseModel):
    """Sinh bài học từ 1 topic trong curriculum"""
    topic_id: int


class GrammarResponse(BaseModel):
    explanation: str = ""
    examples: List[GrammarExample] = []
    exercises: List[GrammarExercise] = []