# AIHR — AI-Powered Recruitment Platform

> **Language / 语言**: English | [简体中文](./README_zh.md)

An AI-driven intelligent recruitment management system supporting resume parsing, smart screening, interview question generation, and AI semantic search. Supports both cloud API and local Ollama AI integration.

For a high-level overview of the system design, see [AIHR Technical Architecture](./AIHR_技术架构图.md) and the [simplified architecture diagram](./AIHR_技术架构图_简版.png).

## Tech Stack

### Backend
- **Framework**: FastAPI + Uvicorn
- **Database**: SQLite + SQLAlchemy
- **Async Tasks**: Celery + Redis
- **AI Integration**: OpenAI-compatible API (supports SiliconFlow, OpenAI, local Ollama, etc.)
- **Vector Search**: NumPy cosine similarity + JSON file persistence (lightweight in-house implementation)
- **File Processing**: pdfplumber, python-docx, reportlab

### Frontend
- **Framework**: React 18 + TypeScript
- **UI Components**: Ant Design 5
- **Routing**: React Router 6
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Build Tool**: Vite

## Feature Modules

| Module | Description |
|--------|-------------|
| Dashboard | Recruitment data statistics dashboard |
| Job Management | Job posting, editing, status management |
| Resume Management | Resume import (PDF/DOCX), AI parsing, status flow |
| AI Resume Search | RAG-based semantic search, find candidates via natural language |
| Matching Center | Resume screening & scoring, interview question generation |
| Interview Questions | Question viewing, PDF/DOCX export |
| Prompt Management | Prompt template version management |
| LLM Management | LLM configuration (chat model + embedding model), API Key encrypted storage, Token usage tracking |

## AI Resume Search (RAG)

A standalone semantic search feature that implements intelligent resume retrieval via RAG (Retrieval-Augmented Generation).

### Technical Approach
- **Embedding Model**: Configure the embedding model via the "LLM Management" menu (supports SiliconFlow, OpenAI, local Ollama, or any OpenAI-compatible API)
- **Vector Storage**: NumPy cosine similarity + JSON file persistence
- **No vector database used** (ChromaDB was deprecated due to Python 3.14 compatibility issues)
- **No LangChain framework** (calls OpenAI-compatible API directly)

### Configuration
The Embedding model supports two configuration methods, in order of priority:
1. **Database configuration (recommended)**: Create an "embedding model" type config on the "LLM Management" page, set API Key, Base URL, and model name; takes effect automatically once enabled
2. **Environment variable fallback**: If no active embedding config exists in the database, uses `EMBEDDING_*` settings from `.env`

### Workflow
1. **Build Index**: Concatenate structured data of all successfully parsed resumes into natural-language text, call the Embedding API to generate vectors, and persist to a local JSON file
2. **Semantic Search**: User enters a natural-language query → generate query vector → compute cosine similarity against all resume vectors → return Top-K matches (with match scores)
3. **Auto Vectorization**: Automatically calls vector storage after a resume is successfully parsed — no manual action required

## Quick Start

### Requirements
- Python 3.10+ (verified with Python 3.14)
- Node.js 18+ (verified with Node.js 24)
- Redis (required for Celery async tasks)
- Ollama (optional, for local AI mode)

### 1. Install Redis

**Windows (winget recommended):**
```bash
winget install taizod1024.redis-windows-fork
```

**Other methods:** See [Redis Windows port](https://github.com/redis-windows/redis-windows)

Start the Redis service:
```bash
redis-server --port 6379
```

### 2. Install Ollama (Local AI Mode)

To use local AI features (no cloud API costs), install Ollama and pull models:

```bash
# Install Ollama: https://ollama.com/download
# Pull the chat model (qwen2.5:3b recommended for 8GB RAM)
ollama pull qwen2.5:3b
# Pull the embedding model
ollama pull qwen3-embedding:8b
```

> **Memory recommendation**: 8GB RAM — 3B chat model + 8B embedding model; 16GB+ RAM — 7B chat model.

### 3. Start the Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Generate keys and configure environment variables (choose one)
# Option A: use the script (recommended)
generate_keys.bat

# Option B: generate manually
python -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))" >> .env
python -c "import secrets; print('ENCRYPTION_KEY=' + secrets.token_urlsafe(32))" >> .env

