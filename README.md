## Lyra Quote Ask Agent (PoC)

Backend-first proof-of-concept for a **Telegram-first AI quote intake agent** for auto insurance.

### Quickstart

```bash
uvicorn app.main:app --reload
```

The app uses:
- FastAPI
- OpenAI Agents SDK
- SQLAlchemy 2.x
- Alembic
- SQLite (dev) with PostgreSQL-compatible models

