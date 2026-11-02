"""Resume ingestion, semantic retrieval, and evidence-grounded job comparison."""
from __future__ import annotations

import io
import re
from functools import lru_cache

from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from backend.rag_store import EMBEDDING_DIMENSION, init_rag_database, save_resume, retrieve_evidence

MAX_RESUME_BYTES = 8 * 1024 * 1024
MAX_RESUME_CHARS = 50_000
CHUNK_CHARS = 900
CHUNK_OVERLAP = 140


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    import os
    return SentenceTransformer(os.getenv(
        "EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"
    ))


def embed_texts(texts: list[str]) -> list[list[float]]:
    vectors = get_embedding_model().encode(
        texts, normalize_embeddings=True, show_progress_bar=False
    )
    return [vector.astype(float).tolist() for vector in vectors]


def extract_pdf_text(uploaded_file) -> str:
    raw = uploaded_file.getvalue()
    if len(raw) > MAX_RESUME_BYTES:
        raise ValueError("Resume PDF must be 8 MB or smaller.")
    if not raw.startswith(b"%PDF"):
        raise ValueError("Please upload a valid PDF file.")
    try:
        reader = PdfReader(io.BytesIO(raw), strict=False)
        if reader.is_encrypted:
            raise ValueError("This PDF is password-protected. Upload an unlocked copy.")
        text = "\n".join((page.extract_text() or "") for page in reader.pages[:10])
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError("Could not read this PDF. Please export it again as a text-based PDF.") from exc
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text).strip()
    if len(text) < 80:
        raise ValueError("Not enough selectable text was found. Scanned-image PDFs need OCR first.")
    return text[:MAX_RESUME_CHARS]


def split_resume(text: str) -> list[dict]:
    """Create overlapping chunks and attach a best-effort section label."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    sections = []
    current_section = "Resume"
    for line in lines:
        if len(line) < 65 and re.fullmatch(r"[A-Za-z][A-Za-z &/+-]{1,48}", line):
            current_section = line.title()
        sections.append((current_section, line))

    chunks, buffer, section, index = [], "", "Resume", 0
    for current, line in sections:
        if buffer and (len(buffer) + len(line) + 1 > CHUNK_CHARS or current != section):
            chunks.append({"chunk_index": index, "section": section, "content": buffer.strip()})
            index += 1
            buffer = buffer[-CHUNK_OVERLAP:] if current == section else ""
        section = current
        buffer = f"{buffer}\n{line}".strip()
    if buffer:
        chunks.append({"chunk_index": index, "section": section, "content": buffer.strip()})
    return chunks


def ingest_resume(candidate_name: str, filename: str, pdf_file) -> str:
    text = extract_pdf_text(pdf_file)
    chunks = split_resume(text)
    vectors = embed_texts([item["content"] for item in chunks])
    for item, vector in zip(chunks, vectors):
        item["embedding"] = vector
    init_rag_database()
    return save_resume(candidate_name, filename, text, chunks)


def compare_resume_to_job(resume_id: str, job_description: str, top_k: int = 8) -> list[dict]:
    requirements = [
        re.sub(r"^[\s•*\-\d.)]+", "", line).strip()
        for line in job_description.splitlines()
    ]
    requirements = [line for line in requirements if len(line) >= 12]
    if not requirements:
        requirements = [sentence.strip() for sentence in re.split(r"(?<=[.!?])\s+", job_description) if len(sentence.strip()) >= 12]
    if not requirements:
        raise ValueError("Enter a job description with role responsibilities or skill requirements.")
    vectors = embed_texts(requirements)
    evidence = []
    for requirement, vector in zip(requirements[:top_k], vectors[:top_k]):
        matches = retrieve_evidence(resume_id, vector, limit=2)
        evidence.append({"requirement": requirement, "matches": matches})
    return evidence


def get_resume_embedding_dimension() -> int:
    return EMBEDDING_DIMENSION
