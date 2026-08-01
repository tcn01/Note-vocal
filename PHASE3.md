# Phase 3: Core AI — OpenRouter Service (Xương sống)

## Mục tiêu
- Xây dựng OpenRouterService với cơ chế **fallback model** chuyên nghiệp
- Tích hợp **Function Calling** để ép kiểu dữ liệu đầu ra
- **Retry + exponential backoff** khi call API thất bại
- Parse JSON an toàn, không crash khi response lỗi

## Kiến trúc

### Luồng xử lý

```
Client/Frontend
     │
     ▼
Router (endpoints)
     │  POST /api/v1/ai/lookup-word
     │  POST /api/v1/ai/grammar
     │
     ▼
OpenRouterService
     │
     ├── lookup_word(word, lang)
     │       └── _call_openrouter(messages, tools)  ← retry x3, backoff
     │
     └── generate_grammar(topic, level)
             └── _call_openrouter(messages)
                     │
                     ▼
              ┌─────────────────────┐
              │  Model Priority     │
              │  1. gemma-4-31b-it  │  ← free
              │  2. phi-4           │  ← free (rate limit fallback)
              │  3. qwen2.5-7b      │  ← free (timeout fallback)
              └─────────────────────┘
                     │
                     ▼
              OpenRouter API
              (openrouter.ai/api/v1)
```

### Fallback chiến lược

| Bước | Model | Khi nào fallback |
|---|---|---|
| 1 | `google/gemma-4-31b-it:free` | Mặc định |
| 2 | `microsoft/phi-4:free` | Rate limit (429) hoặc model unavailable |
| 3 | `qwen/qwen2.5-7b-instruct:free` | Timeout hoặc tất cả model trên đều fail |

