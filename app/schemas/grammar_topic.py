from typing import Optional

from pydantic import BaseModel, ConfigDict


# =============================================
# Schema cho grammar_topics (curriculum)
# GrammarTopicOut: thông tin cơ bản 1 topic
# GrammarTopicProgress: topic + trạng thái học
# của user (đã complete chưa, có lesson chưa)
# =============================================


class GrammarTopicBase(BaseModel):
    """Thông tin cơ bản của 1 chủ điểm ngữ pháp"""
    order_num: int
    topic: str
    level: str
    category: str
    description: str = ""


class GrammarTopicOut(GrammarTopicBase):
    """Grammar topic — dùng cho response"""
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class GrammarTopicProgress(GrammarTopicOut):
    """Grammar topic kèm trạng thái học của user"""
    is_completed: bool = False
    is_reviewed: bool = False
    has_lesson: bool = False
    lesson_id: Optional[int] = None
    score: Optional[float] = None
