import logging
from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.ai import (
    GrammarGenerateRequest,
    GrammarRequest,
    GrammarResponse,
    LookupWordRequest,
)
from app.schemas.grammar import GrammarLesson as GrammarLessonSchema
from app.schemas.grammar import GrammarLessonUpdate, TodayPlan
from app.schemas.grammar_topic import GrammarTopicProgress
from app.schemas.user import User
from app.schemas.vocabulary import Vocabulary as VocabSchema
from app.services.grammar_service import grammar_service
from app.services.openrouter_service import openrouter_service
from app.services.vocabulary_service import vocabulary_service

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================
# VOCABULARY ENDPOINTS
# =============================================

@router.post("/lookup-word", response_model=VocabSchema)
async def lookup_word(
    req: LookupWordRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Thêm từ mới: lookup AI + TTS + lưu DB.
    Nếu từ đã tồn tại → 409 Conflict.
    """
    try:
        vocab = await vocabulary_service.add_new_word(
            db, current_user.id, req.word, req.language
        )
        await db.commit()
        return vocab
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT if "đã tồn tại" in str(e) else status.HTTP_502_BAD_GATEWAY,
            detail=str(e),
        )
    except Exception as e:
        await db.rollback()
        logger.error("Lookup word error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to look up word",
        )


@router.get("/vocabulary", response_model=List[VocabSchema])
async def list_vocabulary(
    skip: int = 0,
    limit: int = 100,
    from_date: str = Query(None, description="Lọc từ ngày (YYYY-MM-DD)"),
    to_date: str = Query(None, description="Lọc đến ngày (YYYY-MM-DD)"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy danh sách từ vựng, có thể lọc theo khoảng ngày"""
    try:
        if from_date and to_date:
            fd = date.fromisoformat(from_date)
            td = date.fromisoformat(to_date)
            return await vocabulary_service.get_vocabulary_by_date(
                db, current_user.id, fd, td
            )
        return await vocabulary_service.get_user_vocabulary(
            db, current_user.id, skip, limit
        )
    except Exception as e:
        logger.error("List vocabulary error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list vocabulary",
        )


@router.delete("/vocabulary/{vocab_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_vocabulary(
    vocab_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Xoá từ vựng theo ID"""
    deleted = await vocabulary_service.delete_word(db, current_user.id, vocab_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    await db.commit()


@router.patch("/vocabulary/{vocab_id}/toggle-important", response_model=VocabSchema)
async def toggle_important(
    vocab_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Đánh dấu / bỏ đánh dấu từ quan trọng"""
    vocab = await vocabulary_service.toggle_important(db, current_user.id, vocab_id)
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    await db.commit()
    return vocab


@router.patch("/vocabulary/{vocab_id}/notes", response_model=VocabSchema)
async def update_notes(
    vocab_id: int,
    notes: str = Query(..., description="Ghi chú mới"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật ghi chú cho từ vựng"""
    vocab = await vocabulary_service.update_notes(db, current_user.id, vocab_id, notes)
    if not vocab:
        raise HTTPException(status_code=404, detail="Vocabulary not found")
    await db.commit()
    return vocab


# =============================================
# GRAMMAR ENDPOINTS — LỘ TRÌNH CÁ NHÂN HOÁ
# =============================================

@router.get("/grammar/curriculum", response_model=List[GrammarTopicProgress])
async def get_grammar_curriculum(
    level: str = Query(None, description="Lọc theo level: A1, A2, B1, B2"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy danh sách tất cả chủ điểm ngữ pháp kèm trạng thái học của user"""
    try:
        return await grammar_service.get_curriculum_progress(
            db, current_user.id, level
        )
    except Exception as e:
        logger.error("Get curriculum error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get curriculum",
        )


@router.get("/grammar/today", response_model=TodayPlan)
async def get_today_plan(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy kế hoạch học hôm nay:
    - review: bài cần ôn lại (nếu có)
    - new: bài mới (nếu còn trong daily limit)
    """
    try:
        return await grammar_service.get_today_plan(db, current_user.id)
    except Exception as e:
        logger.error("Get today plan error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get today plan",
        )


@router.get("/grammar/next", response_model=GrammarTopicProgress)
async def get_next_topic(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bỏ qua daily limit, lấy topic tiếp theo chưa hoàn thành."""
    try:
        topic = await grammar_service.skip_to_next(db, current_user.id)
        return GrammarTopicProgress(
            id=topic.id,
            order_num=topic.order_num,
            topic=topic.topic,
            level=topic.level,
            category=topic.category,
            description=topic.description,
            is_active=topic.is_active,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Get next topic error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get next topic",
        )


@router.post("/grammar/generate", response_model=GrammarLessonSchema)
async def generate_grammar_lesson(
    req: GrammarGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sinh bài học ngữ pháp cho 1 topic trong curriculum."""
    try:
        lesson = await grammar_service.generate_lesson(
            db, current_user.id, req.topic_id
        )
        await db.commit()
        return lesson
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error("Generate grammar lesson error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate grammar lesson",
        )


@router.patch("/grammar/lessons/{lesson_id}", response_model=GrammarLessonSchema)
async def update_grammar_lesson(
    lesson_id: int,
    update_data: GrammarLessonUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Cập nhật bài học: đánh dấu hoàn thành, review, cập nhật điểm"""
    try:
        lesson = await grammar_service.update_lesson(
            db, lesson_id, current_user.id, update_data
        )
        if not lesson:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Lesson not found",
            )
        await db.commit()
        return lesson
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error("Update lesson error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update lesson",
        )


@router.get("/grammar/lessons", response_model=List[GrammarLessonSchema])
async def list_grammar_lessons(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy lịch sử bài học ngữ pháp đã sinh"""
    try:
        return await grammar_service.get_lessons(db, current_user.id, skip, limit)
    except Exception as e:
        logger.error("List lessons error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list lessons",
        )
