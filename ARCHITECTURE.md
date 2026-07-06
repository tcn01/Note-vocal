# VisionNest — Kiến trúc dự án

> File này được cập nhật mỗi khi có thay đổi cấu trúc project.

---

## 1. Tổng quan

```
VisionNest/
├── app/               # Backend (FastAPI + PostgreSQL)
├── frontend/          # Frontend (React + TypeScript + Tailwind)
├── tests/             # Backend tests
├── PROJECT.md         # Tổng quan dự án
├── ARCHITECTURE.md    # (file này) Sơ đồ kiến trúc
└── README.md
```

---

## 2. Backend Flow

```mermaid
graph TB
    Client["Browser / Mobile"] -->|HTTP| FastAPI

    subgraph Backend["app/"]
        Main["main.py<br/>app = FastAPI()<br/>CORS + lifespan"]
        Router["api/v1/router.py"]

        subgraph Endpoints["api/v1/endpoints/"]
            AuthEP["auth.py<br/>POST /login"]
            UsersEP["users.py<br/>CRUD users"]
        end

        subgraph Core["core/"]
            Config["config.py<br/>Settings"]
            Security["security.py<br/>JWT + bcrypt"]
            DB["database.py<br/>AsyncSession"]
        end

        subgraph Services["services/"]
            UserSvc["user_service.py"]
        end

        subgraph Repos["repositories/"]
            BaseRepo["base_repository.py<br/>Generic CRUD"]
            UserRepo["user_repository.py"]
        end

        subgraph Models["models/"]
            UserModel["user.py"]
            VocabModel["vocabulary.py"]
            GrammarModel["grammar.py"]
            TestModel["test_result.py"]
        end

        subgraph Migrations["migrations/"]
            EnvPy["env.py"]
            Versions["versions/*.py"]
        end

        subgraph Schemas["schemas/"]
            UserSchema["user.py"]
            AuthSchema["auth.py"]
            VocabSchema["vocabulary.py"]
            GrammarSchema["grammar.py"]
            TestSchema["test_result.py"]
        end
    end

    PostgreSQL[("PostgreSQL")]

    Main --> Router
    Router --> AuthEP & UsersEP
    AuthEP --> UserSvc
    UsersEP --> UserSvc
    UserSvc --> UserRepo
    UserRepo -.-> BaseRepo
    UserRepo --> UserModel
    AuthEP --> Security
    UsersEP --> Security
    Security --> Config
    DB --> Config
    BaseRepo --> DB
    DB --> PostgreSQL
    EnvPy --> Models
    EnvPy --> DB
```

---

## 3. Frontend Flow

```mermaid
graph TB
    subgraph Frontend["frontend/"]
        MainTSX["main.tsx<br/>ReactDOM + QueryClient + BrowserRouter"]
        App["App.tsx<br/>MainLayout + AppRouter"]
        Routes["routes/index.tsx"]

        subgraph Pages["pages/"]
            Home["HomePage.tsx"]
            Login["LoginPage.tsx"]
        end

        subgraph Hooks["hooks/"]
            UseAuth["useAuth.ts<br/>React Query"]
        end

        subgraph Api["api/"]
            Client["client.ts<br/>Axios + interceptors"]
            AuthAPI["auth.ts"]
            VocabAPI["vocabulary.ts"]
        end

        subgraph I18n["i18n/"]
            Config["config.ts"]
            Vi["locales/vi.json"]
            En["locales/en.json"]
            Zh["locales/zh.json"]
        end

        subgraph Types["types/"]
            Index["index.ts"]
        end

        Layout["components/layout/MainLayout.tsx"]
    end

    MainTSX --> App
    App --> Layout
    App --> Routes
    Routes --> Home & Login
    Login --> UseAuth
    UseAuth --> AuthAPI
    VocabAPI --> Client
    AuthAPI --> Client
```

---

## 4. Database Schema

```mermaid
erDiagram
    User ||--o{ Vocabulary : has
    User ||--o{ GrammarLesson : has
    User ||--o{ TestResult : has

    User {
        int id PK
        string email UK
        string hashed_password
        string name
        enum preferred_language
        bool is_active
        datetime created_at
    }

    Vocabulary {
        int id PK
        int user_id FK
        string word
        enum language
        json definitions
        string pronunciation_url
        json examples
        json synonyms
        text memory_tip
        date learned_date
        UQ user_id_word_lang
    }

    GrammarLesson {
        int id PK
        int user_id FK
        string topic
        enum level
        text explanation
        json examples
        json exercises
        date generated_date
        bool is_completed
        bool is_quiz_taken
        float score
    }

    TestResult {
        int id PK
        int user_id FK
        string test_type
        date start_date
        date end_date
        int total_questions
        int correct_answers
        float score
    }
```

---

## 5. Kiến trúc Backend (Clean 3-layer)

```
HTTP Request
    → Router (endpoints/)       — Xác thực, validate, routing
        → Service (services/)   — Business logic, orchestration
            → Repository (repositories/) — CRUD, DB queries
                → Model (models/) — SQLAlchemy ORM mapping
```

- **Router** không chứa logic — chỉ gọi Service, trả response
- **Service** chứa business logic — không biết DB
- **Repository** chỉ thao tác DB — không biết logic

---

## 6. Luồng request ví dụ

```mermaid
sequenceDiagram
    Client->>+Router: POST /api/v1/auth/login
    Router->>+Service: user_service.authenticate()
    Service->>+Repository: user_repository.get_by_email()
    Repository->>+DB: SELECT * FROM users WHERE email=?
    DB-->>-Repository: User row
    Repository-->>-Service: User object
    Service->>Service: verify_password()
    Service-->>-Router: User
    Router->>Router: create_access_token()
    Router-->>-Client: { access_token: "..." }
```

---

> ⚠️ **Ghi chú**: Khi thêm/sửa/xóa models, endpoints, services, hoặc cấu trúc thư mục, hãy cập nhật file `ARCHITECTURE.md` này tương ứng.
