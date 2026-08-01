import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grammar import GrammarLesson
from app.models.grammar_topic import GrammarTopic
from app.repositories.base_repository import BaseRepository
from app.schemas.grammar_topic import GrammarTopicProgress

logger = logging.getLogger(__name__)


# =============================================
# Repository: grammar_topics (curriculum)
# Các truy vấn đặc thù cho grammar_topics:
# - get_ordered: lấy topics theo thứ tự
# - get_by_order: lấy 1 topic theo order_num
# - get_with_progress: topics + trạng thái user
# - get_next: tìm topic tiếp theo chưa học
# =============================================

class GrammarTopicRepository(BaseRepository):
    """Repository quản lý curriculum ngữ pháp"""

    async def get_ordered(
        self, db: AsyncSession, level: Optional[str] = None
    ) -> List[GrammarTopic]:
        """Lấy danh sách topics theo thứ tự, có thể lọc theo level"""
        query = select(GrammarTopic).where(GrammarTopic.is_active == True)
        if level:
            query = query.where(GrammarTopic.level == level.upper())
        query = query.order_by(GrammarTopic.order_num)
        result = await db.execute(query)
        return result.scalars().all()

    async def get_by_order(self, db: AsyncSession, order_num: int) -> Optional[GrammarTopic]:
        """Lấy 1 topic theo order_num"""
        result = await db.execute(
            select(GrammarTopic).where(
                GrammarTopic.order_num == order_num,
                GrammarTopic.is_active == True,
            )
        )
        return result.scalars().first()

    async def get_first_by_level(self, db: AsyncSession, level: str) -> Optional[GrammarTopic]:
        """Lấy topic đầu tiên của 1 level (dùng khi set trình độ)"""
        result = await db.execute(
            select(GrammarTopic)
            .where(GrammarTopic.level == level.upper(), GrammarTopic.is_active == True)
            .order_by(GrammarTopic.order_num)
            .limit(1)
        )
        return result.scalars().first()

    async def get_with_progress(
        self, db: AsyncSession, user_id: int, level: Optional[str] = None
    ) -> List[GrammarTopicProgress]:
        """
        Lấy tất cả topics + trạng thái học của user.
        Dùng LEFT JOIN để biết user đã học topic nào chưa.
        """
        query = (
            select(
                GrammarTopic,
                GrammarLesson.id,
                GrammarLesson.is_completed,
                GrammarLesson.is_reviewed,
                GrammarLesson.score,
            )
            .outerjoin(
                GrammarLesson,
                (GrammarLesson.topic_id == GrammarTopic.id)
                & (GrammarLesson.user_id == user_id),
            )
            .where(GrammarTopic.is_active == True)
        )
        if level:
            query = query.where(GrammarTopic.level == level.upper())
        query = query.order_by(GrammarTopic.order_num)

        result = await db.execute(query)
        rows = result.all()

        progress_list = []
        for row in rows:
            topic = row[0]
            progress_list.append(GrammarTopicProgress(
                id=topic.id,
                order_num=topic.order_num,
                topic=topic.topic,
                level=topic.level,
                category=topic.category,
                description=topic.description,
                is_active=topic.is_active,
                is_completed=bool(row.is_completed) if row.is_completed is not None else False,
                is_reviewed=bool(row.is_reviewed) if row.is_reviewed is not None else False,
                has_lesson=row.id is not None,
                lesson_id=row.id,
                score=row.score,
            ))
        return progress_list

    async def get_next_uncompleted(
        self, db: AsyncSession, user_id: int, start_order: int = 1
    ) -> Optional[GrammarTopic]:
        """
        Tìm topic tiếp theo chưa hoàn thành (từ start_order trở đi).
        Dùng subquery để kiểm tra user đã complete topic nào chưa.
        """
        completed_subq = (
            select(GrammarLesson.topic_id)
            .where(
                GrammarLesson.user_id == user_id,
                GrammarLesson.is_completed == True,
                GrammarLesson.topic_id.isnot(None),
            )
            .subquery()
        )
        query = (
            select(GrammarTopic)
            .where(
                GrammarTopic.is_active == True,
                GrammarTopic.order_num >= start_order,
                GrammarTopic.id.notin_(select(completed_subq.c.topic_id)),
            )
            .order_by(GrammarTopic.order_num)
            .limit(1)
        )
        result = await db.execute(query)
        return result.scalars().first()

    async def get_unreviewed_previous(
        self, db: AsyncSession, user_id: int, current_order: int
    ) -> Optional[GrammarLesson]:
        """
        Kiểm tra bài hôm qua (current_order - 1) đã được review chưa.
        Nếu chưa → trả về để yêu cầu review trước khi học bài mới.
        """
        if current_order <= 1:
            return None
        prev_topic = await self.get_by_order(db, current_order - 1)
        if not prev_topic:
            return None
        result = await db.execute(
            select(GrammarLesson).where(
                GrammarLesson.user_id == user_id,
                GrammarLesson.topic_id == prev_topic.id,
                GrammarLesson.is_completed == True,
                GrammarLesson.is_reviewed == False,
            )
        )
        return result.scalars().first()


grammar_topic_repository = GrammarTopicRepository(GrammarTopic)
