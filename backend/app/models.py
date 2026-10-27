"""Database tables (SQLAlchemy ORM models).

What is persisted, and what deliberately is not:

  users            — accounts (email + hashed password; never plaintext)
  story_progresses — ONE active playthrough per user per story
  story_events     — an append-only log: every choice the player made,
                     the scene it happened in, and the variables after
  characters & story node definitions STAY in Python code (app/data/)
  because they are authored content, versioned with the codebase —
  like source code, not user data. Moving them to the DB later is
  optional and touches only app/data/.
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import JSON, Boolean, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _uuid() -> str:
    return uuid.uuid4().hex


def _now() -> datetime:
    return datetime.now(UTC)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(50))
    hashed_password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    progress: Mapped[list["StoryProgress"]] = relationship(back_populates="user")


class StoryProgress(Base):
    __tablename__ = "story_progresses"
    __table_args__ = (
        # One active playthrough per user per story.
        UniqueConstraint("user_id", "story_id", name="uq_user_story"),
    )

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    story_id: Mapped[str] = mapped_column(String(64), index=True)
    node_id: Mapped[str] = mapped_column(String(64))
    # Relationship variables: {"trust": n, "playfulness": n, "openness": n}
    vars: Mapped[dict] = mapped_column(JSON, default=dict)
    finished: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_now, onupdate=_now
    )

    user: Mapped[User] = relationship(back_populates="progress")
    events: Mapped[list["StoryEvent"]] = relationship(back_populates="progress")


class StoryEvent(Base):
    """One row per player choice — the raw material for the future
    memory scrapbook and relationship timeline."""

    __tablename__ = "story_events"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_uuid)
    progress_id: Mapped[str] = mapped_column(
        ForeignKey("story_progresses.id"), index=True
    )
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    story_id: Mapped[str] = mapped_column(String(64), index=True)
    node_id: Mapped[str] = mapped_column(String(64))  # scene it happened in
    choice_id: Mapped[str] = mapped_column(String(64))  # what was picked
    chapter: Mapped[int] = mapped_column(Integer)
    # Variables AFTER the choice was applied (snapshot).
    vars_after: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_now)

    progress: Mapped[StoryProgress] = relationship(back_populates="events")
