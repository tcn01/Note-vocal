# VisionNest

Học ngôn ngữ thông minh với AI (Anh/Trung).

## Cấu trúc project

```
VisionNest/
├── app/               # Backend (FastAPI)
├── frontend/          # Frontend (React + TypeScript)
├── tests/             # Backend tests
├── requirements.txt
└── README.md
```

## Backend Setup

### Prerequisites
- Docker & Docker Compose (cho database)
- Python 3.11+

### 1. Khởi động database

```bash
docker compose up -d
```

### 2. Chạy backend

```bash
cp .env.example .env
venv\Scripts\activate       # Windows
pip install -r requirements.txt
python -m alembic upgrade head   # Tạo bảng
uvicorn app.main:app --reload    # http://localhost:8000
```

Hoặc dùng script tự động:

```bash
start.bat
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev                     # http://localhost:3000
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
pytest tests/ -v               # Backend tests
cd frontend && npm run build    # Frontend build
```
