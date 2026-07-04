# VisionNest API

Production-ready FastAPI backend with async patterns, PostgreSQL, JWT authentication, and layered architecture.

## Tech Stack

- **FastAPI** — async REST framework
- **PostgreSQL + asyncpg** — async database
- **SQLAlchemy 2.0** — async ORM
- **JWT + bcrypt** — authentication
- **Pytest + httpx** — async testing

## Project Structure

```
app/
├── api/v1/endpoints/   # Route handlers
├── core/               # Config, database, security
├── models/             # SQLAlchemy models
├── schemas/            # Pydantic validation
├── repositories/       # Data access layer
├── services/           # Business logic
└── main.py             # App entry point
```

## Setup

```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Endpoints

| Method | Path                 | Auth | Description        |
|--------|----------------------|------|--------------------|
| POST   | /api/v1/users/       | No   | Register user      |
| GET    | /api/v1/users/me     | Yes  | Current user       |
| GET    | /api/v1/users/       | Yes  | List users         |
| GET    | /api/v1/users/{id}   | Yes  | Get user by ID     |
| PATCH  | /api/v1/users/{id}   | Yes  | Update user        |
| DELETE | /api/v1/users/{id}   | Yes  | Delete user        |
| POST   | /api/v1/auth/login   | No   | Login → JWT token  |

## Testing

```bash
pytest tests/ -v
```
