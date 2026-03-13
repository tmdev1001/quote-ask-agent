"""
Mixin classes for timestamp columns.

SQLite-compatible; portable to PostgreSQL.
Uses Python-side defaults for SQLite compatibility.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class CreatedAtMixin:
    """Adds created_at (set on insert)."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        nullable=False,
    )


class UpdatedAtMixin:
    """Adds updated_at (set on insert/update)."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=_utc_now,
        onupdate=_utc_now,
        nullable=False,
    )


class TimestampMixin(CreatedAtMixin, UpdatedAtMixin):
    """Adds created_at and updated_at."""

    pass
