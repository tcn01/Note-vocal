from datetime import date
from typing import List, Optional

from pydantic import BaseModel


class VocabularyBase(BaseModel):
    word: str
    language: str
    definitions: List[str] = []
    pronunciation_url: Optional[str] = None
    examples: List[str] = []
    synonyms: List[str] = []
    memory_tip: Optional[str] = None
    learned_date: Optional[date] = None


class VocabularyCreate(VocabularyBase):
    pass


class VocabularyUpdate(BaseModel):
    definitions: Optional[List[str]] = None
    pronunciation_url: Optional[str] = None
    examples: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    memory_tip: Optional[str] = None
    learned_date: Optional[date] = None


class Vocabulary(VocabularyBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True
