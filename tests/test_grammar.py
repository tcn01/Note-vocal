from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.database import get_db
from app.main import app
from app.models.grammar_topic import GrammarTopic
from app.services.openrouter_service import openrouter_service

# =============================================
# Fake AI response dùng để mock OpenRouter
# =============================================
FAKE_GRAMMAR_RESPONSE = {
    "explanation": "Present Simple is used for habits, general truths, and repeated actions.",
    "examples": [
        {"sentence": "She drinks coffee every morning.", "translation": "Cô ấy uống cà phê mỗi sáng."},
        {"sentence": "The sun rises in the east.", "translation": "Mặt trời mọc ở hướng đông."},
    ],
    "exercises": [
        {
            "question": "Complete the sentence: She ___ (work) in a bank.",
            "options": ["work", "works", "working"],
            "answer": "works",
        },
    ],
}


# =============================================
# Fixture: seed 2 grammar topics vào test DB
# =============================================
@pytest.fixture
async def seed_topics(db_session):
    topic1 = GrammarTopic(
        order_num=1,
        topic="Present Simple — to be",
        level="A1",
        category="Tenses",
        description="Cách dùng am/is/are",
    )
    topic2 = GrammarTopic(
        order_num=2,
        topic="Present Simple — other verbs",
        level="A1",
        category="Tenses",
        description="Thêm s/es với ngôi thứ 3",
    )
    db_session.add(topic1)
    db_session.add(topic2)
    await db_session.flush()
    await db_session.refresh(topic1)
    await db_session.refresh(topic2)
    return topic1, topic2


# =============================================
# Fixture: đăng ký + login → trả về token
# =============================================
@pytest.fixture
async def auth_token(client):
    await client.post(
        "/api/v1/users/",
        json={
            "email": "grammar@test.com",
            "password": "testpass123",
            "name": "Grammar Tester",
        },
    )
    resp = await client.post(
        "/api/v1/auth/login",
        json={"email": "grammar@test.com", "password": "testpass123"},
    )
    return resp.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    return {"Authorization": f"Bearer {auth_token}"}


# =============================================
# TESTS
# =============================================

