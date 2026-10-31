from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def uid() -> str:
    return str(uuid4())


def now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), default="Local learner")


class ResearchDocument(Base):
    __tablename__ = "research_documents"
    name: Mapped[str] = mapped_column(String(150), primary_key=True)
    version: Mapped[str] = mapped_column(String(50))
    digest: Mapped[str] = mapped_column(String(64))
    data: Mapped[dict] = mapped_column(JSON)


class ResearchRecord(Base):
    __tablename__ = "research_records"
    id: Mapped[str] = mapped_column(String(150), primary_key=True)
    kind: Mapped[str] = mapped_column(String(30), index=True)
    document_name: Mapped[str] = mapped_column(ForeignKey("research_documents.name"))
    data: Mapped[dict] = mapped_column(JSON)


class Plan(Base):
    __tablename__ = "plans"
    id: Mapped[str] = mapped_column(String(100), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    track_id: Mapped[str] = mapped_column(ForeignKey("research_records.id"))
    title: Mapped[str] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="active")
    config: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class PlanLesson(Base):
    __tablename__ = "plan_lessons"
    __table_args__ = (UniqueConstraint("plan_id", "sequence"), CheckConstraint("day >= 1"))
    id: Mapped[str] = mapped_column(String(100), primary_key=True, default=uid)
    plan_id: Mapped[str] = mapped_column(ForeignKey("plans.id", ondelete="CASCADE"), index=True)
    research_id: Mapped[str | None] = mapped_column(ForeignKey("research_records.id"), nullable=True)
    sequence: Mapped[int] = mapped_column(Integer)
    day: Mapped[int] = mapped_column(Integer)
    skipped: Mapped[bool] = mapped_column(Boolean, default=False)
    data: Mapped[dict] = mapped_column(JSON)


class Progress(Base):
    __tablename__ = "progress"
    slot_id: Mapped[str] = mapped_column(ForeignKey("plan_lessons.id", ondelete="CASCADE"), primary_key=True)
    video: Mapped[bool] = mapped_column(Boolean, default=False)
    reading: Mapped[bool] = mapped_column(Boolean, default=False)
    practical: Mapped[bool] = mapped_column(Boolean, default=False)
    knowledge: Mapped[bool] = mapped_column(Boolean, default=False)
    watched_minutes: Mapped[int] = mapped_column(Integer, default=0)
    study_minutes: Mapped[int] = mapped_column(Integer, default=0)
    evidence: Mapped[str] = mapped_column(Text, default="")
    answers: Mapped[dict] = mapped_column(JSON, default=dict)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    __table_args__ = (
        CheckConstraint("watched_minutes >= 0 AND watched_minutes <= 1440"),
        CheckConstraint("study_minutes >= 0 AND study_minutes <= 1440"),
    )


class PersonalRecord(Base):
    __tablename__ = "personal_records"
    __table_args__ = (
        UniqueConstraint("user_id", "kind", "ref_key"),
        CheckConstraint(
            "kind IN ('note','resource','competency','company','job','project','attempt','review','settings')"
        ),
    )
    id: Mapped[str] = mapped_column(String(100), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), index=True)
    kind: Mapped[str] = mapped_column(String(30), index=True)
    ref_key: Mapped[str | None] = mapped_column(String(150), nullable=True)
    research_ref: Mapped[str | None] = mapped_column(ForeignKey("research_records.id"), nullable=True)
    parent_id: Mapped[str | None] = mapped_column(ForeignKey("personal_records.id"), nullable=True)
    data: Mapped[dict] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=now)


class StudyActivity(Base):
    __tablename__ = "study_activity"
    slot_id: Mapped[str] = mapped_column(ForeignKey("progress.slot_id", ondelete="CASCADE"), primary_key=True)
    day: Mapped[str] = mapped_column(String(10), primary_key=True)
    minutes: Mapped[int] = mapped_column(Integer)


class ImportPreview(Base):
    __tablename__ = "import_previews"
    id: Mapped[str] = mapped_column(String(100), primary_key=True, default=uid)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    kind: Mapped[str] = mapped_column(String(30))
    data: Mapped[dict] = mapped_column(JSON)
    digest: Mapped[str] = mapped_column(String(64))
    applied: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
