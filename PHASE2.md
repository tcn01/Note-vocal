# Phase 2: Authentication & Security

## Mục tiêu
- Củng cố luồng xác thực JWT + bcrypt
- Thêm Redis-based rate limiting (5 req/phút cho register)
- Thêm structured logging toàn bộ auth flow
- Viết test đầy đủ

## Kiến trúc

### Luồng xác thực

```
Client                    FastAPI                        Database/Redis
  │                         │                               │
  │  POST /api/v1/users/    │                               │
  │  (email, password)      │                               │
  │ ───────────────────────►│                               │
  │                         │  rate_limit(5, 60) ──────────►│  Redis
  │                         │◄──────────────────────────────│
  │                         │                               │
  │                         │  Check duplicate email ──────►│  PostgreSQL
  │                         │◄──────────────────────────────│
  │                         │  Hash password (bcrypt)       │
  │                         │  Create user ────────────────►│  PostgreSQL
  │                         │◄──────────────────────────────│
  │◄────────────────────────│  201 Created (user object)    │
  │                         │                               │
  │  POST /api/v1/auth/login│                               │
  │  (email, password)      │                               │
  │ ───────────────────────►│                               │
  │                         │  Get user by email ──────────►│  PostgreSQL
  │                         │◄──────────────────────────────│
  │                         │  Verify password (bcrypt)     │
  │                         │  Create JWT token             │
  │◄────────────────────────│  200 { access_token }         │
  │                         │                               │
  │  GET /api/v1/users/me   │                               │
  │  Authorization: Bearer..│                               │
  │ ───────────────────────►│                               │
  │                         │  Decode JWT ───────────       │
  │                         │  Get user by id ────────────►│  PostgreSQL
  │                         │◄──────────────────────────────│
  │◄────────────────────────│  200 (user object)            │
```

### Modules

| File | Chức năng |
|---|---|
| `app/core/security.py` | Hash/verify bcrypt, tạo JWT |
| `app/api/dependencies.py` | `get_current_user` — giải mã token, trả về user |
| `app/core/redis.py` | Kết nối Redis async (singleton), init/shutdown qua lifespan |
| `app/core/rate_limiter.py` | Sliding window rate limiter, trả về FastAPI `Depends` |
| `app/core/logging.py` | Cấu hình logging (stdout + rotating file) |
| `app/api/v1/endpoints/auth.py` | `POST /auth/login` |
| `app/api/v1/endpoints/users.py` | `POST /users/` (register), `GET /users/me` |

### Rate Limiting — Chi tiết

- **Thuật toán**: Sliding window trên Redis sorted set
- **Key pattern**: `rate_limit:{client_ip}:{url_path}`
- **Endpoint bị giới hạn**: `POST /api/v1/users/` — **5 requests / 60 giây**
- **Cách hoạt động**:
  1. `ZREMRANGEBYSCORE` xoá entries cũ ngoài window
  2. `ZCARD` đếm số request hiện tại
  3. Nếu >= max_requests → 429 Too Many Requests
  4. Nếu chưa đạt → `ZADD` request mới + `EXPIRE` key
- **Fallback**: Nếu Redis offline → log warning + skip rate limit (không block user)

### Logging — Chi tiết

- **Format**: `%(asctime)s | %(levelname)s | %(name)s | %(message)s`
- **Handlers**:
  - StreamHandler → stdout
  - RotatingFileHandler → `logs/app.log` (max 10MB, 5 backups)
- **Events được log**:
  - ✅ Register thành công (user id, email)
  - ❌ Register thất bại (duplicate email)
  - 🚫 Rate limit hit (ip, endpoint)
  - ✅ Login thành công (user id, email)
  - ❌ Login thất bại (wrong password / user not found)
  - ❌ JWT decode fail (invalid / expired token)

## Dependencies mới

```txt
redis>=5.0.0           # Redis async client
```

## API Endpoints

| Method | Endpoint | Auth | Rate Limit | Mô tả |
|---|---|---|---|---|
| POST | `/api/v1/users/` | No | 5 req/min | Đăng ký user |
| POST | `/api/v1/auth/login` | No | No | Đăng nhập, trả về JWT |
| GET | `/api/v1/users/me` | JWT | No | Lấy thông tin user hiện tại |
| GET | `/api/v1/users/` | JWT | No | Danh sách users (admin) |
| GET | `/api/v1/users/{id}` | JWT | No | Chi tiết user |
| PATCH | `/api/v1/users/{id}` | JWT | No | Cập nhật user |
| DELETE | `/api/v1/users/{id}` | JWT | No | Xoá user |

## Cấu trúc thư mục (sau Phase 2)

```
app/
├── api/
│   ├── v1/
│   │   ├── endpoints/
│   │   │   ├── auth.py
│   │   │   └── users.py
│   │   └── router.py
│   └── dependencies.py
├── core/
│   ├── config.py
│   ├── security.py           # JWT + bcrypt
│   ├── database.py           # Async SQLAlchemy
│   ├── redis.py              # Redis async connection   ← NEW
│   ├── rate_limiter.py       # Sliding window limiter   ← NEW
│   └── logging.py            # Structured logging      ← NEW
├── models/
│   └── user.py
├── schemas/
│   ├── user.py
│   └── auth.py
├── services/
│   └── user_service.py
├── repositories/
│   ├── base_repository.py
│   └── user_repository.py
├── migrations/
│   └── versions/
├── main.py                   # lifespan init Redis + logging
└── tests/
    ├── conftest.py
    └── test_users.py
```

## Testing

### Test cases cho Phase 2

```python
# test_users.py (hiện tại — 4 tests pass)
test_create_user            # 201 Created
test_create_duplicate_user  # 400 Duplicate email
test_login                  # 200 + access_token
test_read_current_user     # 200 + user info (with JWT)

# Cần thêm (sau Phase 2)
test_create_user_rate_limit # 429 after 5 requests
test_login_invalid_password # 401 wrong password
test_login_nonexistent_user # 401 user not found
test_access_expired_token   # 401 expired JWT
test_access_malformed_token # 401 bad JWT
```

### Config test hiện tại

```ini
# pytest.ini
[pytest]
asyncio_mode = auto
asyncio_default_fixture_loop_scope = function
```

> ⚠️ Lưu ý: Tests rate limiting cần mock Redis hoặc Redis test instance.
