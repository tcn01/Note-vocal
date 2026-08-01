# VisionNest / NoteLanguage — API Reference

> Dành cho Frontend Developer. Base URL: `http://localhost:8000/api/v1`

---

## 1. Authentication

### POST `/auth/login`

Đăng nhập → nhận JWT token.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response `200` — Token:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Lưu ý:**
- Tất cả endpoint khác đều yêu cầu `Authorization: Bearer <token>` header.
- Swagger UI Authorize → paste token dạng `eyJ...` (không cần "Bearer " prefix).
- Token hết hạn sau 30 phút (configurable trong `.env`).

---

## 2. Users

### POST `/users/` — Đăng ký

**Request:**
```json
{
  "email": "user@example.com",
  "name": "Nguyen Van A",
  "password": "securepassword123",
  "preferred_language": "vi",
  "role": "user"
}
```

**Response `201`:**
```json
{
  "id": 1,
  "email": "user@example.com",
  "name": "Nguyen Van A",
  "preferred_language": "vi",
  "role": "user",
  "grammar_level": null,
  "is_active": true,
  "created_at": "2026-07-08T12:00:00"
}
```

### GET `/users/me` — Thông tin user hiện tại

Auth required. Trả về User object như trên.

### GET `/users/` — Danh sách users

Query params: `skip=0&limit=100`

### GET `/users/{user_id}` — 1 user theo ID

### PATCH `/users/{user_id}` — Cập nhật user

**Request** (tất cả optional):
```json
{
  "email": "new@example.com",
  "name": "New Name",
  "password": "newpass",
  "preferred_language": "en",
  "role": "user",
  "grammar_level": "B1"
}
```

### DELETE `/users/{user_id}` → `204 No Content`

### PATCH `/users/me/grammar-level` — Set trình độ ngữ pháp

**Request:**
```json
{
  "grammar_level": "A1"
}
```

**Response — UserGrammarSettings:**
```json
{
  "id": 1,
  "user_id": 1,
  "start_level": "A1",
  "current_order": 1,
  "daily_limit": 1,
  "last_study_date": null,
  "lessons_today": 0,
  "updated_at": "2026-07-08T12:00:00"
}
```

**Quy tắc mapping level → topic bắt đầu:**
| Level | order_num đầu tiên |
|-------|-------------------|
| A1    | 1                 |
| A2    | 13                |
| B1    | 25                |
| B2    | 37                |

---

## 3. Vocabulary

### POST `/ai/lookup-word` — Thêm từ mới

**Request:**
```json
{
  "word": "serendipity",
  "language": "en"
}
```

`language` hỗ trợ: `en` (Anh), `vi` (Việt), `zh` (Trung), `ja` (Nhật), `ko` (Hàn).

**Response `200`:**
```json
{
  "id": 42,
  "user_id": 1,
  "word": "serendipity",
  "ipa": "/ˌserənˈdɪpəti/",
  "language": "en",
  "definitions": [
    {
      "partOfSpeech": "noun",
      "meaning": "sự tình cờ may mắn",
      "example": "Finding that book was pure serendipity.",
      "memory_tip": "Serendip = tên vua Serendip",
      "notes": "Thường dùng trong văn viết trang trọng"
    },
    {
      "partOfSpeech": "verb",
      "meaning": "tình cờ phát hiện",
      "example": "I serendipitied this rare book.",
      "memory_tip": null,
      "notes": "Dạng verb không phổ biến"
    }
  ],
  "pronunciation_url": "/static/audio/abc123.mp3",
  "examples": ["Finding that book was pure serendipity."],
  "synonyms": ["luck", "chance"],
  "memory_tip": "Serendip = vua Serendip (Sri Lanka) thích tình cờ khám phá",
  "notes": null,
  "is_important": false,
  "learned_date": "2026-07-08"
}
```

**Error `409`:**
```json
{
  "detail": "Từ \"serendipity\" đã tồn tại trong hệ thống"
}
```

