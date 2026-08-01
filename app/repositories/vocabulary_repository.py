import logging
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.vocabulary import Vocabulary
from app.repositories.base_repository import BaseRepository
from app.schemas.vocabulary import VocabularyCreate, VocabularyUpdate

logger = logging.getLogger(__name__)


class VocabularyRepository(BaseRepository[Vocabulary, VocabularyCreate, VocabularyUpdate]):

    async def get_by_user_word_lang(
        self, db: AsyncSession, user_id: int, word: str, language: str
    ) -> Optional[Vocabulary]:
        result = await db.execute(
            select(Vocabulary).where(
                Vocabulary.user_id == user_id,
                Vocabulary.word == word,
                Vocabulary.language == language,
            )
        )
        return result.scalars().first()

    async def get_by_user(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Vocabulary]:
        result = await db.execute(
            select(Vocabulary)
            .where(Vocabulary.user_id == user_id)
            .order_by(Vocabulary.learned_date.desc(), Vocabulary.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_date(
        self, db: AsyncSession, user_id: int, from_date: date, to_date: date
    ) -> List[Vocabulary]:
        result = await db.execute(
            select(Vocabulary)
            .where(
                Vocabulary.user_id == user_id,
                Vocabulary.learned_date >= from_date,
                Vocabulary.learned_date <= to_date,
            )
            .order_by(Vocabulary.learned_date.desc())
        )
        return result.scalars().all()

    async def get_by_id_and_user(
        self, db: AsyncSession, vocab_id: int, user_id: int
    ) -> Optional[Vocabulary]:
        result = await db.execute(
            select(Vocabulary).where(
                Vocabulary.id == vocab_id,
                Vocabulary.user_id == user_id,
            )
        )
        return result.scalars().first()


vocabulary_repository = VocabularyRepository(Vocabulary)