class TestSetGrammarLevel:
    """PATCH /api/v1/users/me/grammar-level"""

    async def test_set_level_success(self, client, auth_headers, db_session):
        resp = await client.patch(
            "/api/v1/users/me/grammar-level",
            json={"grammar_level": "B1"},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["start_level"] == "B1"
        assert data["current_order"] == 25  # topic đầu của B1

    async def test_set_level_invalid(self, client, auth_headers):
        resp = await client.patch(
            "/api/v1/users/me/grammar-level",
            json={"grammar_level": "C1"},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "không hợp lệ" in resp.json()["detail"].lower()

    async def test_set_level_unauthorized(self, client):
        resp = await client.patch(
            "/api/v1/users/me/grammar-level",
            json={"grammar_level": "A1"},
        )
        assert resp.status_code == 401


class TestGetTodayPlan:
    """GET /api/v1/ai/grammar/today"""

    async def test_today_plan_without_topics(self, client, auth_headers):
        """Không có topics nào trong DB → message hoàn thành"""
        resp = await client.get("/api/v1/ai/grammar/today", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "message" in data

    async def test_today_plan_with_topics(self, client, auth_headers, seed_topics):
        """Có topics nhưng chưa học → trả về bài mới"""
        resp = await client.get("/api/v1/ai/grammar/today", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["new"] is not None
        assert data["new"]["order_num"] == 1
        assert data["new"]["topic"] == "Present Simple — to be"
        assert data["review"] is None


class TestGrammarCurriculum:
    """GET /api/v1/ai/grammar/curriculum"""

    async def test_curriculum_empty(self, client, auth_headers):
        resp = await client.get("/api/v1/ai/grammar/curriculum", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_curriculum_with_topics(self, client, auth_headers, seed_topics):
        resp = await client.get("/api/v1/ai/grammar/curriculum", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(t["is_completed"] == False for t in data)
        assert all(t["has_lesson"] == False for t in data)

    async def test_curriculum_filter_by_level(self, client, auth_headers, seed_topics):
        resp = await client.get(
            "/api/v1/ai/grammar/curriculum?level=A2", headers=auth_headers
        )
        assert resp.status_code == 200
        assert resp.json() == []  # chỉ có A1 trong seed


class TestGenerateLesson:
    """POST /api/v1/ai/grammar/generate"""

    async def test_generate_topic_not_found(self, client, auth_headers):
        """topic_id không tồn tại → 400"""
        resp = await client.post(
            "/api/v1/ai/grammar/generate",
            json={"topic_id": 999},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    async def test_generate_success(self, client, auth_headers, seed_topics):
        """Sinh bài học từ topic → lưu grammar_lessons"""
        topic1, _ = seed_topics

        with patch.object(openrouter_service, "generate_grammar", return_value=FAKE_GRAMMAR_RESPONSE):
            resp = await client.post(
                "/api/v1/ai/grammar/generate",
                json={"topic_id": topic1.id},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["topic"] == "Present Simple — to be"
        assert data["level"] == "A1"
        assert data["topic_id"] == topic1.id
        assert data["explanation"] == FAKE_GRAMMAR_RESPONSE["explanation"]
        assert len(data["examples"]) == 2
        assert len(data["exercises"]) == 1
        assert data["is_completed"] == False

    async def test_generate_duplicate_topic(self, client, auth_headers, seed_topics):
        """Sinh lại topic đã học → vẫn cho phép"""
        topic1, _ = seed_topics
        with patch.object(openrouter_service, "generate_grammar", return_value=FAKE_GRAMMAR_RESPONSE):
            resp1 = await client.post(
                "/api/v1/ai/grammar/generate",
                json={"topic_id": topic1.id},
                headers=auth_headers,
            )
            resp2 = await client.post(
                "/api/v1/ai/grammar/generate",
                json={"topic_id": topic1.id},
                headers=auth_headers,
            )
        assert resp1.status_code == 200
        assert resp2.status_code == 200
        # Mỗi lần tạo 1 lesson mới
        assert resp1.json()["id"] != resp2.json()["id"]

    async def test_generate_unauthorized(self, client, seed_topics):
        topic1, _ = seed_topics
        resp = await client.post(
            "/api/v1/ai/grammar/generate",
            json={"topic_id": topic1.id},
        )
        assert resp.status_code == 401


class TestUpdateLesson:
    """PATCH /api/v1/ai/grammar/lessons/{id}"""

    async def _create_lesson(self, client, auth_headers, seed_topics):
        """Helper: tạo 1 lesson để test update"""
        topic1, _ = seed_topics
        with patch.object(openrouter_service, "generate_grammar", return_value=FAKE_GRAMMAR_RESPONSE):
            resp = await client.post(
                "/api/v1/ai/grammar/generate",
                json={"topic_id": topic1.id},
                headers=auth_headers,
            )
        return resp.json()["id"]

    async def test_update_complete(self, client, auth_headers, seed_topics):
        lesson_id = await self._create_lesson(client, auth_headers, seed_topics)

        resp = await client.patch(
            f"/api/v1/ai/grammar/lessons/{lesson_id}",
            json={"is_completed": True, "is_reviewed": True, "score": 8.5},
            headers=auth_headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_completed"] == True
        assert data["is_reviewed"] == True
        assert data["score"] == 8.5

    async def test_update_not_found(self, client, auth_headers):
        resp = await client.patch(
            "/api/v1/ai/grammar/lessons/999",
            json={"is_completed": True},
            headers=auth_headers,
        )
        assert resp.status_code == 404

    async def test_update_other_user_lesson(self, client, auth_headers, seed_topics):
        """User khác không thể update bài của user này"""
        lesson_id = await self._create_lesson(client, auth_headers, seed_topics)

        # Tạo user khác
        await client.post(
            "/api/v1/users/",
            json={
                "email": "other@test.com",
                "password": "pass123",
                "name": "Other User",
            },
        )
        resp_login = await client.post(
            "/api/v1/auth/login",
            json={"email": "other@test.com", "password": "pass123"},
        )
        other_headers = {"Authorization": f"Bearer {resp_login.json()['access_token']}"}

        resp = await client.patch(
            f"/api/v1/ai/grammar/lessons/{lesson_id}",
            json={"is_completed": True},
            headers=other_headers,
        )
        assert resp.status_code == 404

    async def test_update_unauthorized(self, client, auth_headers, seed_topics):
        lesson_id = await self._create_lesson(client, auth_headers, seed_topics)
        resp = await client.patch(
            f"/api/v1/ai/grammar/lessons/{lesson_id}",
            json={"is_completed": True},
        )
        assert resp.status_code == 401


class TestGetLessons:
    """GET /api/v1/ai/grammar/lessons"""

    async def test_list_empty(self, client, auth_headers):
        resp = await client.get("/api/v1/ai/grammar/lessons", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    async def test_list_with_lessons(self, client, auth_headers, seed_topics):
        topic1, _ = seed_topics
        with patch.object(openrouter_service, "generate_grammar", return_value=FAKE_GRAMMAR_RESPONSE):
            await client.post(
                "/api/v1/ai/grammar/generate",
                json={"topic_id": topic1.id},
                headers=auth_headers,
            )

        resp = await client.get("/api/v1/ai/grammar/lessons", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["topic"] == "Present Simple — to be"
        assert data[0]["topic_id"] == topic1.id


class TestGetNextTopic:
    """GET /api/v1/ai/grammar/next"""

    async def test_next_without_topics(self, client, auth_headers):
        resp = await client.get("/api/v1/ai/grammar/next", headers=auth_headers)
        assert resp.status_code == 400
        assert "không" in resp.json()["detail"].lower() or "topic" in resp.json()["detail"].lower()

    async def test_next_after_completing_first(self, client, auth_headers, seed_topics):
        topic1, topic2 = seed_topics

        # Học topic 1
        with patch.object(openrouter_service, "generate_grammar", return_value=FAKE_GRAMMAR_RESPONSE):
            lesson_resp = await client.post(
                "/api/v1/ai/grammar/generate",
                json={"topic_id": topic1.id},
                headers=auth_headers,
            )
        lesson_id = lesson_resp.json()["id"]

        # Mark complete + reviewed
        await client.patch(
            f"/api/v1/ai/grammar/lessons/{lesson_id}",
            json={"is_completed": True, "is_reviewed": True},
            headers=auth_headers,
        )

        # GET /next → topic 2
        resp = await client.get("/api/v1/ai/grammar/next", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["order_num"] == 2
        assert resp.json()["topic"] == "Present Simple — other verbs"