**Error `502`:** AI lookup failed (OpenRouter không phản hồi).
**Error `500`:** Lỗi DB hoặc TTS.

**Quy trình:**
1. Gọi OpenRouter AI → sinh IPA + definitions (mỗi loại từ có meaning, memory_tip, notes) (~5-15s)
2. Gọi gTTS → file âm thanh
3. Lưu DB
4. Trả về DTO

### GET `/ai/vocabulary` — Danh sách từ vựng

**Query params:** `skip=0&limit=100&from_date=2026-07-01&to_date=2026-07-08`

Trả về `List[Vocabulary]` (mảng các object như trên, sắp xếp theo `learned_date` mới nhất).

### DELETE `/ai/vocabulary/{vocab_id}` — Xoá từ

Auth required. Trả về `204 No Content`.

### PATCH `/ai/vocabulary/{vocab_id}/toggle-important` — Đánh dấu quan trọng

Auth required. Trả về Vocabulary đã cập nhật.

### PATCH `/ai/vocabulary/{vocab_id}/notes` — Cập nhật ghi chú

**Query param:** `notes=ghi chú mới`

Auth required. Trả về Vocabulary đã cập nhật.

---

## 4. Grammar — Curriculum & Personalized Learning Path

### GET `/ai/grammar/curriculum` — Toàn bộ chương trình học

**Query params:** `level=A1` (optional, filter theo level)

**Response — `List[GrammarTopicProgress]`:**
```json
[
  {
    "id": 1,
    "order_num": 1,
    "topic": "Present Simple — to be",
    "level": "A1",
    "category": "Tenses",
    "description": "Cách dùng am/is/are trong câu khẳng định, phủ định, nghi vấn",
    "is_active": true,
    "is_completed": false,
    "is_reviewed": false,
    "has_lesson": false,
    "lesson_id": null,
    "score": null
  }
]
```

### GET `/ai/grammar/today` — Kế hoạch học hôm nay

**Response — TodayPlan:**
```json
{
  "review": {
    "id": 5,
    "user_id": 1,
    "topic_id": 2,
    "topic": "Present Simple — other verbs",
    "level": "A1",
    "explanation": "...",
    "examples": [{"sentence": "...", "translation": "..."}],
    "exercises": [{"question": "...", "options": ["a","b"], "answer": "a"}],
    "generated_date": "2026-07-07",
    "is_completed": true,
    "is_reviewed": false,
    "is_quiz_taken": false,
    "score": 80.0
  },
  "new": {
    "id": 3,
    "order_num": 3,
    "topic": "Articles: a/an, the",
    "level": "A1",
    "category": "Vocabulary & Grammar",
    "description": "Mạo từ cơ bản — khi nào dùng a, an, the",
    "is_active": true
  },
  "message": "Học 1 bài mới hôm nay"
}
```

**Quy tắc `today` plan:**
- `review` = bài đã "complete" nhưng chưa "reviewed" (học trước, ưu tiên ôn lại)
- `new` = topic tiếp theo chưa hoàn thành (trong daily limit, mặc định 1)
- `review` = null nếu không cần ôn
- `new` = null nếu đã hết daily limit hoặc đã học hết curriculum
- `message`: thông báo bằng tiếng Việt cho user

### GET `/ai/grammar/next` — Bỏ qua daily limit, lấy topic tiếp theo

Không cần body. Trả về `GrammarTopicProgress` (giống 1 phần tử trong curriculum).

Dùng khi user muốn "học thêm" sau khi đã học bài mới hôm nay.

### POST `/ai/grammar/generate` — Sinh bài học cho 1 topic

**Request:**
```json
{
  "topic_id": 3
}
```

