"""PostgreSQL + pgvector persistence for resume-grounded retrieval.

This subsystem is deliberately separate from the legacy SQLite interview-history
store. Existing practice sessions continue to work while resume evidence moves
to PostgreSQL.
"""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Iterable

from sqlalchemy import DateTime, ForeignKey, String, Text, create_engine, select, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from pgvector.sqlalchemy import Vector

EMBEDDING_DIMENSION = 384
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://interviewiq:change-this-local-password@localhost:5432/interviewiq",
)


class Base(DeclarativeBase):
    pass


class ResumeDocument(Base):
    __tablename__ = "resume_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    candidate_name: Mapped[str] = mapped_column(String(120), nullable=False)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    chunks: Mapped[list["ResumeChunk"]] = relationship(
        back_populates="resume", cascade="all, delete-orphan"
    )


class ResumeChunk(Base):
    __tablename__ = "resume_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    resume_id: Mapped[str] = mapped_column(ForeignKey("resume_documents.id", ondelete="CASCADE"), index=True)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    section: Mapped[str] = mapped_column(String(80), default="Resume")
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(EMBEDDING_DIMENSION), nullable=False)
    resume: Mapped[ResumeDocument] = relationship(back_populates="chunks")


_engine = None
_SessionLocal = None


def get_session_factory():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        _engine = create_engine(DATABASE_URL, pool_pre_ping=True, future=True)
        _SessionLocal = sessionmaker(bind=_engine, expire_on_commit=False)
    return _SessionLocal


def init_rag_database() -> None:
    factory = get_session_factory()
    with factory() as db:
        db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        db.commit()
    Base.metadata.create_all(bind=_engine)


def save_resume(candidate_name: str, filename: str, extracted_text: str,
                chunks: Iterable[dict]) -> str:
    factory = get_session_factory()
    document = ResumeDocument(
        candidate_name=candidate_name.strip(),
        filename=filename,
        extracted_text=extracted_text,
    )
    with factory() as db:
        db.add(document)
        db.flush()
        for item in chunks:
            db.add(ResumeChunk(
                resume_id=document.id,
                chunk_index=item["chunk_index"],
                section=item.get("section", "Resume"),
                content=item["content"],
                embedding=item["embedding"],
            ))
        db.commit()
        return document.id


def list_resumes() -> list[dict]:
    factory = get_session_factory()
    with factory() as db:
        rows = db.execute(
            select(ResumeDocument).order_by(ResumeDocument.created_at.desc())
        ).scalars().all()
        return [{
            "id": row.id, "candidate_name": row.candidate_name,
            "filename": row.filename, "created_at": row.created_at,
        } for row in rows]


def retrieve_evidence(resume_id: str, query_embedding: list[float], limit: int = 6) -> list[dict]:
    factory = get_session_factory()
    distance = ResumeChunk.embedding.cosine_distance(query_embedding)
    with factory() as db:
        rows = db.execute(
            select(ResumeChunk, distance.label("distance"))
            .where(ResumeChunk.resume_id == resume_id)
            .order_by(distance)
            .limit(limit)
        ).all()
        return [{
            "section": chunk.section,
            "content": chunk.content,
            "similarity": round(1.0 - float(distance_value), 4),
        } for chunk, distance_value in rows]