# Edit .env to configure Embedding model and other params (see environment variables below)

# Start the API service (use python -m, do not call uvicorn directly)
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Start the Celery Worker (new terminal)
celery -A app.tasks worker --loglevel=info --pool=solo
```

> **Note**: The Celery startup command uses `-A app.tasks` (not `-A app.core.celery_app`) to ensure async tasks are registered correctly.
>
> **First run**: The system does not auto-create an admin account. On first startup the backend will auto-create database tables and 3 default prompts. To create an admin user:
> ```bash
> python -c "from app.db.session import SessionLocal; from app.models import User; from app.core.security import get_password_hash; db = SessionLocal(); u = User(username='admin', password_hash=get_password_hash('your-strong-password')); db.add(u); db.commit()"
> ```

### 4. Start the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server
npm run dev
```

Open http://localhost:5173 to use the app.

### One-Click Start (Windows)

Double-click `backend/start_all.bat` to start Redis (with check), backend API, Celery Worker, and frontend in order. The script auto-detects whether `.env` exists and keys are configured.

### Environment Variables

Main backend `.env` settings:

```env
# JWT secret (required, generate with the command above)
SECRET_KEY=

# Token expiration (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
DATABASE_URL=sqlite:///./hr_ai.db

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1

# API Key encryption key (required, generate with the command above)
ENCRYPTION_KEY=

# Embedding (AI search; can be omitted once configured in the database)
# Cloud API example:
EMBEDDING_API_KEY=your-api-key
EMBEDDING_BASE_URL=https://api.siliconflow.cn/v1
EMBEDDING_MODEL=Qwen/Qwen3-VL-Embedding-8B

# Local Ollama example:
# EMBEDDING_API_KEY=ollama
# EMBEDDING_BASE_URL=http://localhost:11434/v1
# EMBEDDING_MODEL=qwen3-embedding:8b
```

## LLM Configuration

The system supports two AI integration methods, switchable on the "LLM Management" page:

### Cloud API
- **Providers**: SiliconFlow, OpenAI, DeepSeek, Zhipu, or any OpenAI-compatible API
- **Pros**: Fast response, strong model capabilities
- **Cons**: Paid, depends on network

