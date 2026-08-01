import logging
from datetime import date
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grammar import GrammarLesson
from app.repositories.base_repository import BaseRepository
from app.schemas.grammar import GrammarLessonCreate, GrammarLessonUpdate

logger = logging.getLogger(__name__)


# =============================================
# Repository: grammar_lessons
# Quản lý bài học ngữ pháp đã được AI sinh.
# Các truy vấn đặc thù:
# - get_by_user: lấy tất cả bài của user
# - get_by_user_and_topic: kiểm tra đã học topic chưa
# - get_today_lessons: đếm số bài đã học hôm nay
# - get_completed_unreviewed: bài cần ôn tập
# =============================================

class GrammarLessonRepository(BaseRepository):
    """Repository quản lý bài học ngữ pháp của user"""

    async def get_by_user(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[GrammarLesson]:
        """Lấy tất cả bài học của user, mới nhất trước"""
        result = await db.execute(
            select(GrammarLesson)
            .where(GrammarLesson.user_id == user_id)
            .order_by(GrammarLesson.generated_date.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_user_and_topic(
        self, db: AsyncSession, user_id: int, topic_id: int
    ) -> Optional[GrammarLesson]:
        """Kiểm tra user đã học topic này chưa"""
        result = await db.execute(
            select(GrammarLesson).where(
                GrammarLesson.user_id == user_id,
                GrammarLesson.topic_id == topic_id,
            )
        )
        return result.scalars().first()

    async def get_today_count(
        self, db: AsyncSession, user_id: int, study_date: date
    ) -> int:
        """Đếm số bài user đã học trong 1 ngày"""
        result = await db.execute(
            select(GrammarLesson).where(
                GrammarLesson.user_id == user_id,
                GrammarLesson.generated_date == study_date,
            )
        )
        return len(result.scalars().all())

    async def get_completed_unreviewed(
        self, db: AsyncSession, user_id: int
    ) -> List[GrammarLesson]:
        """Lấy các bài đã complete nhưng chưa review"""
        result = await db.execute(
            select(GrammarLesson).where(
                GrammarLesson.user_id == user_id,
                GrammarLesson.is_completed == True,
                GrammarLesson.is_reviewed == False,
            )
            .order_by(GrammarLesson.generated_date.desc())
        )
        return result.scalars().all()


grammar_lesson_repository = GrammarLessonRepository(GrammarLesson)
