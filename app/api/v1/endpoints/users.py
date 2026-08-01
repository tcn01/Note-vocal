import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.core.rate_limiter import rate_limit
from app.schemas.user import User, UserCreate, UserGrammarLevelUpdate, UserUpdate
from app.schemas.user_grammar_settings import UserGrammarSettingsOut
from app.services.grammar_service import grammar_service
from app.services.user_service import user_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    dependencies=[rate_limit(5, 60)],
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    try:
        user = await user_service.create_user(db, user_in)
        logger.info("User registered: id=%s email=%s", user.id, user.email)
        return user
    except ValueError as e:
        logger.warning("User registration failed: %s", e)
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/me", response_model=User)
async def read_current_user(
    current_user: User = Depends(get_current_user),
):
    return current_user


@router.get("/", response_model=List[User])
async def read_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    users = await user_service.repository.get_multi(db, skip=skip, limit=limit)
    return users


@router.get("/{user_id}", response_model=User)
async def read_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    user = await user_service.repository.get(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=User)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    user = await user_service.update_user(db, user_id, user_in)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized")

    deleted = await user_service.repository.delete(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")


# =============================================
# GRAMMAR LEVEL — CÁ NHÂN HOÁ LỘ TRÌNH HỌC
# Cho phép user set trình độ ngữ pháp đầu vào.
# Hệ thống tự động tính topic bắt đầu phù hợp.
# =============================================

@router.patch("/me/grammar-level", response_model=UserGrammarSettingsOut)
async def set_grammar_level(
    req: UserGrammarLevelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Set trình độ ngữ pháp đầu vào.

    - A1 → bắt đầu từ topic 1
    - A2 → bắt đầu từ topic 13
    - B1 → bắt đầu từ topic 25
    - B2 → bắt đầu từ topic 37
    """
    try:
        settings = await grammar_service.set_grammar_level(
            db, current_user.id, req.grammar_level
        )
        # Cập nhật User model
        current_user.grammar_level = req.grammar_level
        await db.commit()
        return settings
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error("Set grammar level error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to set grammar level",
        )
