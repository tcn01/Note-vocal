from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash, verify_password
from app.repositories.user_repository import user_repository
from app.schemas.user import User, UserCreate, UserUpdate


class UserService:
    def __init__(self):
        self.repository = user_repository

    async def create_user(self, db: AsyncSession, user_in: UserCreate) -> User:
        existing = await self.repository.get_by_email(db, user_in.email)
        if existing:
            raise ValueError("Email already registered")

        user_dict = user_in.model_dump()
        user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
        user = await self.repository.create(db, UserCreate(**user_dict))
        return user

    async def authenticate(
        self, db: AsyncSession, email: str, password: str
    ) -> Optional[User]:
        user = await self.repository.get_by_email(db, email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def update_user(
        self, db: AsyncSession, user_id: int, user_in: UserUpdate
    ) -> Optional[User]:
        user = await self.repository.get(db, user_id)
        if not user:
            return None

        if user_in.password:
            user_dict = user_in.model_dump(exclude_unset=True)
            user_dict["hashed_password"] = get_password_hash(
                user_dict.pop("password")
            )
            user_in = UserUpdate(**user_dict)

        return await self.repository.update(db, user, user_in)


user_service = UserService()
