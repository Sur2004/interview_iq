# InterviewIQ local demo (Windows development, Mac presentation)

## What is included
- Existing Streamlit mock-interview experience remains the main application.
- A separate Resume Intelligence page extracts PDF text, chunks it, embeds the chunks with Sentence Transformers, and stores the source text plus 384-dimensional vectors in PostgreSQL with pgvector.
- Job-description comparison retrieves the closest resume passages for each requirement. Similarity is a retrieval signal, not an ATS score or hiring decision.
- Docker Compose runs the Streamlit app and PostgreSQL together. The same images and configuration work on Windows, Intel Mac, and Apple Silicon Mac through Docker Desktop.

## Prerequisites
- Docker Desktop installed and running.
- Git.
- At least 8 GB available RAM recommended for the first embedding-model download.

## Configure
1. Copy `env.example` to `.env`.
2. Replace `POSTGRES_PASSWORD` with a strong local password.
3. Optionally add exactly one hosted model provider key (Gemini, Groq, or OpenAI). Resume extraction and semantic retrieval do not require a hosted LLM key.

Never commit `.env`, API keys, uploaded resumes, or database volumes to Git.

## Start
```bash
docker compose up --build
```
Open http://localhost:8501. The first start downloads Python dependencies and the sentence-transformers embedding model; allow time and network access.

## Stop / preserve data
```bash
docker compose down
```
The PostgreSQL named volume is retained. To delete the demo database and uploaded files permanently:
```bash
docker compose down -v
```

## Windows development, Mac demo
Push the feature branch to GitHub, then on the Mac:
```bash
git clone --branch feature/rag-postgres-cross-platform https://github.com/Sur2004/interview_iq.git
cd interview_iq
docker compose up --build
```

## Current scope and limitations
- The new PostgreSQL database stores resume documents and vector chunks. The existing interview-history implementation has not yet been migrated from SQLite/browser storage; it remains compatible as a separate subsystem for this first integration.
- PDF parsing supports text-based PDFs, not image-only scans (OCR is not included yet).
- Retrieval results show source passages and similarity. A calibrated ATS score and LLM-generated evidence synthesis are intentionally not claimed by this initial RAG vertical slice.
- The first run downloads the embedding model from Hugging Face. For an offline presentation, pre-cache the model or run once while connected.
- Run automated tests with `python -m pytest -q`. Docker-based integration tests and a real end-to-end run are still required before calling this production-ready.
