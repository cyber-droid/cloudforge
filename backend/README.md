# CloudForge Backend Service

Production-grade FastAPI backend for CloudForge — AI-assisted Cloud & DevOps learning platform.

## Architecture

- **Language**: Python 3.12+
- **Framework**: FastAPI (Async ASGI)
- **Database**: PostgreSQL 16
- **ORM & Migrations**: SQLAlchemy 2.0 (Async) + Alembic
- **Validation**: Pydantic v2 + Pydantic Settings
- **Security**: JWT (PyJWT) + Bcrypt Password Hashing
- **Testing**: Pytest + Pytest-AsyncIO + HTTPX AsyncClient
- **Containerization**: Docker & Docker Compose

## Directory Structure

```
backend/
├── alembic/              # Alembic database migration environment
│   ├── env.py            # Async engine migration hook
│   └── versions/         # Version migration revisions
├── app/
│   ├── api/              # API route controllers
│   │   └── v1/           # Versioned API routes & endpoints
│   ├── core/             # Configuration, async DB session, security utils
│   │   ├── config.py     # Pydantic v2 settings
│   │   ├── database.py   # SQLAlchemy async engine & sessionmaker
│   │   └── security.py   # Bcrypt hashing & PyJWT tokens
│   ├── models/           # SQLAlchemy 2.0 declarative database models
│   ├── repositories/     # Async repository pattern for DB access
│   ├── schemas/          # Pydantic v2 schemas for request/response validation
│   ├── services/         # Business logic layer
│   └── main.py           # FastAPI application entrypoint & middleware
├── tests/                # Async test suite
│   ├── conftest.py       # Test fixtures and SQLite in-memory engine
│   ├── test_health.py    # Health & readiness probe tests
│   └── test_security.py  # Password hashing & JWT tests
├── alembic.ini           # Alembic config
├── Dockerfile            # Container image build file
├── pyproject.toml        # Project metadata and test configuration
└── requirements.txt      # Python dependencies
```

## Quickstart

### 1. Start PostgreSQL with Docker Compose
```bash
docker compose up -d postgres
```

### 2. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 3. Run Migrations
```bash
alembic upgrade head
```

### 4. Start Development Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- Interactive Swagger UI: [http://localhost:8000/api/v1/docs](http://localhost:8000/api/v1/docs)
- Health Check: [http://localhost:8000/api/v1/healthz](http://localhost:8000/api/v1/healthz)

### 5. Run Test Suite
```bash
pytest -v
```
