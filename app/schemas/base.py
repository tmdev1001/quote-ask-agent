from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ORMBaseModel(BaseModel):
    """Base Pydantic model configured to work with SQLAlchemy models."""

    model_config = ConfigDict(from_attributes=True)


class TimestampedModel(ORMBaseModel):
    """Common created/updated timestamp fields."""

    created_at: datetime
    updated_at: datetime

