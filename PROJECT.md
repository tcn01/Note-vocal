# NoteVocal - Tổng quan dự án

## 1. Mục tiêu
Xây dựng ứng dụng web học ngôn ngữ (Anh/Trung) với AI, hỗ trợ nhập từ mới tự động tra cứu, sinh ngữ pháp theo lộ trình IELTS hàng ngày, và bài test hỗn hợp.

## 2. Công nghệ chính
- **Backend**: FastAPI (Python 3.11+), SQLAlchemy 2.0 (async), PostgreSQL, Redis (cache + Celery broker).
- **AI**: OpenRouter (Gemma 4, Gemini 2.0 Flash, Qwen3 Next, Llama 3.3...), Google Cloud TTS.
- **Frontend**: React + TypeScript + Tailwind, React Query, i18next.
- **DevOps**: Docker Compose, GCP (Cloud Run, Cloud SQL, Cloud Storage).
- **Scheduler**: Celery Beat chạy daily grammar generation.

## 3. Kiến trúc Clean (3 lớp)
```
Router (API endpoints) → Service (business logic) → Repository (DB queries)
Frontend: Container/Presentation pattern + Custom hooks
```

## 4. Tính năng chính
| Tính năng | Mô tả |
|---|---|
| **Quản lý từ vựng** | Nhập từ → AI trả về định nghĩa, phát âm, câu ví dụ, đồng nghĩa, mẹo nhớ. Hỗ trợ Anh và Trung. |
| **Ngữ pháp hàng ngày** | Tự động sinh bài học mới theo lộ trình IELTS (12 chủ đề A2→B2), kèm giải thích, ví dụ, bài tập. |
| **Bài test hỗn hợp** | Chọn khoảng ngày → AI sinh đề (trắc nghiệm, điền từ, nghe). Chấm điểm tự động. |
| **Đa ngôn ngữ UI** | Chuyển đổi giữa Việt, Anh, Trung. |
| **Xác thực JWT** | Đăng ký, đăng nhập, rate limiting. |

## 5. Cấu trúc backend (hiện tại)

```
VisionNest/
├── app/                    # Backend (FastAPI)
├── frontend/               # Frontend (React + TypeScript)
├── tests/                  # Backend tests
├── ARCHITECTURE.md         # Sơ đồ kiến trúc (cập nhật khi có thay đổi)
├── requirements.txt
├── README.md
└── PROJECT.md              # (file này)
```

> Xem chi tiết từng layer, database schema, và luồng request tại **`ARCHITECTURE.md`**.

## 6. Quy trình phát triển (Vibe Code)
1. AI đọc `PROJECT.md` để nắm tổng thể.
2. Làm từng phase: Setup → Database → Auth → OpenRouter → Vocab → Celery → TestEngine → Frontend.
3. Kiểm tra code, chạy thử, fix lỗi nếu có.
4. Đánh dấu hoàn thành phase trước khi chuyển tiếp.

## 7. Lưu ý
- **OpenRouter**: Cơ chế fallback giữa các model free khi bị rate limit.
- **Google TTS**: File MP3 lưu lên GCP Storage hoặc local.
- **Database**: Composite unique key (`user_id`, `word`, `language`) tránh trùng từ.
- **Celery**: Worker và Beat chạy container riêng.
- **Bảo mật**: bcrypt cho password, JWT expiry, không lộ secret.

## 8. Chủ sở hữu
- Dự án: NoteVocal
- Ngày tạo: 2026-07-05
