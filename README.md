# VisionNest / NoteLanguage

Học ngôn ngữ thông minh với AI. Hỗ trợ Anh, Việt, Trung, Nhật, Hàn.

## Tech Stack

- **Backend**: FastAPI + SQLAlchemy 2.0 async + PostgreSQL + Redis
- **AI**: OpenRouter (free models), gTTS
- **Frontend**: React + TypeScript + Tailwind (in `frontend/`)
- **DevOps**: Docker Compose

## Quick Start

```bash
# 1. Database + Redis
docker compose up -d

# 2. Backend
cp .env.example .env
venv\Scripts\activate
pip install -r requirements.txt
python -m alembic upgrade head
python scripts/seed_grammar.py      # Seed 48 grammar topics
uvicorn app.main:app --reload       # http://localhost:8000

# Hoặc chạy tự động:
start.bat

# 3. Frontend
cd frontend
npm install
npm run dev                         # http://localhost:3000
```

## API Endpoints (16 endpoints)

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/api/v1/auth/login` | No | Login → JWT |
| POST | `/api/v1/users/` | No | Register |
| GET | `/api/v1/users/me` | Yes | Profile |
| GET/PATCH/DELETE | `/api/v1/users/{id}` | Yes | CRUD |
| PATCH | `/api/v1/users/me/grammar-level` | Yes | Set grammar level |
| POST | `/api/v1/ai/lookup-word` | Yes | Add word (AI lookup + TTS) |
| GET | `/api/v1/ai/vocabulary` | Yes | List words (date filter) |
| GET | `/api/v1/ai/grammar/curriculum` | Yes | Grammar topics + progress |
| GET | `/api/v1/ai/grammar/today` | Yes | Today's plan (review + new) |
| GET | `/api/v1/ai/grammar/next` | Yes | Skip to next topic |
| POST | `/api/v1/ai/grammar/generate` | Yes | Generate lesson |
| PATCH | `/api/v1/ai/grammar/lessons/{id}` | Yes | Update lesson |
| GET | `/api/v1/ai/grammar/lessons` | Yes | Lesson history |
| POST | `/api/v1/tests/generate` | Yes | Generate test (mixed 15q) |
| POST | `/api/v1/tests/{id}/submit` | Yes | Submit test → score |
| GET | `/api/v1/tests/` | Yes | Test history |

Full JSON schemas: see `API_REFERENCE.md`

## Testing

```bash
pytest tests/ -v        # 47 tests (user, grammar, vocab, test, openrouter)
```

## Swagger UI

`http://localhost:8000/docs` — Authorize with `Bearer <token>` after login.

## Project Structure

```
VisionNest/
├── app/                  # Backend (FastAPI)
│   ├── api/v1/endpoints/ # auth, users, ai, tests
│   ├── core/             # config, security, database, redis
│   ├── models/           # user, vocabulary, grammar, test_result
│   ├── schemas/          # Pydantic DTOs
│   ├── services/         # business logic
│   └── repositories/     # DB queries
├── frontend/             # React + TypeScript + Tailwind
├── data/                 # grammar_curriculum.yaml (48 topics)
├── scripts/              # seed_grammar.py
├── static/audio/         # TTS mp3 files
├── tests/                # 47 pytest tests
├── migrations/           # Alembic
├── API_REFERENCE.md      # Full API docs for FE
└── docker-compose.yml    # PostgreSQL + Redis
```
