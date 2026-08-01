import logging
from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.vocabulary_repository import vocabulary_repository
from app.schemas.vocabulary import Vocabulary, VocabularyCreate, VocabularyUpdate
from app.services.openrouter_service import openrouter_service
from app.services.tts_service import tts_service

logger = logging.getLogger(__name__)

LANG_NAME_TO_CODE = {
    "english": "en", "en": "en",
    "vietnamese": "vi", "vi": "vi",
    "chinese": "zh", "zh": "zh",
    "japanese": "ja", "ja": "ja",
    "korean": "ko", "ko": "ko",
}


class VocabularyService:

    async def add_new_word(
        self,
        db: AsyncSession,
        user_id: int,
        word: str,
        language: str,
    ) -> Vocabulary:
        lang_code = LANG_NAME_TO_CODE.get(language.lower(), language.lower())

        existing = await vocabulary_repository.get_by_user_word_lang(
            db, user_id, word, lang_code
        )
        if existing:
            logger.warning("Word already exists: user=%s word=%s", user_id, word)
            raise ValueError(f"Từ '{word}' đã tồn tại trong từ điển của bạn")

        data = await openrouter_service.lookup_word(word, language)
        if not data:
            raise ValueError(f"AI không tra được từ: {word}")

        pronunciation_url = await tts_service.generate_pronunciation(word, lang_code)

        # Extract per-definition memory_tip/notes into top-level fallback
        definitions = data.get("definitions", [])
        first_def = definitions[0] if definitions else {}

        vocab_in = VocabularyCreate(
            user_id=user_id,
            word=word,
            ipa=data.get("ipa"),
            language=lang_code,
            definitions=definitions,
            examples=data.get("examples", []),
            synonyms=data.get("synonyms", []),
            memory_tip=data.get("memory_tip", first_def.get("memory_tip")),
            notes=first_def.get("notes"),
            pronunciation_url=pronunciation_url,
            learned_date=date.today(),
        )
        vocab = await vocabulary_repository.create(db, vocab_in)
        await db.flush()
        await db.refresh(vocab)

        logger.info(
            "Vocabulary added: user=%s word=%s lang=%s ipa=%s tts=%s",
            user_id, word, lang_code, data.get("ipa"), bool(pronunciation_url),
        )
        return vocab

    async def get_user_vocabulary(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[Vocabulary]:
        return await vocabulary_repository.get_by_user(db, user_id, skip, limit)

    async def get_vocabulary_by_date(
        self,
        db: AsyncSession,
        user_id: int,
        from_date: date,
        to_date: date,
    ) -> List[Vocabulary]:
        return await vocabulary_repository.get_by_date(db, user_id, from_date, to_date)

    async def delete_word(
        self, db: AsyncSession, user_id: int, vocab_id: int
    ) -> bool:
        vocab = await vocabulary_repository.get_by_id_and_user(db, vocab_id, user_id)
        if not vocab:
            return False
        await vocabulary_repository.delete(db, vocab_id)
        return True

    async def toggle_important(
        self, db: AsyncSession, user_id: int, vocab_id: int
    ) -> Optional[Vocabulary]:
        vocab = await vocabulary_repository.get_by_id_and_user(db, vocab_id, user_id)
        if not vocab:
            return None
        update = VocabularyUpdate(is_important=not vocab.is_important)
        updated = await vocabulary_repository.update(db, vocab, update)
        return updated

    async def update_notes(
        self, db: AsyncSession, user_id: int, vocab_id: int, notes: str
    ) -> Optional[Vocabulary]:
        vocab = await vocabulary_repository.get_by_id_and_user(db, vocab_id, user_id)
        if not vocab:
            return None
        update = VocabularyUpdate(notes=notes)
        updated = await vocabulary_repository.update(db, vocab, update)
        return updated


vocabulary_service = VocabularyService()