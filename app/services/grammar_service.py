import logging
from datetime import date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.grammar import GrammarLesson
from app.models.grammar_topic import GrammarTopic
from app.models.user_grammar_settings import UserGrammarSettings
from app.repositories.grammar_lesson_repository import grammar_lesson_repository
from app.repositories.grammar_topic_repository import grammar_topic_repository
from app.repositories.user_grammar_settings_repository import (
    user_grammar_settings_repository,
)
from app.schemas.ai import GrammarResponse
from app.schemas.grammar import GrammarLessonCreate, GrammarLessonUpdate, TodayPlan
from app.schemas.grammar_topic import GrammarTopicProgress
from app.schemas.user_grammar_settings import UserGrammarSettingsCreate
from app.services.openrouter_service import openrouter_service

logger = logging.getLogger(__name__)

# =============================================
# LEVEL_ORDER: map thứ tự bắt đầu cho mỗi level
# Dùng để tính current_order khi user set trình độ.
# A1 bắt đầu từ topic 1, A2 từ 13, B1 từ 25, B2 từ 37.
# =============================================
LEVEL_START_ORDER = {
    "A1": 1,
    "A2": 13,
    "B1": 25,
    "B2": 37,
}


class GrammarService:
    """Dịch vụ quản lý lộ trình học ngữ pháp cá nhân hoá.
    
    Quy tắc daily learning:
    1. Kiểm tra bài hôm qua đã review chưa — nếu chưa thì học lại trước
    2. Nếu đã review hoặc không có bài cần review → học bài mới
    3. lessons_today >= daily_limit → chặn (trừ khi force = skip_to_next)
    4. Khi sang ngày mới → reset lessons_today = 0
    """

    async def _ensure_settings(
        self, db: AsyncSession, user_id: int
    ) -> UserGrammarSettings:
        """Tự động tạo settings nếu user chưa có (lazy init)"""
        settings = await user_grammar_settings_repository.get_by_user(db, user_id)
        if not settings:
            settings = await user_grammar_settings_repository.create(
                db, UserGrammarSettingsCreate(user_id=user_id)
            )
        return settings

    async def set_grammar_level(
        self, db: AsyncSession, user_id: int, level: str
    ) -> UserGrammarSettings:
        """Set trình độ đầu vào và khởi tạo lộ trình.
        
        - start_level = level người dùng chọn
        - current_order = topic đầu tiên của level đó
        - Tìm topic đầu tiên của level để lấy order_num
        """
        level = level.upper()
        if level not in LEVEL_START_ORDER:
            raise ValueError(f"Trình độ không hợp lệ: {level}. Chấp nhận: {', '.join(LEVEL_START_ORDER.keys())}")

        # Tìm topic đầu tiên của level để lấy order_num
        first_topic = await grammar_topic_repository.get_first_by_level(db, level)
        start_order = first_topic.order_num if first_topic else LEVEL_START_ORDER.get(level, 1)

        settings_data = UserGrammarSettingsCreate(
            user_id=user_id,
            start_level=level,
            current_order=start_order,
            daily_limit=1,
        )
        settings = await user_grammar_settings_repository.create_or_update(
            db, user_id, settings_data
        )
        logger.info(
            "Grammar level set: user=%s level=%s start_order=%s",
            user_id, level, start_order,
        )
        return settings

    async def get_today_plan(self, db: AsyncSession, user_id: int) -> TodayPlan:
        """Trả về kế hoạch học hôm nay.
        
        Logic:
        1. Lấy settings user
        2. Kiểm tra có bài cần review không (bài hôm qua chưa review)
        3. Kiểm tra daily limit
        4. Trả về { review, new, message }
        """
        settings = await self._ensure_settings(db, user_id)

        # Reset lessons_today nếu sang ngày mới
        today = date.today()
        if settings.last_study_date != today:
            settings.lessons_today = 0
            settings.last_study_date = today
            await db.flush()

        plan = TodayPlan(message="")

        # Kiểm tra bài cần review (bài hôm qua chưa review)
        review_lesson = await grammar_topic_repository.get_unreviewed_previous(
            db, user_id, settings.current_order
        )
        if review_lesson:
            lesson = await grammar_lesson_repository.get(db, review_lesson.id)
            if lesson:
                plan.review = lesson
                plan.message = "Hãy ôn lại bài hôm qua trước khi học bài mới!"

        # Kiểm tra daily limit cho bài mới
        if settings.lessons_today >= settings.daily_limit:
            # Còn bài cần review thì vẫn cho review, nhưng không cho new
            if not plan.review:
                plan.message = f"Bạn đã đạt giới hạn {settings.daily_limit} bài/ngày. Quay lại vào ngày mai hoặc dùng 'next' để học thêm!"
            return plan

        # Lấy topic tiếp theo chưa hoàn thành
        next_topic = await grammar_topic_repository.get_next_uncompleted(
            db, user_id, start_order=settings.current_order
        )
        if next_topic:
            plan.new = next_topic
            if not plan.message:
                plan.message = "Sẵn sàng học bài mới!"
        else:
            plan.message = "Chúc mừng! Bạn đã hoàn thành tất cả các chủ điểm ngữ pháp!"

        return plan

    async def generate_lesson(
        self, db: AsyncSession, user_id: int, topic_id: int
    ) -> GrammarLesson:
        """Sinh bài học từ 1 topic trong curriculum.
        
        1. Lấy thông tin topic từ DB
        2. Gọi AI sinh explanation + examples + exercises
        3. Lưu vào grammar_lessons
        4. Cập nhật settings (last_study_date, lessons_today, current_order)
        """
        # Lấy topic
        topic = await grammar_topic_repository.get(db, topic_id)
        if not topic:
            raise ValueError(f"Không tìm thấy topic_id={topic_id}")

        # Gọi AI
        ai_data = await openrouter_service.generate_grammar(topic.topic, topic.level)
        if not ai_data:
            raise ValueError(f"AI không sinh được bài học cho topic: {topic.topic}")

        # Parse response
        explanation = ai_data.get("explanation", "")
        examples = ai_data.get("examples", [])
        exercises = ai_data.get("exercises", [])

        # Tạo lesson
        lesson_in = GrammarLessonCreate(
            user_id=user_id,
            topic_id=topic.id,
            topic=topic.topic,
            level=topic.level,
            explanation=explanation,
            examples=examples,
            exercises=exercises,
            generated_date=date.today(),
        )
        lesson = await grammar_lesson_repository.create(db, lesson_in)

        # Cập nhật settings
        settings = await self._ensure_settings(db, user_id)
        today = date.today()

        # Reset lessons_today nếu sang ngày mới
        if settings.last_study_date != today:
            settings.lessons_today = 0

        settings.last_study_date = today
        settings.lessons_today = (settings.lessons_today or 0) + 1

        # Chỉ tăng current_order nếu đây là topic đang chờ học
        if settings.current_order <= topic.order_num:
            settings.current_order = topic.order_num + 1

        await db.flush()

        logger.info(
            "Grammar lesson generated: user=%s topic=%s level=%s",
            user_id, topic.topic, topic.level,
        )
        return lesson

    async def skip_to_next(self, db: AsyncSession, user_id: int) -> GrammarTopic:
        """Bỏ qua daily limit, trả về topic kế tiếp chưa hoàn thành.
        
        Dùng khi user muốn học nhiều hơn daily_limit trong 1 ngày.
        """
        settings = await self._ensure_settings(db, user_id)
        settings.lessons_today = max(0, (settings.lessons_today or 0) - 1)

        plan = await self.get_today_plan(db, user_id)
        if not plan.new:
            raise ValueError("Không còn topic nào để học!")
        return plan.new

    async def update_lesson(
        self, db: AsyncSession, lesson_id: int, user_id: int, update_data: GrammarLessonUpdate
    ) -> Optional[GrammarLesson]:
        """Cập nhật bài học (complete, review, score)"""
        lesson = await grammar_lesson_repository.get(db, lesson_id)
        if not lesson or lesson.user_id != user_id:
            return None
        return await grammar_lesson_repository.update(db, lesson, update_data)

    async def get_curriculum_progress(
        self, db: AsyncSession, user_id: int, level: Optional[str] = None
    ) -> List[GrammarTopicProgress]:
        """Lấy curriculum + trạng thái học của user"""
        return await grammar_topic_repository.get_with_progress(db, user_id, level)

    async def get_lessons(
        self, db: AsyncSession, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[GrammarLesson]:
        """Lấy lịch sử bài đã học"""
        return await grammar_lesson_repository.get_by_user(db, user_id, skip, limit)


grammar_service = GrammarService()
