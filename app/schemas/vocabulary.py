from datetime import date
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class Definition(BaseModel):
    partOfSpeech: str
    meaning: str
    example: str
    memory_tip: Optional[str] = None
    notes: Optional[str] = None


class VocabularyBase(BaseModel):
    word: str
    ipa: Optional[str] = None
    language: str
    definitions: List[Dict[str, Any]] = []
    pronunciation_url: Optional[str] = None
    examples: List[str] = []
    synonyms: List[str] = []
    memory_tip: Optional[str] = None
    notes: Optional[str] = None
    is_important: bool = False
    learned_date: Optional[date] = None


class VocabularyCreate(VocabularyBase):
    user_id: int


class VocabularyUpdate(BaseModel):
    definitions: Optional[List[Dict[str, Any]]] = None
    pronunciation_url: Optional[str] = None
    examples: Optional[List[str]] = None
    synonyms: Optional[List[str]] = None
    memory_tip: Optional[str] = None
    notes: Optional[str] = None
    is_important: Optional[bool] = None
    learned_date: Optional[date] = None


class Vocabulary(VocabularyBase):
    id: int
    user_id: int

    model_config = ConfigDict(from_attributes=True)