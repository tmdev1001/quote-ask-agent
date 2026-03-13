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

### Database and migrations (Phase 2)

The app uses **SQLAlchemy 2** and **Alembic**. The default database is SQLite (file under `./data/lyra.db`). Ensure the `data` directory exists so the SQLite file can be created.

1. **Create the database directory** (if using default SQLite path):

```bash
mkdir data
```

2. **Run migrations**:

```bash
alembic upgrade head
```

Migrations use a sync driver derived from your `DATABASE_URL` (e.g. `sqlite:///./data/lyra.db` for local). To switch to PostgreSQL later, set `DATABASE_URL` to a `postgresql+asyncpg://...` URL; Alembic will use the corresponding sync URL for migrations.

3. **Create a new migration** after changing models:

```bash
alembic revision --autogenerate -m "describe your change"
alembic upgrade head
```

