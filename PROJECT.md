# VisionNest / NoteLanguage — Tổng quan dự án

## 1. Mục tiêu
Xây dựng ứng dụng web học ngôn ngữ (Anh, Việt, Trung, Nhật, Hàn) với AI: nhập từ mới tự động tra cứu + TTS, sinh ngữ pháp theo lộ trình IELTS (48 topics A1→B2) cá nhân hoá, và bài test hỗn hợp.

## 2. Công nghệ chính
- **Backend**: FastAPI, SQLAlchemy 2.0 async, PostgreSQL, Redis (rate limiting), Alembic
- **AI**: OpenRouter (free models), gTTS (text-to-speech)
- **Frontend**: React + TypeScript + Tailwind, TanStack React Query, i18next
- **DevOps**: Docker Compose (PostgreSQL + Redis)

## 3. Kiến trúc (3-layer)
```
Router (endpoints) → Service (business logic) → Repository (DB queries)
```

## 4. Tính năng chính
| Tính năng | Mô tả |
|---|---|
| **Quản lý từ vựng** | Nhập từ → AI lookup (5 ngôn ngữ) + TTS → lưu DB. |
| **Ngữ pháp cá nhân hoá** | 48 topics IELTS (A1→B2), daily limit, review trước học mới. |
| **Bài test hỗn hợp** | Chọn khoảng ngày → AI sinh 15 câu (trắc nghiệm + điền từ + nghe). |
| **Đa ngôn ngữ UI** | Việt, Anh, Trung, Nhật, Hàn. |
| **Xác thực JWT** | HTTPBearer, rate limited register. |

## 5. Cấu trúc project

```
VisionNest/
├── app/                    # Backend (FastAPI)
├── frontend/               # Frontend (React + TypeScript)
├── data/                   # grammar_curriculum.yaml (48 topics)
├── scripts/                # seed_grammar.py
├── static/audio/           # TTS files
├── tests/                  # 47 tests
├── .agents/skills/         # AI development skills
│   ├── fastapi-templates/  # BE skill
│   └── frontend-visionnest/# FE skill (cho AI model khác)
├── API_REFERENCE.md        # Full JSON schemas cho FE team
├── ARCHITECTURE.md         # Diagram + data flows
├── PROJECT.md              # (file này)
├── docker-compose.yml      # PostgreSQL + Redis
└── README.md
```

## 6. API Summary (16 endpoints)

| Group | Endpoints |
|-------|-----------|
| Auth | `/auth/login` |
| Users | CRUD + `/users/me/grammar-level` |
| AI/Vocab | `/ai/lookup-word`, `/ai/vocabulary` |
| AI/Grammar | `/ai/grammar/curriculum`, `/today`, `/next`, `/generate`, `/lessons` |
| Tests | `/tests/generate`, `/tests/{id}/submit`, `/tests/` |

Xem `API_REFERENCE.md` cho JSON schemas chi tiết.

## 7. Development Notes
- **Seed data**: Sau migration, chạy `python scripts/seed_grammar.py` để nạp 48 topics.
- **Tests**: `pytest tests/ -v` (47 tests).
- **Swagger**: `http://localhost:8000/docs` — Authorize với Bearer token.
- **OpenRouter**: Free tier có rate limit và model chậm (~60s). Cần payment cho Gemini.
- **gTTS**: Miễn phí, không cần API key. File lưu tại `static/audio/`.
- **Database**: Unique key (`user_id`, `word`, `language`) tránh trùng từ.
- **Bảo mật**: bcrypt cho password, JWT expiry 30 phút, không lộ secret.

## 8. Chủ sở hữu
- Dự án: VisionNest / NoteLanguage
- Ngày tạo: 2026-07-05