**Response — GrammarLesson:**
```json
{
  "id": 10,
  "user_id": 1,
  "topic_id": 3,
  "topic": "Articles: a/an, the",
  "level": "A1",
  "explanation": "Dùng 'a' trước phụ âm, 'an' trước nguyên âm...",
  "examples": [
    {"sentence": "I have a cat.", "translation": "Tôi có một con mèo"},
    {"sentence": "She is an engineer.", "translation": "Cô ấy là kỹ sư"}
  ],
  "exercises": [
    {
      "question": "Fill in: She is ___ engineer.",
      "options": ["a", "an", "the"],
      "answer": "an"
    }
  ],
  "generated_date": "2026-07-08",
  "is_completed": false,
  "is_reviewed": false,
  "is_quiz_taken": false,
  "score": null
}
```

### PATCH `/ai/grammar/lessons/{lesson_id}` — Cập nhật bài học

**Request** (tất cả optional):
```json
{
  "is_completed": true,
  "is_reviewed": true,
  "is_quiz_taken": true,
  "score": 90.0
}
```

**Response:** GrammarLesson đã cập nhật.

### GET `/ai/grammar/lessons` — Lịch sử bài học đã sinh

**Query params:** `skip=0&limit=100`

Trả về `List[GrammarLesson]`.

---

## 5. Test Engine

### POST `/tests/generate` — Sinh đề kiểm tra

**Request:**
```json
{
  "start_date": "2026-07-01",
  "end_date": "2026-07-08"
}
```

**Response — TestResultOut (đã ẩn đáp án):**
```json
{
  "id": 15,
  "test_type": "mixed",
  "start_date": "2026-07-01",
  "end_date": "2026-07-08",
  "total_questions": 15,
  "questions": [
    {
      "id": 1,
      "type": "multiple_choice",
      "question": "What is the meaning of 'serendipity'?",
      "options": ["sự tình cờ may mắn", "sự thất vọng", "sự ngạc nhiên"],
      "word_audio": null
    },
    {
      "id": 6,
      "type": "fill_in_blank",
      "question": "She ___ a student at Harvard.",
      "options": null,
      "word_audio": null
    },
    {
      "id": 11,
      "type": "listening",
      "question": "Choose the correct meaning of the word you hear",
      "options": ["từ điển", "quyển sách"],
      "word_audio": "book"
    }
  ],
  "score": null
}
```

**Lưu ý:** Field `answer` đã bị xoá khỏi mỗi question. FE không thấy đáp án đúng khi render.

**Error `400` (không đủ từ):**
```json
{
  "detail": "Cần ít nhất 5 từ để tạo đề. Bạn mới có 3 từ trong khoảng 2026-07-01 → 2026-07-08."
}
```

**Cấu trúc câu hỏi (đầy đủ, có đáp án — FE không bao giờ thấy):**
```json
{
  "id": 1,
  "type": "multiple_choice",
  "question": "...",
  "options": ["A", "B", "C"],
  "word_audio": null,
  "answer": "A"
}
```

### POST `/tests/{test_id}/submit` — Nộp bài

**Request:**
```json
{
  "answers": {
    "1": "sự tình cờ may mắn",
    "2": "is",
    "3": "sai rồi"
  }
}
```

`answers` là map: `question_id (string) → câu_trả_lời_của_user (string)`.

**Response — TestResultDetail:**
```json
{
  "id": 15,
  "user_id": 1,
  "test_type": "mixed",
  "start_date": "2026-07-01",
  "end_date": "2026-07-08",
  "questions": [
    {
      "id": 1,
      "type": "multiple_choice",
      "question": "What is the meaning of 'serendipity'?",
      "options": ["sự tình cờ may mắn", "sự thất vọng", "sự ngạc nhiên"],
      "word_audio": null,
      "answer": "sự tình cờ may mắn"
    }
  ],
  "answers": {
    "1": "sự tình cờ may mắn",
    "2": "is",
    "3": "sai rồi"
  },
  "total_questions": 3,
  "correct_answers": 2,
  "score": 66.7,
  "results": {
    "1": {
      "correct": true,
      "user_answer": "sự tình cờ may mắn",
      "correct_answer": "sự tình cờ may mắn"
    },
    "2": {
      "correct": true,
      "user_answer": "is",
      "correct_answer": "is"
    },
    "3": {
      "correct": false,
      "user_answer": "sai rồi",
      "correct_answer": "quyển sách"
    }
  }
}
```