### Local Ollama
- **Configuration**: Set Base URL to `http://localhost:11434/v1` and API Key to `ollama` (placeholder)
- **Pros**: Free, data stays on your machine, works offline
- **Cons**: Slower response (hardware-dependent), requires more memory
- **Recommended models**:
  - Chat model: `qwen2.5:3b` (8GB RAM) or `qwen2.5:7b` (16GB+ RAM)
  - Embedding model: `qwen3-embedding:8b`

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/v1/auth/login` | User login |
| GET | `/api/v1/dashboard/stats` | Dashboard statistics |
| GET/POST/PUT/DELETE | `/api/v1/jobs` | Job management |
| GET/POST | `/api/v1/resumes` | Resume management |
| POST | `/api/v1/resumes/import` | Resume import |
| POST | `/api/v1/ai-search` | AI semantic search |
| POST | `/api/v1/ai-search/index` | Build search index |
| POST | `/api/v1/matching/{id}/score` | Resume scoring |
| POST | `/api/v1/interviews/{id}/generate` | Generate interview questions |
| GET | `/api/v1/interviews/{id}/download/pdf` | Download questions as PDF |
| GET | `/api/v1/interviews/{id}/download/docx` | Download questions as DOCX |
| GET/POST/PUT | `/api/v1/prompts` | Prompt management |
| GET/POST/PUT/DELETE | `/api/v1/llm-configs` | LLM configuration management |

Full API docs: after starting the backend, visit http://localhost:8000/docs

## Project Structure

```
AIHR/
├── backend/
│   ├── app/
│   │   ├── api/                # API routes
│   │   │   ├── ai_search.py    # AI search endpoints
│   │   │   ├── apply.py        # Application endpoints
│   │   │   ├── auth.py         # Auth endpoints
│   │   │   ├── dashboard.py    # Dashboard endpoints
│   │   │   ├── interviews.py   # Interview question endpoints
│   │   │   ├── jobs.py         # Job endpoints
│   │   │   ├── llm_configs.py  # LLM config endpoints
│   │   │   ├── matching.py     # Matching/scoring endpoints
│   │   │   ├── prompts.py      # Prompt endpoints
│   │   │   └── resumes.py      # Resume endpoints
│   │   ├── core/               # Core configuration
│   │   │   ├── celery_app.py   # Celery configuration
│   │   │   ├── config.py       # App config (with startup validation)
│   │   │   └── security.py     # JWT / API Key encryption
│   │   ├── db/                 # Database session
│   │   ├── models/             # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   ├── services/
│   │   │   └── vector_store.py # Vector store service (NumPy-based)
│   │   └── tasks/              # Celery async tasks
│   │       └── __init__.py     # parse_resume / score_resume / generate_interview
│   ├── chroma_db/              # Vector persistence directory (JSON)
│   ├── downloads/              # Exported files directory
│   ├── uploads/                # Uploaded files directory
│   ├── .env                    # Environment variables
│   ├── .env.example            # Environment variable template
│   ├── generate_keys.bat       # Key generation script
│   ├── start_all.bat           # One-click startup script
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/                # API call layer
│   │   ├── components/         # Shared components
│   │   ├── pages/              # Page components
│   │   │   ├── AiSearch/           # AI resume search
│   │   │   ├── Apply/              # Application management
│   │   │   ├── Dashboard/          # Dashboard
│   │   │   ├── InterviewQuestions/ # Interview question management
│   │   │   ├── Jobs/               # Job management
│   │   │   ├── LLMConfigs/         # LLM management
│   │   │   ├── Login/              # Login
│   │   │   ├── MatchingCenter/     # Matching center
│   │   │   ├── Prompts/            # Prompt management
│   │   │   ├── ResumeDetail/       # Resume detail
│   │   │   ├── ResumeImport/       # Resume import
│   │   │   └── Resumes/            # Resume management
│   │   ├── router/             # Routing
│   │   ├── stores/             # State management (Zustand)
│   │   └── types/              # TypeScript types
│   └── package.json
└── README.md
```

## Security Notes

Before deploying to production, note the following:

- **`SECRET_KEY`** and **`ENCRYPTION_KEY`** are required with no defaults. The app will refuse to start with a clear error message if not configured. Generate random keys with `secrets.token_urlsafe(32)`.
- **Admin account** is not auto-created; create it manually via the command line with a strong password.
- **CORS** only allows `http://localhost:5173` (frontend dev server) by default. Update to your actual domain in production.
- **Uploaded resume files** may contain personal sensitive information — do not commit to version control (excluded in `.gitignore`).
- **Database files** (`.db`) and **Redis snapshots** (`.rdb`) are also excluded in `.gitignore`.

## Troubleshooting

### Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| `RuntimeError: SECRET_KEY is not set` on startup | `.env` keys empty or not configured | Run `generate_keys.bat` or fill in `.env` manually |
| `uvicorn: command not found` | uvicorn not in PATH | Use `python -m uvicorn` instead |
| Frontend 404 loading favicon | `vite.svg` missing | Reference already removed |
| Blank page after login | Backend not running or port mismatch | Confirm backend runs on port 8000 and the frontend dev server proxy is configured |
| Celery tasks not executing | Celery Worker not started | Run `celery -A app.tasks worker --loglevel=info --pool=solo` in a new terminal |
| Vector search returns empty results | Embedding model not configured | Configure an embedding model on the "LLM Management" page, or rebuild the index |

### Standard Startup Flow After a Fresh Clone

1. `cp backend/.env.example backend/.env` (or copy and edit manually)
2. Run `generate_keys.bat` to generate `SECRET_KEY` and `ENCRYPTION_KEY`
3. Edit `.env` to configure the Embedding model (cloud or local Ollama)
4. `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload`
5. Create the admin user (see command above)
6. `cd frontend && npm run dev`

## License

MIT
