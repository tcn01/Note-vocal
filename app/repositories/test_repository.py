import logging
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_result import TestResult
from app.repositories.base_repository import BaseRepository
from app.schemas.test_result import TestResultCreate, TestResultUpdate

logger = logging.getLogger(__name__)


# =============================================
# Repository: test_results
# =============================================

class TestRepository(BaseRepository[TestResult, TestResultCreate, TestResultUpdate]):
    """Repository quản lý bài kiểm tra"""

    async def get_by_user(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[TestResult]:
        """Lấy danh sách bài kiểm tra của user"""
        result = await db.execute(
            select(TestResult)
            .where(TestResult.user_id == user_id)
            .order_by(TestResult.id.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def get_by_id_and_user(
        self, db: AsyncSession, test_id: int, user_id: int
    ) -> Optional[TestResult]:
        """Kiểm tra bài test thuộc về user"""
        result = await db.execute(
            select(TestResult).where(
                TestResult.id == test_id,
                TestResult.user_id == user_id,
            )
        )
        return result.scalars().first()


test_repository = TestRepository(TestResult)
