# 🎯 InterviewIQ

> **Intelligent, Repeatable Interview Practice and Structured Feedback for Internship and Graduate-Job Applicants.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit App](https://img.shields.io/badge/frontend-Streamlit-FF4B4B.svg)](https://streamlit.io)
[![Tests Passing](https://img.shields.io/badge/tests-13%20passed-brightgreen.svg)]()
[![Ethics](https://img.shields.io/badge/ethical%20feedback-anti--fabrication-success.svg)]()

---

## 📌 Problem to Solve
Job seekers and students preparing for competitive internships and graduate roles often fall into the trap of memorizing generic, canned answers. In real interviews, this fragile preparation crumbles as soon as interviewers ask probing follow-up questions.

**InterviewIQ** solves this problem by providing a realistic, repeatable practice loop:
1. One question at a time across Technical, Behavioral, and Project-Explanation domains.
2. Contextual follow-up questions that probe decisions, trade-offs, and metrics.
3. Diagnostic scoring against a transparent, visible 4-part rubric.
4. Constructive improvement advice and structural answer outlines without fabricating false work experience.

---

## 🚀 Key Features

### 1. MVP Capabilities
- **Targeted Profiles:** Collects target role (Software Engineering, Frontend, Data Science/ML, Product Management, DevOps), experience level (Internship, Graduate 0-1 yrs, Junior 1-2 yrs, Switcher), and interview type.
- **Dynamic Session Flow:** Configurable sessions of 5 to 8 questions asking one question at a time with a dynamic follow-up probe.
- **Visible 4-Part Rubric:**
  - **Relevance & Directness:** Direct alignment with prompt and follow-up sub-intent.
  - **Structure & Organization:** Explicit narrative sequencing (STAR framework, problem-solution-tradeoff).
  - **Evidence & Ownership:** Concrete technical specifics, personal agency ("I" vs generic "we"), and measurable impact.
  - **Clarity & Communication:** Professional vocabulary, conciseness, and elimination of filler.
- **Ethical Answer Outlines:** Scaffolding blueprints that teach candidates how to frame their real coursework, labs, and personal projects rather than inventing fake companies or inflated metrics.

### 2. Advanced Extensions
- **Curated Question Banks & STAR Coach:**
  - Curated behavioral bank with STAR hints across leadership, teamwork, failure, and ambiguity.
  - Role-specific technical quizzes for SWE, Data Science, PM, and Cloud/DevOps.
  - Project architecture & retrospective challenges.
  - Interactive STAR Sandbox to test and refine individual stories.
- **Local SQLite Persistence:**
  - Complete turn-by-turn answer history, follow-up pairs, and timestamps stored locally in SQLite (`interview_iq.db`).
  - Historical student performance analytics and rubric trends.
- **Multi-Format Report Export:**
  - Export practice summaries in Markdown (`.md`), standalone printable HTML / PDF (`.html`), and machine-readable JSON (`.json`).
  - Features an Executive Scorecard and a 7-Day Personalized Next-Steps Action Plan.
- **Dual Evaluation Engine:**
  - Works 100% offline out-of-the-box with intelligent structural heuristics.
  - Supports live LLMs (Google Gemini / OpenAI compatible) with strict ethical system prompts.

---

## ⚖️ Transparent Rubric & Ethical Guardrails

### ⚠️ Practice Feedback Notice
> **Notice:** Rubric scores and feedback are formative practice indicators designed to highlight communication structure, technical depth, and answer organization. They are **NOT predictive hiring decisions, ATS screening filters, or employment guarantees**. Use these insights to refine your authentic voice and genuine experiences.

### 🛡️ Anti-Fabrication Guarantee
> **Ethical Standard:** Feedback and stronger outlines provide structural scaffolding and strategic framing prompts. They **NEVER fabricate fictional company names, unearned technical credentials, or false project metrics**.

---

## 🛠️ Architecture & Tech Stack

```
interview_iq/
├── app.py                      # Streamlit frontend & interactive tabs
├── backend/
│   ├── __init__.py             # Package exports
│   ├── models.py               # Dataclasses, Enums, and Rubric schemas
│   ├── question_bank.py        # Curated technical, behavioral, & project questions
│   ├── database.py             # SQLite persistence, CRUD, & analytics
│   ├── evaluator.py            # Dual-mode rubric engine (Heuristic & LLM)
│   └── report_generator.py     # Markdown, HTML, & JSON report builders
├── tests/
│   ├── __init__.py
│   └── test_interview_iq.py    # Unit & acceptance test suite
├── requirements.txt            # Python dependencies
└── README.md                   # Documentation
```

- **Frontend:** Streamlit 1.66+
- **Backend:** Python 3.10+ dataclasses, regex heuristics, and REST APIs
- **Database:** SQLite3 with relational foreign keys and indexes
- **Testing:** Pytest

---

## ⚡ Quickstart Guide

### 1. Prerequisites
- Python 3.10 or higher

### 2. Installation
Clone the repository and set up a virtual environment:

```bash
cd interview_iq
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Run the Application
Launch the Streamlit app:

```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

### 4. Running Without an API Key
InterviewIQ comes with an **Intelligent Offline Evaluator** enabled by default. You can immediately practice full interview sessions, answer follow-ups, and receive rubric scoring without any API keys or network connection!

### 5. (Optional) Using Live LLM (Gemini / OpenAI)
To enable live LLM evaluation, either:
- Export your key in your environment:
  ```bash
  export GEMINI_API_KEY="your-gemini-key"
  # or
  export OPENAI_API_KEY="your-openai-key"
  ```
- Or enter it directly in the app's sidebar under **Evaluator Engine Settings**.

---

## 🧪 Running Acceptance & Unit Tests

The test suite validates technical, behavioral, and project-explanation questions, transparent scoring rubrics, ethical guardrails, SQLite storage, and report generation:

```bash
pytest tests/
```

---

## 📄 License
MIT License. See [LICENSE](LICENSE) for details.
