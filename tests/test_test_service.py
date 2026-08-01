from datetime import date, timedelta
from unittest.mock import patch

import pytest

from app.services.openrouter_service import openrouter_service
from app.services.test_service import test_service, _strip_answers

# =============================================
# Fake AI test response
# =============================================
FAKE_TEST_RESPONSE = {
    "questions": [
        {"id": 1, "type": "multiple_choice", "question": "Meaning of 'hello'?",
         "options": ["Xin chào", "Tạm biệt"], "answer": "Xin chào"},
        {"id": 2, "type": "fill_in_blank", "question": "She ___ a student.",
         "options": None, "answer": "is"},
        {"id": 3, "type": "listening", "question": "Choose the correct meaning",
         "options": ["từ điển", "quyển sách"], "word_audio": "book", "answer": "quyển sách"},
    ],
}


class TestTestService:
    """Unit tests cho Test Engine"""

    @pytest.mark.asyncio
    async def test_generate_test_success(self, db_session):
        """Sinh đề thành công với đủ từ vựng"""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.schemas.vocabulary import VocabularyCreate
        from app.repositories.vocabulary_repository import vocabulary_repository

        user = User(email="testgen@test.com", hashed_password=get_password_hash("pass"), name="Test Gen")
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        today = date.today()
        for i in range(6):
            await vocabulary_repository.create(db_session, VocabularyCreate(
                user_id=user.id, word=f"word{i}", language="en",
                definitions=[{"partOfSpeech": "noun", "meaning": f"nghĩa {i}", "example": ""}],
                learned_date=today,
            ))

        with patch.object(openrouter_service, "generate_test", return_value=FAKE_TEST_RESPONSE):
            result = await test_service.generate_test(db_session, user.id, today, today)

        assert result.total_questions == 3
        assert result.test_type == "mixed"
        # Questions should NOT contain 'answer' field
        for q in result.questions:
            assert "answer" not in q, f"Answer should be hidden: {q}"

    @pytest.mark.asyncio
    async def test_generate_test_not_enough_words(self, db_session):
        """Không đủ từ → raise ValueError"""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(email="fewwords@test.com", hashed_password=get_password_hash("pass"), name="Few Words")
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        today = date.today()
        with pytest.raises(ValueError, match="ít nhất"):
            await test_service.generate_test(db_session, user.id, today, today)

    @pytest.mark.asyncio
    async def test_submit_test_success(self, db_session):
        """Nộp bài → chấm điểm chính xác"""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.schemas.test_result import TestResultCreate
        from app.repositories.test_repository import test_repository

        user = User(email="submitok@test.com", hashed_password=get_password_hash("pass"), name="Submit OK")
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        test = await test_repository.create(db_session, TestResultCreate(
            user_id=user.id, test_type="mixed", start_date=date.today(),
            questions=FAKE_TEST_RESPONSE["questions"],
            total_questions=3,
        ))

        result = await test_service.submit_test(db_session, test.id, user.id, {
            "1": "Xin chào",   # đúng
            "2": "is",          # đúng
            "3": "sai rồi",     # sai
        })

        assert result.correct_answers == 2
        assert result.score == pytest.approx(66.7, rel=0.1)
        assert result.results["1"]["correct"] is True
        assert result.results["2"]["correct"] is True
        assert result.results["3"]["correct"] is False

    @pytest.mark.asyncio
    async def test_submit_test_not_found(self, db_session):
        """Test ID không tồn tại → raise ValueError"""
        from app.models.user import User
        from app.core.security import get_password_hash

        user = User(email="notfound@test.com", hashed_password=get_password_hash("pass"), name="Not Found")
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        with pytest.raises(ValueError, match="Không tìm thấy"):
            await test_service.submit_test(db_session, 999, user.id, {})

    @pytest.mark.asyncio
    async def test_submit_test_already_submitted(self, db_session):
        """Bài đã nộp → không nộp lại"""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.schemas.test_result import TestResultCreate
        from app.repositories.test_repository import test_repository

        user = User(email="duplicate@test.com", hashed_password=get_password_hash("pass"), name="Duplicate")
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        test = await test_repository.create(db_session, TestResultCreate(
            user_id=user.id, test_type="mixed", start_date=date.today(),
            questions=FAKE_TEST_RESPONSE["questions"],
            total_questions=3,
            answers={"1": "Xin chào"},  # đã nộp rồi
            correct_answers=1,
            score=33.3,
        ))

        with pytest.raises(ValueError, match="đã được nộp"):
            await test_service.submit_test(db_session, test.id, user.id, {"1": "Xin chào"})

    def test_strip_answers(self):
        """_strip_answers xoá đúng trường answer"""
        questions = [{"id": 1, "question": "test", "answer": "secret"}]
        cleaned = _strip_answers(questions)
        assert "answer" not in cleaned[0]
        assert cleaned[0]["id"] == 1

    @pytest.mark.asyncio
    async def test_get_user_tests(self, db_session):
        """Lấy lịch sử bài kiểm tra"""
        from app.models.user import User
        from app.core.security import get_password_hash
        from app.schemas.test_result import TestResultCreate
        from app.repositories.test_repository import test_repository

        user = User(email="history@test.com", hashed_password=get_password_hash("pass"), name="History")
        db_session.add(user)
        await db_session.flush()
        await db_session.refresh(user)

        await test_repository.create(db_session, TestResultCreate(
            user_id=user.id, test_type="mixed", start_date=date.today(), questions=[], total_questions=0,
        ))

        tests = await test_service.get_user_tests(db_session, user.id)
        assert len(tests) >= 1
