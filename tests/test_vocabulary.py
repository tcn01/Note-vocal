from unittest.mock import patch

import pytest

from app.services.openrouter_service import openrouter_service
from app.services.tts_service import tts_service
from app.services.vocabulary_service import vocabulary_service

# =============================================
# Fake AI lookup response
# =============================================
FAKE_LOOKUP_RESPONSE = {
    "definitions": [
        {"partOfSpeech": "noun", "meaning": "a greeting", "example": "Hello, how are you?"},
        {"partOfSpeech": "exclamation", "meaning": "used to attract attention", "example": "Hello, is anyone there?"},
    ],
    "examples": ["Hello world!", "She said hello to me."],
    "synonyms": ["hi", "greetings", "hey"],
    "memory_tip": "Think of 'hello' as a friendly wave in words.",
}


class TestVocabularyService:
    """Unit tests cho nghiệp vụ từ vựng"""

    @pytest.mark.asyncio
    async def test_add_new_word_success(self, db_session):
        """Tạo user + thêm từ mới thành công"""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            email="vocabuser@test.com",
            hashed_password=get_password_hash("testpass"),
            name="Vocab User",
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        with (
            patch.object(openrouter_service, "lookup_word", return_value=FAKE_LOOKUP_RESPONSE),
            patch.object(tts_service, "generate_pronunciation", return_value="/static/audio/abc.mp3"),
        ):
            vocab = await vocabulary_service.add_new_word(
                db_session, user.id, "hello", "English"
            )

        assert vocab.word == "hello"
        assert vocab.language == "en"
        assert len(vocab.definitions) == 2
        assert vocab.pronunciation_url == "/static/audio/abc.mp3"
        assert vocab.user_id == user.id

    @pytest.mark.asyncio
    async def test_add_duplicate_word_raises_error(self, db_session):
        """Thêm từ đã tồn tại → raise ValueError"""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.schemas.vocabulary import VocabularyCreate
        from app.repositories.vocabulary_repository import vocabulary_repository

        user = User(
            email="dupe@test.com",
            hashed_password=get_password_hash("pass"),
            name="Dupe User",
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        # Thêm từ trước vào DB
        existing = VocabularyCreate(
            user_id=user.id,
            word="hello",
            language="en",
            definitions=[],
        )
        await vocabulary_repository.create(db_session, existing)

        # Thử thêm lại → lỗi
        with pytest.raises(ValueError, match="đã tồn tại"):
            await vocabulary_service.add_new_word(db_session, user.id, "hello", "English")

    @pytest.mark.asyncio
    async def test_add_word_ai_fails(self, db_session):
        """AI không trả về data → raise ValueError"""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            email="aifail@test.com",
            hashed_password=get_password_hash("pass"),
            name="AI Fail User",
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        with patch.object(openrouter_service, "lookup_word", return_value={}):
            with pytest.raises(ValueError, match="không tra được"):
                await vocabulary_service.add_new_word(db_session, user.id, "test", "English")

    @pytest.mark.asyncio
    async def test_add_word_tts_fallback(self, db_session):
        """TTS lỗi → pronunciation_url=None, service vẫn hoạt động"""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(
            email="ttsfallback@test.com",
            hashed_password=get_password_hash("pass"),
            name="TTS Fallback",
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        with (
            patch.object(openrouter_service, "lookup_word", return_value=FAKE_LOOKUP_RESPONSE),
            patch.object(tts_service, "generate_pronunciation", return_value=None),
        ):
            vocab = await vocabulary_service.add_new_word(
                db_session, user.id, "hello", "English"
            )

        assert vocab.word == "hello"
        assert vocab.pronunciation_url is None

    @pytest.mark.asyncio
    async def test_get_vocabulary_by_date(self, db_session):
        """Lọc từ vựng theo khoảng ngày"""
        from datetime import date, timedelta
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.schemas.vocabulary import VocabularyCreate
        from app.repositories.vocabulary_repository import vocabulary_repository

        user = User(
            email="datefilter@test.com",
            hashed_password=get_password_hash("pass"),
            name="Date Filter",
        )
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        today = date.today()
        yesterday = today - timedelta(days=1)

        await vocabulary_repository.create(db_session, VocabularyCreate(
            user_id=user.id, word="hello", language="en", learned_date=today,
        ))
        await vocabulary_repository.create(db_session, VocabularyCreate(
            user_id=user.id, word="world", language="en", learned_date=yesterday,
        ))

        today_words = await vocabulary_service.get_vocabulary_by_date(
            db_session, user.id, today, today
        )
        assert len(today_words) == 1
        assert today_words[0].word == "hello"

        all_words = await vocabulary_service.get_vocabulary_by_date(
            db_session, user.id, yesterday, today
        )
        assert len(all_words) == 2
