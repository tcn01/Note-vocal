import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.schemas.test_result import (
    TestGenerateRequest,
    TestResult as TestResultSchema,
    TestResultDetail,
    TestResultOut,
    TestSubmitRequest,
)
from app.schemas.user import User
from app.services.test_service import test_service

logger = logging.getLogger(__name__)

router = APIRouter()


# =============================================
# TEST ENDPOINTS — KIỂM TRA HỖN HỢP
# =============================================

@router.post("/generate", response_model=TestResultOut)
async def generate_test(
    req: TestGenerateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Sinh bài kiểm tra hỗn hợp dựa trên từ vựng trong khoảng ngày.
    Gồm 15 câu: 5 trắc nghiệm + 5 điền từ + 5 nghe.
    """
    try:
        test_out = await test_service.generate_test(
            db, current_user.id, req.start_date, req.end_date
        )
        await db.commit()
        return test_out
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error("Generate test error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate test",
        )


@router.post("/{test_id}/submit", response_model=TestResultDetail)
async def submit_test(
    test_id: int,
    req: TestSubmitRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Nộp bài kiểm tra. So sánh đáp án, tính điểm, trả về kết quả chi tiết."""
    try:
        result = await test_service.submit_test(
            db, test_id, current_user.id, req.answers
        )
        await db.commit()
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        await db.rollback()
        logger.error("Submit test error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit test",
        )


@router.get("/", response_model=List[TestResultSchema])
async def list_tests(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Lấy lịch sử bài kiểm tra đã làm"""
    try:
        return await test_service.get_user_tests(db, current_user.id, skip, limit)
    except Exception as e:
        logger.error("List tests error: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list tests",
        )
