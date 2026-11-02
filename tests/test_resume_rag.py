"""Unit tests for deterministic resume chunking and PDF validation."""
import io

import pytest

from backend.resume_rag import split_resume, extract_pdf_text


def test_split_resume_returns_nonempty_indexed_chunks():
    text = "SKILLS\n" + ("Python SQL machine learning and backend development. " * 60)
    chunks = split_resume(text)
    assert chunks
    assert [item["chunk_index"] for item in chunks] == list(range(len(chunks)))
    assert all(item["content"].strip() for item in chunks)
    assert all("section" in item for item in chunks)


def test_split_resume_preserves_section_labels():
    chunks = split_resume("EDUCATION\nB.Tech Computer Science and Engineering\nPROJECTS\nBuilt a Python web application.")
    assert chunks[0]["section"] == "Education"
    assert any(item["section"] == "Projects" for item in chunks)


def test_extract_pdf_rejects_non_pdf():
    class Upload:
        def getvalue(self):
            return b"not a pdf"

    with pytest.raises(ValueError, match="valid PDF"):
        extract_pdf_text(Upload())


def test_extract_pdf_rejects_tiny_or_scanned_content():
    class Upload:
        def getvalue(self):
            return b"%PDF-1.4\n% empty sample"

    with pytest.raises(ValueError):
        extract_pdf_text(Upload())
