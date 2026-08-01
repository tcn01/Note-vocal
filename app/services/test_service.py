import logging
from datetime import date
from typing import Any, Dict, List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.test_repository import test_repository
from app.repositories.vocabulary_repository import vocabulary_repository
from app.schemas.test_result import (
    TestResult,
    TestResultCreate,
    TestResultDetail,
    TestResultOut,
    TestResultUpdate,
)
from app.services.openrouter_service import openrouter_service

logger = logging.getLogger(__name__)

MIN_WORDS_FOR_TEST = 5


# =============================================
# Dịch vụ Test Engine
# Sinh đề kiểm tra hỗn hợp và chấm điểm
# =============================================

class TestService:
    """Dịch vụ sinh đề và chấm điểm bài kiểm tra từ vựng"""

    async def generate_test(
        self,
        db: AsyncSession,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> TestResultOut:
        """Sinh bài kiểm tra hỗn hợp dựa trên từ vựng trong khoảng ngày.
        
        Quy trình:
        1. Lấy danh sách từ vựng trong khoảng ngày
        2. Gọi AI sinh đề (15 câu: 5 trắc nghiệm + 5 điền từ + 5 nghe)
        3. Lưu vào TestResult
        4. Trả về DTO (ẩn đáp án)
        """
        # Bước 1: Lấy từ vựng
        words = await vocabulary_repository.get_by_date(db, user_id, start_date, end_date)
        if len(words) < MIN_WORDS_FOR_TEST:
            raise ValueError(
                f"Cần ít nhất {MIN_WORDS_FOR_TEST} từ để tạo đề. "
                f"Bạn mới có {len(words)} từ trong khoảng {start_date} → {end_date}."
            )

        word_list = [{"word": w.word, "meaning": w.definitions} for w in words]

        # Bước 2: Gọi AI sinh đề
        test_data = await openrouter_service.generate_test(word_list)
        if not test_data or "questions" not in test_data:
            raise ValueError("AI không sinh được đề kiểm tra")

        questions = test_data["questions"]
        if len(questions) != 15:
            logger.warning("AI returned %d questions instead of 15", len(questions))

        # Bước 3: Lưu vào DB
        test_in = TestResultCreate(
            user_id=user_id,
            test_type="mixed",
            start_date=start_date,
            end_date=end_date,
            questions=questions,
            total_questions=len(questions),
        )
        test = await test_repository.create(db, test_in)
        await db.flush()
        await db.refresh(test)

        logger.info(
            "Test generated: user=%s type=%s questions=%d",
            user_id, test.test_type, test.total_questions,
        )

        return TestResultOut(
            id=test.id,
            test_type=test.test_type,
            start_date=test.start_date,
            end_date=test.end_date,
            total_questions=test.total_questions,
            questions=_strip_answers(questions),
            score=test.score,
        )

    async def submit_test(
        self,
        db: AsyncSession,
        test_id: int,
        user_id: int,
        user_answers: Dict[str, str],
    ) -> TestResultDetail:
        """Nộp bài và chấm điểm.
        
        1. Lấy bài test từ DB
        2. So sánh đáp án
        3. Tính điểm
        4. Cập nhật DB
        5. Trả về kết quả chi tiết
        """
        test = await test_repository.get_by_id_and_user(db, test_id, user_id)
        if not test:
            raise ValueError("Không tìm thấy bài kiểm tra")

        if test.answers is not None:
            raise ValueError("Bài kiểm tra này đã được nộp trước đó")

        questions = test.questions
        correct = 0
        total = len(questions)
        results: Dict[str, Any] = {}

        for q in questions:
            qid = str(q["id"])
            user_ans = user_answers.get(qid, "").strip()
            correct_ans = q.get("answer", "").strip()

            is_correct = user_ans.lower() == correct_ans.lower()
            if is_correct:
                correct += 1

            results[qid] = {
                "correct": is_correct,
                "user_answer": user_ans,
                "correct_answer": correct_ans,
            }

        score = round((correct / total) * 100, 1) if total > 0 else 0

        # Cập nhật DB
        update_data = TestResultUpdate(
            answers=user_answers,
            correct_answers=correct,
            score=score,
        )
        await test_repository.update(db, test, update_data)
        await db.flush()

        logger.info(
            "Test submitted: user=%s test=%d score=%.1f%% (%d/%d)",
            user_id, test_id, score, correct, total,
        )

        return TestResultDetail(
            id=test.id,
            user_id=test.user_id,
            test_type=test.test_type,
            start_date=test.start_date,
            end_date=test.end_date,
            questions=questions,
            answers=user_answers,
            total_questions=total,
            correct_answers=correct,
            score=score,
            results=results,
        )

    async def get_user_tests(
        self,
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
    ) -> List[TestResult]:
        """Lấy lịch sử bài kiểm tra của user"""
        return await test_repository.get_by_user(db, user_id, skip, limit)


def _strip_answers(questions: List[dict]) -> List[dict]:
    """Xoá đáp án đúng khỏi câu hỏi trước khi gửi cho FE"""
    return [
        {k: v for k, v in q.items() if k != "answer"} if isinstance(q, dict) else q
        for q in questions
    ]


test_service = TestService()
