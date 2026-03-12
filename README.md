## Lyra Quote Ask Agent (PoC)

Backend-first proof-of-concept for a **Telegram-first AI quote intake agent** for auto insurance.

This Phase 1 scaffold provides:
- FastAPI application bootstrapping
- `/health` endpoint
- Pydantic v2 settings loading from `.env`
- Async SQLAlchemy 2.x engine/session setup (SQLite by default)
- Structured logging via `structlog`

### Setup

1. Create your virtual environment (if not already created):

```bash
python -m venv .venv
```

2. Activate the environment:

```bash
# PowerShell
.\.venv\Scripts\Activate.ps1
```

3. Install dependencies:

```bash
pip install .
```

4. Copy `.env.example` to `.env` and adjust if needed:

```bash
cp .env.example .env
```

### Run the app

```bash
uvicorn app.main:app --reload
```

Then open `http://localhost:8000/health` to verify the service is running.