**Lưu ý:** Sau khi submit, `questions` trả về KÈM `answer` (để FE hiển thị kết quả).

**Error `400` (đã nộp rồi):**
```json
{
  "detail": "Bài kiểm tra này đã được nộp trước đó"
}
```

### GET `/tests/` — Lịch sử bài kiểm tra

**Query params:** `skip=0&limit=100`

Trả về `List[TestResult]`:
```json
[
  {
    "id": 15,
    "user_id": 1,
    "test_type": "mixed",
    "start_date": "2026-07-01",
    "end_date": "2026-07-08",
    "questions": [...],
    "answers": {"1": "..."},
    "total_questions": 15,
    "correct_answers": 12,
    "score": 80.0
  }
]
```

---

## 6. Static Files (Audio / TTS)

- Base: `http://localhost:8000/static/`
- Audio files: `GET /static/audio/{uuid}.mp3`
- Được mount tự động khi server start.
- FE có thể dùng trực tiếp `<audio src="/static/audio/abc123.mp3" controls />`.

---

## 7. Sơ đồ Luồng Dữ Liệu

```
┌──────────────────────────────────────────────────────────────┐
│                     VISIONNEST API                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────┐   ┌───────────┐   ┌──────────────────┐        │
│  │  AUTH    │   │  USERS    │   │   AI (vocab +    │        │
│  │  /auth   │   │  /users   │   │   grammar)       │        │
│  │          │   │           │   │   /ai            │        │
│  │ login    │   │ CRUD      │   │                  │        │
│  │ JWT      │   │ grammar-  │   │ lookup-word      │        │
│  └──────────┘   │ level     │   │ vocabulary       │        │
│                 └───────────┘   │ grammar/*        │        │
│                                 └──────────────────┘        │
│                                                              │
│  ┌──────────────────┐   ┌──────────────────┐                 │
│  │  TESTS           │   │  STATIC          │                 │
│  │  /tests          │   │  /static         │                 │
│  │                  │   │                  │                 │
│  │ generate         │   │ audio/*.mp3     │                 │
│  │ submit           │   │ (TTS files)     │                 │
│  │ list             │   └──────────────────┘                 │
│  └──────────────────┘                                        │
└──────────────────────────────────────────────────────────────┘

         ▲              ▲              ▲              ▲
         │              │              │              │
    ┌────┴────┐   ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
    │  Auth   │   │  CRUD   │   │  Word   │   │  Test   │
    │  Guard  │   │  Users  │   │  + TTS  │   │ Engine  │
    └─────────┘   └─────────┘   └─────────┘   └─────────┘
```

---

## 8. Important Notes cho FE Developer

### Authentication Flow
1. User đăng nhập → lưu `access_token` vào `localStorage` hoặc `httpOnly cookie`
2. Mỗi request gắn header `Authorization: Bearer <token>`
3. Token hết hạn → redirect về login
4. Không có refresh token (hiện tại) — cần re-login

### Loading & Error States
- **POST /ai/lookup-word**: có thể mất 5-15 giây (gọi AI). Cần loading spinner + timeout message.
- **POST /ai/grammar/generate**: tương tự, 5-15 giây.
- **POST /tests/generate**: ~5-15 giây.
- Tất cả endpoint auth: nếu 401 → redirect login.
- Các lỗi 400, 409, 502, 500 đều trả về `{ "detail": "message" }`.

### Date Format
- Luôn dùng `YYYY-MM-DD` (ISO 8601).
- `learned_date` trong Vocabulary mặc định là ngày hiện tại.

