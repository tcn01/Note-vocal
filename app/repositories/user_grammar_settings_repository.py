import logging
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_grammar_settings import UserGrammarSettings
from app.repositories.base_repository import BaseRepository
from app.schemas.user_grammar_settings import UserGrammarSettingsCreate, UserGrammarSettingsUpdate

logger = logging.getLogger(__name__)


# =============================================
# Repository: user_grammar_settings
# Quản lý cài đặt lộ trình học ngữ pháp của user.
# Mỗi user chỉ có 1 settings (unique user_id).
# =============================================

class UserGrammarSettingsRepository(BaseRepository):
    """Repository quản lý settings học ngữ pháp của user"""

    async def get_by_user(self, db: AsyncSession, user_id: int) -> Optional[UserGrammarSettings]:
        """Lấy settings của 1 user (unique)"""
        result = await db.execute(
            select(UserGrammarSettings).where(UserGrammarSettings.user_id == user_id)
        )
        return result.scalars().first()

    async def create_or_update(
        self, db: AsyncSession, user_id: int, obj_in: UserGrammarSettingsCreate
    ) -> UserGrammarSettings:
        """
        Tạo mới hoặc cập nhật settings cho user.
        Dùng khi user set trình độ lần đầu hoặc thay đổi.
        """
        existing = await self.get_by_user(db, user_id)
        if existing:
            for field, value in obj_in.model_dump(exclude_unset=True).items():
                if field != "user_id":
                    setattr(existing, field, value)
            await db.flush()
            await db.refresh(existing)
            return existing
        return await self.create(db, obj_in)


user_grammar_settings_repository = UserGrammarSettingsRepository(UserGrammarSettings)