> **Ghi chú**: Model names có thể thay đổi theo thời gian. Kiểm tra danh sách free models tại [openrouter.ai/models](https://openrouter.ai/models) để cập nhật.

## Module: `app/services/openrouter_service.py`

### Class: `OpenRouterService`

```python
class OpenRouterService:
    BASE_URL = "https://openrouter.ai/api/v1"

    def __init__(self):
        # Đọc API_KEY từ settings
        # models_priority: list[ModelConfig] với retry rules
        # timeout: 30s mặc định

    async def _call_openrouter(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict | list | str:
        """
        Core method — tất cả các phương thức public đều gọi qua đây.
        - Retry tối đa 3 lần với exponential backoff (1s → 2s → 4s)
        - Fallback qua model tiếp theo trong danh sách
        - Parse response JSON an toàn
        """
```

### Phương thức public

| Method | Input | Output | Ghi chú |
|---|---|---|---|
| `lookup_word(word, language)` | word: str, language: str | `{ definitions, examples, synonyms, memory_tip }` | Dùng Function Calling |
| `generate_grammar(topic, level)` | topic: str, level: str | `{ explanation, examples[], exercises[] }` | Dùng system prompt |

### Retry & Backoff

```
Lần 1: chờ 1s  → nếu lỗi → model hiện tại retry
Lần 2: chờ 2s  → nếu lỗi → model hiện tại retry
Lần 3: chờ 4s  → nếu lỗi → fallback sang model tiếp theo
reset counter → retry với model mới (1s, 2s, 4s)
```

## File cần tạo

| File | Mô tả |
|---|---|
| `app/services/openrouter_service.py` | Service chính: fallback, retry, function calling |
| `app/schemas/ai.py` | Pydantic schemas cho request/response AI |
| `app/api/v1/endpoints/ai.py` | Router: lookup-word, generate-grammar |
| `tests/test_openrouter_service.py` | Unit tests (mock OpenRouter API) |

## Cập nhật

| File | Thay đổi |
|---|---|
| `app/api/v1/router.py` | Thêm router AI |
| `app/core/config.py` | Thêm `OPENROUTER_API_KEY` |
| `requirements.txt` | Thêm `httpx` (đã có) |

## Cấu trúc sau Phase 3

```
app/
├── api/
│   └── v1/
│       ├── endpoints/
│       │   ├── ai.py              ← NEW
│       │   ├── auth.py
│       │   └── users.py
│       └── router.py              ← add ai router
├── core/
│   ├── config.py                  ← add OPENROUTER_API_KEY
│   └── ...
├── schemas/
│   ├── ai.py                      ← NEW
│   └── ...
├── services/
│   ├── openrouter_service.py      ← NEW
│   └── user_service.py
└── tests/
    ├── test_openrouter_service.py ← NEW
    └── test_users.py
```

## Chi tiết kỹ thuật

### 1. System Prompt cho lookup_word

```json
{
  "role": "system",
  "content": "Bạn là trợ lý từ vựng. Trả về JSON hợp lệ với schema:
    definitions: [{ \"partOfSpeech\": \"string\", \"meaning\": \"string\", \"example\": \"string\" }],
    examples: [\"string\"],
    synonyms: [\"string\"],
    memory_tip: \"string\"
  Không thêm text nào ngoài JSON."
}
```

### 2. Function Calling cho lookup_word

Dùng `tools` parameter của OpenRouter (tương thích OpenAI API) để ép model trả về đúng cấu trúc.

### 3. System Prompt cho generate_grammar

```json
{
  "role": "system",
  "content": "Bạn là giáo viên ngữ pháp. Trả về JSON hợp lệ với schema:
    explanation: \"string\",
    examples: [{ \"sentence\": \"string\", \"translation\": \"string\" }],
    exercises: [{ \"question\": \"string\", \"options\": [\"string\"], \"answer\": \"string\" }]
  Không thêm text nào ngoài JSON."
}
```

### 4. JSON Parsing

```python
def _safe_parse(response_text: str) -> dict:
    try:
        # Loại bỏ markdown code blocks nếu có
        cleaned = response_text.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        return json.loads(cleaned.strip())
    except (json.JSONDecodeError, Exception):
        logger.error("Failed to parse AI response: %s", response_text[:200])
        return {}
```

### 5. Error Handling

- **HTTP 429** (Rate Limited) → fallback model tiếp theo
- **HTTP 408 / Timeout** → fallback model tiếp theo
- **HTTP 5xx** → retry với backoff
- **JSON parse fail** → trả về dict rỗng, không crash
- **Tất cả model đều fail** → trả về dict rỗng + log error

## Testing

```python
# test_openrouter_service.py
# Dùng httpx mock (respx hoặc pytest-httpx) để giả lập OpenRouter API

def test_lookup_word_success():
    """Mock response 200 + JSON hợp lệ → trả về dict đầy đủ"""

def test_lookup_word_fallback():
    """Model đầu 429 → fallback model 2 thành công"""

def test_lookup_word_all_fail():
    """Tất cả model đều 429 → trả về dict rỗng"""

def test_generate_grammar_success():
    """Mock response 200 → trả về đúng schema"""

def test_safe_parse_invalid_json():
    """Response không phải JSON → trả về dict rỗng"""

def test_safe_parse_markdown_json():
    """Response có ```json ``` block → parse được"""
```

## API Endpoints (Phase 3)

| Method | Endpoint | Auth | Mô tả |
|---|---|---|---|
| POST | `/api/v1/ai/lookup-word` | JWT | Tra từ điển AI |
| POST | `/api/v1/ai/grammar` | JWT | Sinh bài học ngữ pháp |

## Tài liệu tham khảo
- [OpenRouter API Docs](https://openrouter.ai/docs)
- [OpenRouter Free Models](https://openrouter.ai/models?order=pricing)

---

> ⚠️ **Lưu ý**: Model names (`gemma-4-31b-it`, `phi-4`, `qwen2.5-7b-instruct`) cần được verify trên OpenRouter docs trước khi deploy. Cập nhật vào `openrouter_service.py` nếu có thay đổi.