### i18n / Multi-language
- `preferred_language` field trong User: `"vi"` (mặc định), `"en"`, `"zh"`, `"ja"`, `"ko"`.
- AI trả về definitions, examples bằng ngôn ngữ tương ứng.
- TTS hỗ trợ 5 ngôn ngữ.
- Error messages từ backend bằng tiếng Việt.

### Grammar Learning Flow (quan trọng)

```
User set level (A1/B1/...)
        │
        ▼
GET /grammar/today
        │
        ├── review ≠ null → hiển thị bài cần ôn
        │       │
        │       └── PATCH /grammar/lessons/{id} { is_reviewed: true }
        │
        └── new ≠ null → hiển thị topic mới
                │
                ▼
        POST /grammar/generate { topic_id }
                │
                ▼
        Hiển thị bài học (explanation + examples + exercises)
                │
                ▼
        PATCH /grammar/lessons/{id} { is_completed: true, score: 80 }
                │
                ▼
        GET /grammar/today (ngày hôm sau → review bài này)
```

### Test Engine Flow

```
Chọn khoảng ngày (DatePicker)
        │
        ▼
POST /tests/generate { start_date, end_date }
        │
        ▼
Hiển thị 15 câu hỏi (mỗi câu có id, type, question, options)
  - multiple_choice → radio buttons
  - fill_in_blank → text input
  - listening → audio player + options
        │
        ▼
User điền hết → click "Nộp bài"
        │
        ▼
POST /tests/{id}/submit { answers: { "1": "A", "2": "is", ... } }
        │
        ▼
Hiển thị kết quả chi tiết (results map với correct/incorrect)
```

### Pagination Convention
- `skip=0` (offset) + `limit=100` (default)
- Frontend tự implement infinite scroll hoặc "Load more"

### CORS
- Backend cho phép tất cả origins (`*`).
- OK cho development (localhost:5173, localhost:3000, etc.).
- Production: cần restrict.

---

## 9. Summary Endpoints Table

| Method | Path | Auth | Mô tả | Thời gian |
|--------|------|------|-------|-----------|
| POST | `/auth/login` | No | Đăng nhập | Nhanh |
| POST | `/users/` | No (rate-limited) | Đăng ký | Nhanh |
| GET | `/users/me` | Yes | Profile | Nhanh |
| GET/PATCH/DELETE | `/users/{id}` | Yes | CRUD user | Nhanh |
| PATCH | `/users/me/grammar-level` | Yes | Set trình độ | Nhanh |
| POST | `/ai/lookup-word` | Yes | Thêm từ mới (có IPA) | 5-15s |
| GET | `/ai/vocabulary` | Yes | DS từ vựng (sắp xếp theo ngày) | Nhanh |
| DELETE | `/ai/vocabulary/{id}` | Yes | Xoá từ | Nhanh |
| PATCH | `/ai/vocabulary/{id}/toggle-important` | Yes | Đánh dấu quan trọng | Nhanh |
| GET | `/ai/grammar/curriculum` | Yes | DS chủ điểm ngữ pháp | Nhanh |
| GET | `/ai/grammar/today` | Yes | Kế hoạch hôm nay | Nhanh |
| GET | `/ai/grammar/next` | Yes | Topic tiếp theo | Nhanh |
| POST | `/ai/grammar/generate` | Yes | Sinh bài học | 5-15s |
| PATCH | `/ai/grammar/lessons/{id}` | Yes | Cập nhật bài học | Nhanh |
| GET | `/ai/grammar/lessons` | Yes | LS bài học | Nhanh |
| POST | `/tests/generate` | Yes | Sinh đề | 5-15s |
| POST | `/tests/{id}/submit` | Yes | Nộp bài | Nhanh |
| GET | `/tests/` | Yes | LS bài kiểm tra | Nhanh |

---

*Last updated: 2026-07-08*
