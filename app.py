"""
InterviewIQ - AI Mock Interview & Diagnostic Rubric Studio
Cyber-Engineering Edition: Sky Blue, White, & Black High-Tech Architecture.
"""

import streamlit as st
import streamlit.components.v1 as components
import time
import os
import uuid
import pandas as pd
import json

from backend.models import (
    ExperienceLevel,
    InterviewType,
    QuestionCategory,
    TargetRole,
    QuestionItem,
    InterviewTurn,
    InterviewSession,
    RUBRIC_DISCLAIMER,
    ETHICAL_OUTLINE_GUIDELINE,
)
from backend.question_bank import (
    BEHAVIORAL_QUESTIONS,
    PROJECT_QUESTIONS,
    TECHNICAL_QUESTIONS_BY_ROLE,
    build_interview_plan,
)
from backend.evaluator import (
    evaluate_heuristically,
    evaluate_with_llm,
    generate_followup_question,
    analyze_technical_complexity,
    generate_mermaid_architecture,
    generate_dynamic_ai_technical_question,
    RUBRIC_CRITERIA_META,
)
from backend.database import (
    init_db,
    save_session,
    get_session,
    list_sessions,
    delete_session,
    get_aggregate_analytics,
)
from backend.report_generator import (
    generate_markdown_report,
    generate_html_report,
)
from backend.config import get_llm_config

# Page configuration
st.set_page_config(
    page_title="InterviewIQ - AI Technical Interview Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
init_db()

# High-Tech Sky Blue, White, and Black Aesthetic with Animated Cards
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    code, pre {
        font-family: 'JetBrains Mono', monospace !important;
    }

    /* Keyframe Animations */
    @keyframes skyPulse {
        0% { box-shadow: 0 0 12px rgba(14, 165, 233, 0.25); border-color: rgba(14, 165, 233, 0.45); }
        50% { box-shadow: 0 0 30px rgba(14, 165, 233, 0.7); border-color: #38bdf8; }
        100% { box-shadow: 0 0 12px rgba(14, 165, 233, 0.25); border-color: rgba(14, 165, 233, 0.45); }
    }

    @keyframes liveGlow {
        0% { opacity: 0.6; transform: scale(0.96); }
        50% { opacity: 1; transform: scale(1.04); }
        100% { opacity: 0.6; transform: scale(0.96); }
    }

    @keyframes scanLine {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    /* Sky Blue Hero Banner */
    .hero-banner-sky {
        background: linear-gradient(135deg, #000000 0%, #03182e 50%, #0369a1 100%);
        border: 2px solid #0ea5e9;
        border-radius: 16px;
        padding: 30px 36px;
        color: #ffffff;
        margin-bottom: 22px;
        box-shadow: 0 14px 34px -8px rgba(14, 165, 233, 0.4);
        position: relative;
        overflow: hidden;
    }

    .hero-banner-sky::after {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, transparent, #38bdf8, #ffffff, #38bdf8, transparent);
        background-size: 200% 100%;
        animation: scanLine 3.5s linear infinite;
    }

    .hero-title {
        font-size: 2.3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #ffffff;
        margin-bottom: 6px;
    }

    .hero-subtitle {
        font-size: 1.05rem;
        color: #bae6fd;
        max-width: 860px;
        line-height: 1.5;
    }

    /* Animated Question Card */
    .animated-question-card {
        background: #ffffff;
        border: 2px solid #0ea5e9;
        border-radius: 14px;
        padding: 26px 30px;
        color: #000000;
        box-shadow: 0 8px 26px rgba(14, 165, 233, 0.2);
        animation: skyPulse 3.5s infinite ease-in-out;
        margin-bottom: 20px;
    }

    /* Animated Follow-Up Card */
    .animated-followup-card {
        background: #000000;
        border: 2px solid #38bdf8;
        border-radius: 14px;
        padding: 24px 28px;
        color: #ffffff;
        box-shadow: 0 8px 24px rgba(14, 165, 233, 0.35);
        margin: 20px 0;
    }

    /* Dynamic Telemetry Metric Cards */
    .telemetry-card {
        background: #000000;
        border: 1px solid #0284c7;
        border-radius: 12px;
        padding: 18px 20px;
        color: #ffffff;
        box-shadow: 0 4px 14px rgba(0,0,0,0.5);
        margin-bottom: 14px;
        transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
    }

    .telemetry-card:hover {
        transform: translateY(-3px);
        border-color: #38bdf8;
        box-shadow: 0 8px 24px rgba(14, 165, 233, 0.35);
    }

    /* Status Pill */
    .ai-online-badge {
        display: inline-block;
        background: #000000;
        color: #38bdf8;
        border: 1px solid #0284c7;
        padding: 4px 12px;
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 700;
        letter-spacing: 0.05em;
        animation: liveGlow 2.5s infinite ease-in-out;
    }

    .notice-card-sky {
        background: #ffffff;
        border-left: 5px solid #0284c7;
        border-top: 1px solid #e0f2fe;
        border-right: 1px solid #e0f2fe;
        border-bottom: 1px solid #e0f2fe;
        padding: 14px 18px;
        border-radius: 8px;
        font-size: 0.88rem;
        color: #000000;
        margin-bottom: 14px;
    }

    .ethics-card-sky {
        background: #000000;
        border-left: 5px solid #38bdf8;
        border: 1px solid #0369a1;
        padding: 12px 18px;
        border-radius: 8px;
        font-size: 0.86rem;
        color: #e0f2fe;
        margin-bottom: 22px;
    }

    .score-badge-sky {
        font-size: 1rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 9999px;
        display: inline-block;
        background: #000000;
        color: #38bdf8;
        border: 1px solid #0ea5e9;
    }

    .tech-tag {
        display: inline-block;
        background: #000000;
        color: #7dd3fc;
        border: 1px solid #0284c7;
        border-radius: 6px;
        padding: 3px 8px;
        font-size: 0.78rem;
        font-family: 'JetBrains Mono', monospace;
        margin-right: 6px;
        margin-bottom: 6px;
    }

    /* Pacing Indicator */
    .pacing-chip {
        display: inline-block;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 6px;
        margin-left: 8px;
    }
    .pacing-ok { background: #000000; color: #38bdf8; border: 1px solid #0284c7; }
    .pacing-warn { background: #000000; color: #f87171; border: 1px solid #ef4444; }

    /* Responsive layout, accessible focus states, and reduced-motion support */
    .role-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(132px, 1fr));
        gap: 10px;
        margin: 8px 0 18px;
    }
    .role-card {
        min-height: 92px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 5px;
        padding: 12px 8px;
        background: #050b14;
        border: 1px solid #155e85;
        border-radius: 12px;
        text-align: center;
        transition: border-color .18s ease, transform .18s ease;
    }
    .role-card:hover { border-color: #7dd3fc; transform: translateY(-2px); }
    .role-card-icon { font-size: 1.45rem; line-height: 1.2; }
    .role-card-label { color: #e0f2fe; font-size: .78rem; font-weight: 700; line-height: 1.3; }
    button[kind="primary"] { border-radius: 10px; font-weight: 700; }
    button:focus-visible, a:focus-visible, input:focus-visible, textarea:focus-visible {
        outline: 3px solid #38bdf8 !important;
        outline-offset: 2px !important;
    }
    [data-testid="stTabs"] [role="tab"] { font-weight: 650; }
    [data-testid="stMetric"] {
        background: rgba(14, 165, 233, .06);
        border: 1px solid rgba(14, 165, 233, .24);
        border-radius: 12px;
        padding: 12px 14px;
    }
    @media (max-width: 900px) {
        .hero-banner-sky { padding: 24px 22px; }
        .hero-title { font-size: clamp(1.45rem, 4vw, 2rem); line-height: 1.18; }
        .hero-subtitle { font-size: .96rem; }
        .role-grid { grid-template-columns: repeat(auto-fit, minmax(118px, 1fr)); }
    }
    @media (max-width: 600px) {
        .hero-banner-sky { padding: 20px 16px; border-radius: 12px; }
        .hero-title { font-size: 1.5rem; }
        .hero-subtitle { font-size: .9rem; }
        .role-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }
        .role-card { min-height: 78px; }
        .telemetry-card { padding: 14px; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: .01ms !important;
        }
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if "session" not in st.session_state:
    st.session_state.session = None
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
if "eval_mode" not in st.session_state:
    st.session_state.eval_mode = "Intelligent AI Engine"
if "interviewer_persona" not in st.session_state:
    st.session_state.interviewer_persona = "Jordan (Principal Architect / Scale & Failure Modes)"


def get_performance_badge(score: float) -> str:
    if score >= 4.2:
        return '<span class="score-badge-sky">⚡ Advanced Mastery (4.2 – 5.0)</span>'
    elif score >= 3.2:
        return '<span class="score-badge-sky">📈 Proficient Communicator (3.2 – 4.1)</span>'
    else:
        return '<span class="score-badge-sky">🌱 Developing Foundation (1.0 – 3.1)</span>'


def get_word_pacing_chip(words: int) -> str:
    if words < 60:
        return '<span class="pacing-chip pacing-warn">⚠️ Too Brief (&lt;60 words)</span>'
    elif words <= 200:
        return '<span class="pacing-chip pacing-ok">✨ Sweet Spot (60–200 words)</span>'
    else:
        return '<span class="pacing-chip pacing-warn">⚠️ Verbose / Wordy (&gt;200 words)</span>'


def get_active_llm_settings() -> dict:
    """Resolve the selected provider and its own key without cross-provider leakage."""
    configured = get_llm_config()
    selection = st.session_state.get("sb_provider", "Auto (via .env / Secrets)")
    provider_by_label = {
        "Groq Cloud — Llama 3.3 70B": "groq",
        "Google Gemini 3.8 Flash": "gemini",
        "OpenAI GPT-4o Mini": "openai",
        "Built-In Offline Engine": "heuristic",
    }
    provider = provider_by_label.get(selection, configured.get("provider") or "heuristic")
    if provider not in {"groq", "gemini", "openai", "heuristic"}:
        provider = "heuristic"

    manual_key = st.session_state.get("sb_manual_key", "").strip()
    key_field = {
        "groq": "groq_api_key",
        "gemini": "gemini_api_key",
        "openai": "openai_api_key",
    }.get(provider)
    api_key = None if provider == "heuristic" else (manual_key or configured.get(key_field))

    default_models = {
        "groq": "llama-3.3-70b-versatile",
        "gemini": "gemini-3.8-flash",
        "openai": "gpt-4o-mini",
        "heuristic": "built-in-diagnostic-engine",
    }
    return {
        "provider": provider,
        "api_key": api_key,
        "model_name": (
            configured.get("model_name")
            if provider == configured.get("provider")
            else default_models[provider]
        ),
    }


def render_mermaid(code: str, height: int = 240):
    """Renders a Mermaid diagram inside a styled HTML component with sky-blue accents."""
    if not code:
        return
    import html
    escaped_code = html.escape(code)
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ background: transparent; margin: 0; padding: 4px; display: flex; justify-content: center; }}
            .mermaid {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        </style>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ 
                startOnLoad: true, 
                theme: 'dark',
                themeVariables: {{
                    darkMode: true,
                    background: '#000000',
                    primaryColor: '#0ea5e9',
                    primaryTextColor: '#ffffff',
                    primaryBorderColor: '#38bdf8',
                    lineColor: '#38bdf8',
                    secondaryColor: '#0369a1',
                    tertiaryColor: '#0f172a'
                }}
            }});
        </script>
    </head>
    <body>
        <pre class="mermaid">
{escaped_code}
        </pre>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=True)




def render_answer_revision_editor(session: InterviewSession, turn: InterviewTurn, key_prefix: str) -> None:
    """Edit, re-score, and persist a completed answer with an audit trail."""
    with st.container(border=True):
        st.markdown("#### ✏️ Edit answer and refresh feedback")
        st.caption(
            "Edit either response below. Saving a revision re-runs the rubric and records "
            "the previous and updated text in this session's history."
        )
        revised_initial = st.text_area(
            "Main answer", value=turn.initial_answer, height=180,
            key=f"{key_prefix}_initial_revision",
        )
        old_followup_value = turn.followup_answer if turn.followup_answer != "[Skipped]" else ""
        revised_followup = st.text_area(
            "Follow-up answer", value=old_followup_value, height=130,
            key=f"{key_prefix}_followup_revision",
        )
        st.caption(f"Saved revisions: {len(turn.answer_revisions)}")
        if turn.answer_revisions:
            st.markdown("**Revision history (newest first)**")
            for revision_number, revision in enumerate(reversed(turn.answer_revisions), start=1):
                edited_at = revision.get("edited_at", time.time())
                st.markdown(
                    f"**Revision {revision_number} · {revision.get('field', 'answer')} · "
                    f"{time.strftime('%Y-%m-%d %H:%M', time.localtime(edited_at))}**"
                )
                with st.container(border=True):
                    st.caption("Previous version")
                    st.code(revision.get("previous", ""), language=None)
                    st.caption("Updated version")
                    st.code(revision.get("updated", ""), language=None)

        if st.button("Save revision and re-score", key=f"{key_prefix}_save_revision", type="primary"):
            revised_initial = revised_initial.strip()
            revised_followup = revised_followup.strip()
            if not revised_initial:
                st.warning("The main answer cannot be empty.")
                return
            if revised_initial == turn.initial_answer and revised_followup == old_followup_value:
                st.info("No changes detected. Edit an answer before saving.")
                return

            now = time.time()
            if revised_initial != turn.initial_answer:
                turn.answer_revisions.append({
                    "field": "main answer", "previous": turn.initial_answer,
                    "updated": revised_initial, "edited_at": now,
                })
            if revised_followup != old_followup_value:
                turn.answer_revisions.append({
                    "field": "follow-up answer", "previous": old_followup_value,
                    "updated": revised_followup, "edited_at": now,
                })

            turn.initial_answer = revised_initial
            turn.followup_answer = revised_followup or "[Skipped]"
            with st.spinner("Re-scoring your revised answer..."):
                turn.initial_evaluation = evaluate_with_llm(
                    turn.question, turn.initial_answer,
                    candidate_context=session.candidate_context,
                    **get_active_llm_settings(),
                )
                if turn.followup_answer != "[Skipped]":
                    turn.turn_evaluation = evaluate_with_llm(
                        turn.question, turn.initial_answer,
                        followup_answer=turn.followup_answer,
                        candidate_context=session.candidate_context,
                        **get_active_llm_settings(),
                    )
                else:
                    turn.turn_evaluation = turn.initial_evaluation
                turn.completed = True
                turn.timestamp = now
                scored_turns = [item.turn_evaluation for item in session.turns if item.turn_evaluation]
                session.overall_session_score = (
                    round(sum(item.overall_score for item in scored_turns) / len(scored_turns), 1)
                    if scored_turns else None
                )
                save_session(session)
            st.success("Revision saved to session history and feedback updated.")
            st.rerun()




# ==============================================================================
# SIDEBAR CONTROLS  (single clean block – no duplicates)
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#000,#03182e);border:1.5px solid #0ea5e9;
         border-radius:12px;padding:14px 16px;margin-bottom:12px;">
        <div style="font-size:1.35rem;font-weight:800;color:#fff;letter-spacing:-0.01em;">
            \U0001f3af InterviewIQ Studio
        </div>
        <div style="font-size:0.82rem;color:#bae6fd;margin-top:4px;">
            Technical &amp; Behavioural Interview Practice Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("\u2699\ufe0f Session Setup")

    candidate_name = st.text_input(
        "Your Name",
        value="Student Candidate",
        help="Personalises practice reports and rubric summaries.",
        key="sb_candidate_name",
    )

    target_role = st.selectbox(
        "\U0001f3ad Target Role",
        [r.value for r in TargetRole],
        index=0,
        help="Sets technical depth, domain questions and rubric expectations.",
        key="sb_target_role",
    )

    experience_level = st.selectbox(
        "\U0001f4c8 Experience Level",
        [e.value for e in ExperienceLevel],
        index=0,
        help="Tailors question difficulty and scoring criteria.",
        key="sb_experience_level",
    )

    interview_type = st.selectbox(
        "\U0001f5c2\ufe0f Interview Type",
        [t.value for t in InterviewType],
        index=0,
        help="Comprehensive Mix, Technical Deep-Dive, Behavioural, or Architecture.",
        key="sb_interview_type",
    )

    interviewer_persona = st.selectbox(
        "\U0001f935 Interviewer Persona",
        [
            "Jordan — Principal Architect (Scale & Failure Modes)",
            "Alex — Staff Engineer (Algorithms & Clean Code)",
            "Taylor — VP Engineering (Vision & Culture Fit)",
        ],
        index=0,
        help="Shapes tone and technical rigour of follow-up questions.",
        key="sb_interviewer_persona",
    )
    st.session_state.interviewer_persona = interviewer_persona

    num_questions = st.slider(
        "\U0001f522 Questions in Round",
        min_value=5,
        max_value=8,
        value=6,
        help="5-8 questions to simulate a 45-minute technical loop.",
        key="sb_num_questions",
    )

    candidate_context = st.text_area(
        "\U0001f4dd Your Projects / Coursework (Optional)",
        placeholder=(
            "e.g. Distributed KV-Store in Go; Virtual Memory Manager in C; "
            "React & PostgreSQL e-commerce; PyTorch RAG pipeline..."
        ),
        help="Grounds AI feedback in your real background - no fabrication.",
        height=90,
        key="sb_candidate_context",
    )

    st.markdown("---")
    with st.expander("\U0001f511 LLM Provider & API Key", expanded=False):
        provider_opts = [
            "Auto (via .env / Secrets)",
            "Groq Cloud — Llama 3.3 70B",
            "Google Gemini 3.8 Flash",
            "OpenAI GPT-4o Mini",
            "Built-In Offline Engine",
        ]
        chosen_provider = st.selectbox(
            "Provider",
            provider_opts,
            index=0,
            help="Keys live in .env locally or Streamlit Secrets on Cloud.",
            key="sb_provider",
        )
        manual_key = st.text_input(
            "API Key Override",
            value="",
            type="password",
            placeholder="Paste key to override...",
            help="Never committed or logged.",
            key="sb_manual_key",
        )
        if manual_key:
            st.session_state.api_key = manual_key

        active_settings = get_active_llm_settings()
        if active_settings["provider"] == "heuristic":
            st.info("Offline diagnostic mode is selected. No API key is required.")
        elif active_settings.get("api_key"):
            st.success(f"Selected provider is configured: {active_settings['provider'].upper()} · {active_settings['model_name']}")
        else:
            st.warning(
                f"No API key is configured for {active_settings['provider'].upper()}. "
                "The app will fall back to offline diagnostic feedback until a matching key is available."
            )

    st.markdown("---")
    if st.button("\U0001f680 Start Interview Round", type="primary", use_container_width=True):
        questions = build_interview_plan(
            target_role=target_role,
            experience_level=experience_level,
            interview_type=interview_type,
            num_questions=num_questions,
        )
        turns = [
            InterviewTurn(
                question_index=i,
                question=q,
                followup_question=q.default_followup,
            )
            for i, q in enumerate(questions)
        ]
        new_sess = InterviewSession(
            session_id=str(uuid.uuid4())[:8],
            candidate_name=candidate_name.strip() or "Student Candidate",
            target_role=target_role,
            experience_level=experience_level,
            interview_type=interview_type,
            total_questions=len(questions),
            candidate_context=candidate_context.strip(),
            turns=turns,
            current_turn_index=0,
            in_followup=False,
            is_finished=False,
        )
        st.session_state.session = new_sess
        save_session(new_sess)
        st.success(f"\u2705 Round started - {len(questions)} questions queued!")
        st.rerun()

    if st.session_state.session and not st.session_state.session.is_finished:
        st.markdown("---")
        if st.button("\u23f9\ufe0f End Session Early", use_container_width=True):
            st.session_state.session.is_finished = True
            st.session_state.session.completed_at = time.time()
            save_session(st.session_state.session)
            st.rerun()

    st.markdown("---")
    st.page_link("pages/1_History.py", label="\U0001f4da History & Performance", icon="\U0001f4ca")


# ==============================================================================
# HERO HEADER BANNER  (sky-blue / white / black)
# ==============================================================================
st.markdown("""
<div class="hero-banner-sky">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
        <div>
            <div class="hero-title">\U0001f3af InterviewIQ</div>
            <div class="hero-subtitle">
                Practice realistic technical, behavioral, and project interviews.
                Get structured feedback, follow-up challenges, and a clear improvement plan.
            </div>
            <div style="display:flex;flex-wrap:wrap;gap:8px;margin-top:14px;">
                <span class="tech-tag">4-part feedback rubric</span>
                <span class="tech-tag">5–8 questions per round</span>
                <span class="tech-tag">Offline practice available</span>
            </div>
        </div>
        <div style="text-align:right;white-space:nowrap;">
            <span class="ai-online-badge">INTERVIEW PRACTICE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Dynamic Role Selector Cards
roles_meta = [
    ("\U0001f4bb", "Software Engineering", "#0ea5e9"),
    ("\U0001f3a8", "Frontend / UI", "#6366f1"),
    ("\U0001f4ca", "Data Science & ML", "#10b981"),
    ("\U0001f916", "AI / LLM Engineering", "#f59e0b"),
    ("\U0001f512", "Cybersecurity", "#ef4444"),
    ("\U0001f680", "DevOps / Platform", "#8b5cf6"),
    ("\U0001f4e6", "Product Management", "#ec4899"),
]
role_cards_html = "".join(
    f'<div class="role-card" style="border-color:{color}">'
    f'<div class="role-card-icon" aria-hidden="true">{icon}</div>'
    f'<div class="role-card-label">{label}</div>'
    f'</div>'
    for icon, label, color in roles_meta
)
st.markdown(f'<div class="role-grid">{role_cards_html}</div>', unsafe_allow_html=True)

st.markdown(
    f'<div class="notice-card-sky"><strong>\u2139\ufe0f Rubric Notice:</strong> {RUBRIC_DISCLAIMER}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="ethics-card-sky"><strong>\U0001f6e1\ufe0f Anti-Fabrication:</strong> {ETHICAL_OUTLINE_GUIDELINE}</div>',
    unsafe_allow_html=True,
)


# ==============================================================================
# MAIN NAVIGATION TABS
# ==============================================================================
tab_studio, tab_dynamic_ai, tab_flaw_game, tab_star_builder, tab_bank, tab_playbook, tab_analytics, tab_report, tab_rubric = st.tabs([
    "\U0001f3af Mock Interview Studio",
    "\u26a1 Technical Generator",
    "\U0001f3ae Spot the Flaw",
    "\U0001f6e0\ufe0f STAR Builder",
    "\U0001f4da Question Bank",
    "\U0001f4d6 Design Playbooks",
    "\U0001f4ca Practice Analytics",
    "\U0001f4d1 Export Report",
    "\u2696\ufe0f Rubric Guide",
])


# ==============================================================================
# TAB 1: MOCK INTERVIEW STUDIO
# ==============================================================================
with tab_studio:
    session: InterviewSession = st.session_state.session

    if session is None:
        st.markdown("### 👋 Your interview practice workspace")
        st.write("Start with a guided mock interview or choose a focused tool below. Your answers are scored against a practice rubric—not a hiring prediction.")
        quick_cols = st.columns(3)
        with quick_cols[0]:
            st.markdown("**01 · Mock interview**")
            st.caption("A structured 5–8 question round with follow-up probing and answer review.")
        with quick_cols[1]:
            st.markdown("**02 · Technical challenge**")
            st.caption("Practice a specific topic, revise your answer, and refresh the feedback.")
        with quick_cols[2]:
            st.markdown("**03 · Behavioral practice**")
            st.caption("Build stronger STAR stories from your real coursework and project experience.")
        st.info("To begin, choose your target role and experience level in the sidebar, then select **Start Interview Round**. You can also explore the other tabs without starting a round.")

        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown("""
            <div class="telemetry-card">
                <span style="color:#38bdf8; font-weight:700; font-size:0.85rem;">[01 / REAL-TIME PROBES]</span>
                <h4 style="color:#ffffff; margin: 8px 0;">Contextual AI Follow-Ups</h4>
                <p style="color:#94a3b8; font-size:0.9rem;">
                    The AI listens to your primary answer and immediately generates a realistic follow-up probing trade-offs, edge cases, and scale.
                </p>
                <span class="tech-tag">Dynamic Questioning</span>
                <span class="tech-tag">Zero Scripting</span>
            </div>
            """, unsafe_allow_html=True)

        with col_c2:
            st.markdown("""
            <div class="telemetry-card">
                <span style="color:#38bdf8; font-weight:700; font-size:0.85rem;">[02 / TECHNICAL TELEMETRY]</span>
                <h4 style="color:#ffffff; margin: 8px 0;">Big-O & Concurrency Check</h4>
                <p style="color:#94a3b8; font-size:0.9rem;">
                    Evaluates algorithmic time/space complexity, race condition defenses, mutex locks, and architectural patterns.
                </p>
                <span class="tech-tag">O(1) vs O(log N)</span>
                <span class="tech-tag">Mutex / OCC</span>
            </div>
            """, unsafe_allow_html=True)

        with col_c3:
            st.markdown("""
            <div class="telemetry-card">
                <span style="color:#38bdf8; font-weight:700; font-size:0.85rem;">[03 / VISIBLE RUBRIC]</span>
                <h4 style="color:#ffffff; margin: 8px 0;">Diagnostic 4-Part Scoring</h4>
                <p style="color:#94a3b8; font-size:0.9rem;">
                    Transparent scoring across Relevance, Structure, Evidence, and Clarity with personalized improvement roadmaps.
                </p>
                <span class="tech-tag">Formative Feedback</span>
                <span class="tech-tag">Non-Predictive</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
# ==============================================================================

    elif session.is_finished:
        st.success("\U0001f389 **Interview Round Completed!** Full diagnostic transcript compiled below.")

        valid_turns = [t for t in session.turns if t.turn_evaluation]
        if valid_turns:
            avg_score = round(sum(t.turn_evaluation.overall_score for t in valid_turns) / len(valid_turns), 1)
            session.overall_session_score = avg_score
            save_session(session)

            col_sc1, col_sc2, col_sc3 = st.columns([1, 1, 2])
            with col_sc1:
                st.metric("Overall Practice Score", f"{avg_score} / 5.0")
            with col_sc2:
                st.markdown("**Performance Mastery:**")
                st.markdown(get_performance_badge(avg_score), unsafe_allow_html=True)
            with col_sc3:
                st.markdown(f"**Round Overview:** Completed {len(valid_turns)} of {session.total_questions} questions for **{session.target_role}**.")

            st.markdown("### \U0001f4dd Turn-by-Turn Diagnostic Review")
            for i, turn in enumerate(session.turns):
                t_eval = turn.turn_evaluation or turn.initial_evaluation
                score_str = f"{t_eval.overall_score}/5.0" if t_eval else "N/A"
                with st.expander(f"Question {i+1}: {turn.question.question_text[:75]}... (Score: {score_str})"):
                    st.markdown(f"**Question:** {turn.question.question_text}")
                    st.markdown(f"**Your Initial Answer:**\n```\n{turn.initial_answer}\n```")
                    if turn.followup_question:
                        st.markdown(f"**Follow-Up Question:**\n> *\"{turn.followup_question}\"*")
                        st.markdown(f"**Your Follow-Up Answer:**\n```\n{turn.followup_answer or 'N/A'}\n```")
                    if t_eval:
                        if t_eval.technical_breakdown:
                            tb = t_eval.technical_breakdown
                            st.markdown("#### \U0001f52c Technical Depth Telemetry")
                            col_t1, col_t2, col_t3 = st.columns(3)
                            with col_t1:
                                st.write("**Time Complexity:**", ", ".join(tb.get("time_complexity", [])) or "None explicit")
                            with col_t2:
                                st.write("**Concurrency:**", ", ".join(tb.get("concurrency_primitives", [])) or "None explicit")
                            with col_t3:
                                st.write("**Patterns:**", ", ".join(tb.get("architectural_patterns", [])) or "None explicit")
                        if t_eval.architecture_diagram_mermaid:
                            st.markdown("#### \U0001f5fa\ufe0f Architecture Diagram")
                            render_mermaid(t_eval.architecture_diagram_mermaid, height=240)
                        st.markdown("#### \u2696\ufe0f Rubric Breakdown")
                        cols_r = st.columns(4)
                        for idx, (k, r_crit) in enumerate(t_eval.rubric_scores.items()):
                            with cols_r[idx]:
                                st.metric(r_crit.display_name, f"{r_crit.score} / 5.0")
                                st.caption(r_crit.feedback)
                        st.markdown(t_eval.stronger_answer_outline)
                    render_answer_revision_editor(session, turn, f"finished_turn_{i}")
        else:
            st.warning("Session completed without submitted responses.")

        if st.button("\U0001f504 Start Fresh Practice Round"):
            st.session_state.session = None
            st.rerun()

    else:
        # ACTIVE INTERVIEW ROUND IN PROGRESS
        curr_idx = session.current_turn_index
        turn = session.turns[curr_idx]
        q_item = turn.question

        previous_turns = [
            (idx, previous_turn)
            for idx, previous_turn in enumerate(session.turns[:curr_idx])
            if previous_turn.completed
        ]
        if previous_turns:
            with st.expander("🗂️ Review or edit previous answers", expanded=False):
                for previous_idx, previous_turn in previous_turns:
                    previous_score = (
                        f"{previous_turn.turn_evaluation.overall_score:.1f}/5"
                        if previous_turn.turn_evaluation else "Not scored"
                    )
                    st.markdown(
                        f"**Question {previous_idx + 1}:** "
                        f"{previous_turn.question.question_text} · Score: {previous_score}"
                    )
                    st.write(f"Your answer: {previous_turn.initial_answer[:400] or 'No answer'}")
                    render_answer_revision_editor(
                        session, previous_turn, f"previous_turn_{previous_idx}"
                    )
                    st.divider()

        progress_val = curr_idx / session.total_questions
        st.progress(progress_val)
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            st.caption(f"Question {curr_idx + 1} of {session.total_questions} | {session.target_role} \u2022 {session.experience_level}")
        with col_p2:
            st.markdown(f"<span class='tech-tag'>{q_item.category.value.upper()}</span>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="animated-question-card">
            <span style="font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#0284c7; letter-spacing:0.05em;">
                \u26a1 Question {curr_idx + 1} \u2022 Focus: {q_item.competency_or_topic}
            </span>
            <p style="font-size:1.26rem; font-weight:700; color:#000000; margin-top:8px; line-height:1.5;">
                {q_item.question_text}
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("\U0001f4a1 Technical Expectations & Evaluation Hints", expanded=False):
            st.markdown("**What Interviewers Look For:**")
            for h in q_item.rubric_hints:
                st.markdown(f"- {h}")
            if q_item.category == QuestionCategory.BEHAVIORAL:
                st.info("**STAR Framework:**\n- **S:** Situation (15%)\n- **T:** Task (10%)\n- **A:** Action YOU took (60%)\n- **R:** Result + metrics (15%)")
            elif q_item.category == QuestionCategory.TECHNICAL:
                st.info("**Technical Flow:**\n1. Core definition\n2. Internal mechanics & complexity\n3. Real-world trade-offs\n4. Concrete example from your codebase")
            else:
                st.info("**Project Flow:**\n1. Problem & topology\n2. Stack choices vs alternatives\n3. Hardest bug YOU solved\n4. Hindsight redesign")

        if not session.in_followup and not turn.completed:
            st.markdown("#### \u270d\ufe0f Type Your Response")
            user_input = st.text_area(
                "Your Answer:",
                value=turn.initial_answer,
                height=180,
                placeholder="State your answer clearly. Explain technical choices, complexity trade-offs, and use 'I' to highlight your individual contribution...",
                key=f"ans_input_{curr_idx}",
            )
            word_count = len(user_input.strip().split()) if user_input.strip() else 0
            pacing_chip = get_word_pacing_chip(word_count)
            st.markdown(f"**Word Count:** `{word_count} words` {pacing_chip}", unsafe_allow_html=True)

            with st.expander("\U0001f4bb Include Code Snippet (Optional)"):
                code_input = st.text_area(
                    "Code / Pseudocode:",
                    height=110,
                    placeholder="def solve(stream):\n    cache = {}\n    ...",
                    key=f"code_snippet_{curr_idx}",
                )

            col_sub1, col_sub2 = st.columns([1, 4])
            with col_sub1:
                if st.button("Submit Answer \U0001f4ac", type="primary", use_container_width=True):
                    if not user_input.strip():
                        st.warning("Please type your response before submitting.")
                    else:
                        full_content = user_input.strip()
                        if code_input.strip():
                            full_content += f"\n\n[Code]:\n```\n{code_input.strip()}\n```"
                        turn.initial_answer = full_content
                        with st.spinner("Analysing your answer and generating follow-up..."):
                            init_eval = evaluate_with_llm(
                                q_item,
                                turn.initial_answer,
                                candidate_context=session.candidate_context,
                                **get_active_llm_settings(),
                            )
                            turn.initial_evaluation = init_eval
                            if init_eval.suggested_followup_question:
                                turn.followup_question = init_eval.suggested_followup_question
                            session.in_followup = True
                            save_session(session)
                            st.rerun()

        elif session.in_followup and not turn.completed:
            with st.expander("\U0001f4c4 Review Your Initial Response", expanded=False):
                st.markdown(turn.initial_answer)

            persona_name = st.session_state.interviewer_persona.split("\u2014")[0].strip()
            st.markdown(f"""
            <div class="animated-followup-card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:0.06em;">
                        \u26a1 {persona_name}'s Follow-Up Challenge
                    </span>
                    <span class="ai-online-badge">PROBING TRADE-OFFS</span>
                </div>
                <p style="font-size:1.22rem;font-weight:700;color:#ffffff;margin-top:8px;margin-bottom:0;line-height:1.5;">
                    \"{turn.followup_question or q_item.default_followup}\"
                </p>
            </div>
            """, unsafe_allow_html=True)

            followup_input = st.text_area(
                "Your Follow-Up Response:",
                value=turn.followup_answer,
                height=140,
                placeholder="Elaborate on failure modes, concurrency race conditions, or edge case trade-offs...",
                key=f"followup_input_{curr_idx}",
            )
            f_word_count = len(followup_input.strip().split()) if followup_input.strip() else 0
            st.caption(f"Follow-up length: {f_word_count} words")

            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                if st.button("Submit Follow-Up & Score Turn \U0001f3af", type="primary", use_container_width=True):
                    turn.followup_answer = followup_input.strip()
                    with st.spinner("Executing full 4-part rubric scoring..."):
                        full_eval = evaluate_with_llm(
                            q_item,
                            turn.initial_answer,
                            followup_answer=turn.followup_answer,
                            candidate_context=session.candidate_context,
                            **get_active_llm_settings(),
                        )
                        turn.turn_evaluation = full_eval
                        turn.completed = True
                        session.in_followup = False
                        save_session(session)
                        st.rerun()
            with col_f2:
                if st.button("Skip Follow-Up", use_container_width=True):
                    turn.followup_answer = "[Skipped]"
                    turn.turn_evaluation = turn.initial_evaluation
                    turn.completed = True
                    session.in_followup = False
                    save_session(session)
                    st.rerun()

        elif turn.completed and turn.turn_evaluation:
            t_eval = turn.turn_evaluation
            st.markdown("### \U0001f4ca Turn Diagnostic Results")
            col_sc, col_badge = st.columns([1, 2])
            with col_sc:
                st.metric("Turn Practice Score", f"{t_eval.overall_score} / 5.0")
            with col_badge:
                st.markdown("**Mastery Level:**")
                st.markdown(get_performance_badge(t_eval.overall_score), unsafe_allow_html=True)

            if t_eval.technical_breakdown:
                tb = t_eval.technical_breakdown
                st.markdown("#### \U0001f52c Technical Telemetry")
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    time_comp = ", ".join(tb.get("time_complexity", [])) or "None detected"
                    st.markdown(f'<div class="telemetry-card"><span style="color:#38bdf8;font-size:0.75rem;">TIME COMPLEXITY</span><h4 style="color:#fff;margin:6px 0;">{time_comp}</h4></div>', unsafe_allow_html=True)
                with col_m2:
                    concurrency = ", ".join(tb.get("concurrency_primitives", [])) or "None detected"
                    st.markdown(f'<div class="telemetry-card"><span style="color:#38bdf8;font-size:0.75rem;">CONCURRENCY</span><h4 style="color:#fff;margin:6px 0;">{concurrency}</h4></div>', unsafe_allow_html=True)
                with col_m3:
                    patterns = ", ".join(tb.get("architectural_patterns", [])) or "None detected"
                    st.markdown(f'<div class="telemetry-card"><span style="color:#38bdf8;font-size:0.75rem;">PATTERNS</span><h4 style="color:#fff;margin:6px 0;">{patterns}</h4></div>', unsafe_allow_html=True)

            if t_eval.architecture_diagram_mermaid:
                st.markdown("#### \U0001f5fa\ufe0f Architecture Diagram")
                render_mermaid(t_eval.architecture_diagram_mermaid, height=260)

            st.markdown("#### \u2696\ufe0f Rubric Breakdown")
            cols_r = st.columns(4)
            for idx, (k, r_crit) in enumerate(t_eval.rubric_scores.items()):
                with cols_r[idx]:
                    st.metric(r_crit.display_name, f"{r_crit.score} / 5.0")
                    st.caption(r_crit.feedback)

            st.markdown(t_eval.stronger_answer_outline)

            render_answer_revision_editor(session, turn, f"current_turn_{curr_idx}")

            st.markdown("---")
            is_last = (curr_idx + 1) >= session.total_questions
            btn_label = "Conclude Round & Export Report \U0001f389" if is_last else "Next Question \u27a1\ufe0f"
            if st.button(btn_label, type="primary", use_container_width=True):
                if is_last:
                    session.is_finished = True
                    session.completed_at = time.time()
                    save_session(session)
                    st.rerun()
                else:
                    session.current_turn_index += 1
                    session.in_followup = False
                    save_session(session)
                    st.rerun()


# TAB 2: AI TECHNICAL GENERATOR & DEEP-DIVE STUDIO (NEW & TECHNICAL)
# ==============================================================================
with tab_dynamic_ai:
    st.header("⚡ Build and Practice a Technical Challenge")
    st.write(
        "Choose a topic and difficulty, generate a question, write your answer, "
        "then review your score and feedback. You can edit your answer and score it again."
    )

    with st.container(border=True):
        st.subheader("1. Set up your challenge")
        col_g1, col_g2 = st.columns([2, 1])
        with col_g1:
            custom_topic = st.text_input(
                "Topic or technology",
                value="Kafka Partition Rebalancing & Consumer Lag",
                placeholder="For example: SQL indexes, Python concurrency, RAG, Redis caching",
                help="Choose one topic so the question can focus on a specific skill.",
                key="challenge_topic",
            )
        with col_g2:
            custom_difficulty = st.selectbox(
                "Difficulty",
                ["Internship / Entry-Level", "Mid-Level Engineer", "Staff / Principal Architect"],
                index=0,
                help="Choose the level you want the question to target.",
                key="challenge_difficulty",
            )

        if st.button("Generate challenge", type="primary", use_container_width=True, key="generate_dynamic_challenge"):
            if not custom_topic.strip():
                st.warning("Enter a topic before generating a challenge.")
            else:
                with st.spinner("Creating your question and evaluation guide..."):
                    dyn_q = generate_dynamic_ai_technical_question(
                        topic=custom_topic.strip(),
                        role=target_role,
                        experience_level=custom_difficulty,
                        **get_active_llm_settings(),
                    )
                    st.session_state.current_dyn_q = dyn_q
                    st.session_state.current_dyn_eval = None
                    st.session_state.current_dyn_answer = ""
                    st.rerun()

    if "current_dyn_q" in st.session_state:
        dq: QuestionItem = st.session_state.current_dyn_q

        st.markdown("---")
        st.subheader("2. Your challenge")
        st.caption(f"Topic: {dq.competency_or_topic}  ·  Role: {target_role}  ·  Level: {custom_difficulty}")
        with st.container(border=True):
            st.markdown("**Main question**")
            st.markdown(dq.question_text)

            st.markdown("**Follow-up question**")
            st.info(dq.default_followup or "Explain the trade-offs, limitations, and failure cases.")

            with st.expander("What a strong answer should cover", expanded=False):
                for hint in dq.rubric_hints:
                    st.markdown(f"- {hint}")

        st.markdown("---")
        st.subheader("3. Write or update your answer")
        st.caption(
            "Use this space to draft your response. You can change it at any time and select "
            "**Score / update feedback** again to evaluate the latest version."
        )
        answer_key = f"dyn_answer_{dq.id}"
        if answer_key not in st.session_state:
            st.session_state[answer_key] = st.session_state.get("current_dyn_answer", "")

        challenge_answer = st.text_area(
            "Your answer",
            key=answer_key,
            height=220,
            placeholder=(
                "Explain the core idea, how it works, your approach, trade-offs, edge cases, "
                "and a practical example..."
            ),
            help="Write in your own words. You can revise your response after seeing the feedback.",
        )
        word_count = len(challenge_answer.split()) if challenge_answer.strip() else 0
        st.caption(f"{word_count} words · A useful structure is: concept → approach → trade-offs → example.")

        if st.button("Score / update feedback", type="primary", use_container_width=True, key=f"score_dyn_{dq.id}"):
            if not challenge_answer.strip():
                st.warning("Write an answer before requesting feedback.")
            else:
                with st.spinner("Reviewing your answer against the interview rubric..."):
                    dyn_eval = evaluate_with_llm(
                        dq,
                        challenge_answer.strip(),
                        candidate_context=st.session_state.get("sb_candidate_context", "").strip(),
                        **get_active_llm_settings(),
                    )
                    st.session_state.current_dyn_answer = challenge_answer.strip()
                    st.session_state.current_dyn_eval = {
                        "question_id": dq.id,
                        "answer": challenge_answer.strip(),
                        "evaluation": dyn_eval,
                    }
                st.rerun()

        saved_eval = st.session_state.get("current_dyn_eval")
        if saved_eval and saved_eval.get("question_id") == dq.id:
            result = saved_eval["evaluation"]
            st.markdown("---")
            st.subheader("4. Feedback on your latest answer")
            score_col, level_col = st.columns([1, 2])
            score_col.metric("Overall practice score", f"{result.overall_score:.1f} / 5.0")
            with level_col:
                st.markdown("**What this score means**")
                st.write(
                    "4.2–5.0: Strong · 3.2–4.1: Good foundation · Below 3.2: Focus on the improvements below"
                )

            if result.key_strengths:
                st.markdown("**What you did well**")
                for item in result.key_strengths:
                    st.markdown(f"- {item}")

            if result.actionable_improvements:
                st.markdown("**What to improve next**")
                for item in result.actionable_improvements:
                    st.markdown(f"- {item}")

            if result.rubric_scores:
                st.markdown("**Rubric breakdown**")
                rubric_cols = st.columns(len(result.rubric_scores))
                for idx, rubric in enumerate(result.rubric_scores.values()):
                    with rubric_cols[idx]:
                        st.metric(rubric.display_name, f"{rubric.score:.1f} / 5")
                        st.caption(rubric.feedback)

            if result.stronger_answer_outline:
                with st.expander("Suggested answer structure", expanded=False):
                    st.markdown(result.stronger_answer_outline)

            st.caption(
                "This is practice feedback, not a hiring prediction. Your answer remains editable above; "
                "score it again after making changes."
            )

# ==============================================================================
# TAB 3: SPOT THE FLAW INTERACTIVE GAME
# ==============================================================================
with tab_flaw_game:
    st.header("🎮 Spot the Interview Flaw: Interviewer Eye Training")
    st.markdown("""
    The fastest way to sharpen your own answers is learning to spot common red flags in other candidates' responses.
    Read the sample student response below and identify the core weakness an interviewer would flag!
    """)

    flaw_scenarios = [
        {
            "id": 1,
            "title": "Scenario 1: The Group Project Disappearance",
            "prompt": "Tell me about a time you resolved a technical blocker in a team project.",
            "candidate_answer": (
                "In our software engineering capstone, we were building a full-stack web application. "
                "We encountered a nasty database deadlock issue. So we sat down together, we analyzed the logs, "
                "we rewrote the queries, and we deployed the fix to AWS. In the end, we got an A on the project."
            ),
            "options": [
                "The answer lacks personal ownership ('I' vs 'We'); the interviewer has no idea what the candidate actually did.",
                "They should have used MongoDB instead of a relational database.",
                "Mentioning that they got an 'A' grade is strictly forbidden in tech interviews.",
                "The answer is too long and contains too many technical buzzwords.",
            ],
            "correct_index": 0,
            "explanation": (
                "**Exact Flaw:** The 'We' Trap! When interviewers hear 'we analyzed, we rewrote, we deployed', "
                "they cannot verify whether the candidate did the heavy lifting or simply watched their teammate work. "
                "Always state: *'My specific responsibility was isolating the database locking queries. I wrote an EXPLAIN script, discovered the missing index on user_id, and refactored the transaction isolation level...'*."
            ),
            "improved_version": (
                "During our capstone project, our Postgres database experienced deadlocks during concurrent checkout tests. "
                "**My specific role** was isolating the locking mechanism. **I analyzed** the query logs using pg_stat_activity, "
                "**identified** an unindexed foreign key causing table-level lock escalation, and **refactored** the transaction "
                "to update rows in strict primary key order. **As a result**, concurrent test suite failures dropped from 18% to zero."
            ),
        },
        {
            "id": 2,
            "title": "Scenario 2: The Unsubstantiated Metric Trap",
            "prompt": "Describe a project where you improved system performance.",
            "candidate_answer": (
                "I worked on an e-commerce API. I noticed it was slow, so I refactored it and made it 99.9% faster, "
                "saving the company millions of dollars in server costs."
            ),
            "options": [
                "E-commerce APIs do not have latency bottlenecks.",
                "The metric (99.9% / millions of dollars) is unsubstantiated and unrealistically inflated for a student/intern project, triggering skepticism.",
                "They should have mentioned their GPA.",
                "Refactoring is not a recognized software engineering practice.",
            ],
            "correct_index": 1,
            "explanation": (
                "**Exact Flaw:** Inflated or fabricated metrics! Experienced interviewers immediately probe extreme claims like '99.9% faster' or 'saved millions'. "
                "If you cannot explain the exact before-and-after baseline (e.g. 'reduced P95 response time from 480ms to 95ms by adding Redis caching on product catalog reads'), "
                "the claim damages your credibility. Honest, concrete metrics are far more persuasive."
            ),
            "improved_version": (
                "In my portfolio web service, product catalog queries took roughly 500ms under load. "
                "I profiled the endpoints using cProfile, discovered repetitive database lookups for static category data, "
                "and implemented an in-memory Redis cache with a 10-minute TTL. This brought P95 latency down from 500ms to 85ms "
                "under a 50 RPS load test."
            ),
        },
        {
            "id": 3,
            "title": "Scenario 3: The Defensive Blame Game",
            "prompt": "Tell me about a time when a project or assignment did not meet expectations.",
            "candidate_answer": (
                "In my mobile development class, our final app failed the demo because my lab partner didn't know how to use Git. "
                "He overwrote my code at 3 AM the night before and broke the build. If he had listened to me, we would have succeeded."
            ),
            "options": [
                "Mobile apps are too easy for university classes.",
                "Blaming teammates and external circumstances reveals low emotional intelligence and zero personal accountability.",
                "Git is obsolete; they should have used SVN.",
                "They should never admit to working at 3 AM.",
            ],
            "correct_index": 1,
            "explanation": (
                "**Exact Flaw:** Throwing teammates under the bus! Interviewers assess resilience and psychological safety. "
                "Even when a teammate makes a mistake, high-performing engineers focus on preventive systems: *'What failed was our branch protection and merge review discipline. In hindsight, I should have set up GitHub branch rules and continuous integration to prevent main branch breakage...'*."
            ),
            "improved_version": (
                "During a mobile dev group project, a broken merge commit slipped into our release branch hours before our demo. "
                "While the error was introduced during late-night debugging, **I realized the root cause was our lack of team branch protection**. "
                "I stayed calm, reverted the commit using git reflog, and got our core demo working. More importantly, **I learned to establish PR branch rules and automated CI tests** at the start of every subsequent team project."
            ),
        },
        {
            "id": 4,
            "title": "Scenario 4: The Buzzword Salad",
            "prompt": "How does a hash map achieve O(1) average lookup time?",
            "candidate_answer": (
                "A hash map is a highly optimized modern cloud data structure utilizing AI-driven algorithmic hashing "
                "and microservices indexing to immediately fetch data across memory matrices in O(1)."
            ),
            "options": [
                "Hash maps are actually O(N^2) in all cases.",
                "Empty buzzword salad that avoids explaining the underlying mechanism (hash functions, bucket arrays, and collision resolution).",
                "The candidate should have mentioned Python dictionaries only.",
                "O(1) lookups are only possible with quantum computing.",
            ],
            "correct_index": 1,
            "explanation": (
                "**Exact Flaw:** Substituting buzzwords for mechanical understanding! An interviewer wants to hear: "
                "1) Key passes through a hash function generating an integer index, 2) Modulo array length maps it to a bucket, "
                "3) In case of collisions, chaining (linked lists/trees) or open addressing handles it. Avoid buzzword filler."
            ),
            "improved_version": (
                "A hash map passes the key through a hash function to produce a hash code, which is then mapped to an array bucket index via modulo. "
                "Under normal conditions, this direct array indexing allows O(1) lookups. When two keys produce the same index (a collision), "
                "it resolves them using separate chaining (linked list or balanced tree in that bucket) or open addressing. In the worst case where all keys collide into one bucket, lookup degrades to O(N)."
            ),
        },
    ]

    selected_game_id = st.selectbox(
        "Choose Challenge Scenario:",
        [f"Scenario {s['id']}: {s['title'].split(': ')[1]}" for s in flaw_scenarios],
    )
    curr_scenario = flaw_scenarios[int(selected_game_id.split()[1].replace(":", "")) - 1]

    st.markdown(f"### **{curr_scenario['title']}**")
    st.markdown(f"**Interviewer Prompt:** *\"{curr_scenario['prompt']}\"*")

    st.markdown("##### 🎙️ Candidate's Response:")
    st.info(f"\"{curr_scenario['candidate_answer']}\"")

    user_choice = st.radio(
        "What is the single biggest flaw in this answer?",
        curr_scenario["options"],
        key=f"game_choice_{curr_scenario['id']}",
    )

    if st.button("Check My Diagnosis 🔍", key=f"btn_check_{curr_scenario['id']}"):
        chosen_idx = curr_scenario["options"].index(user_choice)
        if chosen_idx == curr_scenario["correct_index"]:
            st.success("🎯 **Spot on! You diagnosed the flaw accurately.**")
        else:
            st.error("❌ Not quite. Review the diagnostic breakdown below:")

        st.markdown(curr_scenario["explanation"])

        with st.expander("✨ Compare with Structurally Elevated Model Answer", expanded=True):
            st.markdown(f"**How to rewrite this using authentic experience:**\n\n{curr_scenario['improved_version']}")


# ==============================================================================
# TAB 4: INTERACTIVE STAR STORY BUILDER
# ==============================================================================
with tab_star_builder:
    st.header("🛠️ Interactive STAR Story Builder & Workshop")
    st.markdown("""
    Convert your raw class assignments, hackathons, and personal projects into powerful, structured STAR stories.
    Follow the step-by-step wizard to craft an authentic story ready for behavioral interviews!
    """)

    col_st1, col_st2 = st.columns([1, 1])

    with col_st1:
        st.subheader("1. Input Your Authentic Project Story")

        story_title = st.text_input(
            "Project / Experience Name",
            value="Web Performance Optimization Project",
            placeholder="e.g. Distributed Key-Value Store, Hackathon Android App, OS Lab",
        )

        b_sit = st.text_area(
            "Situation (10–15%): What was the context, project goal, and deadline?",
            placeholder="During my university web development capstone, our team was building an e-commerce platform that needed to handle a simulated flash-sale demo within 3 weeks...",
            height=100,
        )

        b_task = st.text_area(
            "Task (10%): What was YOUR exact individual responsibility?",
            placeholder="My specific responsibility was identifying why API response times spiked above 1.5 seconds under concurrent load and fixing the bottleneck...",
            height=80,
        )

        b_act = st.text_area(
            "Action (60%): What concrete steps, decisions, and code did YOU write?",
            placeholder="I profiled the backend endpoints using cProfile, discovered unindexed SQL queries, and added an in-memory Redis cache with a 5-minute TTL. I also rewrote 3 redundant queries into a single JOIN...",
            height=130,
        )

        b_res = st.text_area(
            "Result (15–20%): What was the measurable outcome and key takeaway?",
            placeholder="As a result, P95 latency dropped from 1.5s to 120ms during our 100-user load test, and our demo ran flawlessly. This taught me the importance of profiling before guessing at optimizations...",
            height=90,
        )

    with col_st2:
        st.subheader("2. Real-Time Story Diagnosis & Pitch Card")

        total_words = len((b_sit + " " + b_task + " " + b_act + " " + b_res).split())
        st.metric("Total Story Length", f"{total_words} words", help="Aim for 120–250 words for a 90-second spoken answer")

        has_s = len(b_sit.strip().split()) >= 15
        has_t = len(b_task.strip().split()) >= 10
        has_a = len(b_act.strip().split()) >= 25
        has_r = len(b_res.strip().split()) >= 15

        st.markdown("##### Framework Completeness Check:")
        st.markdown(f"{'✅' if has_s else '⏳'} **Situation:** {('Clear context provided' if has_s else 'Add more details on stakes/timeline')}")
        st.markdown(f"{'✅' if has_t else '⏳'} **Task:** {('Individual role specified' if has_t else 'Clarify what YOU specifically owned')}")
        st.markdown(f"{'✅' if has_a else '⏳'} **Action:** {('Substantial technical actions' if has_a else 'Expand on your tools, choices, and logic')}")
        st.markdown(f"{'✅' if has_r else '⏳'} **Result:** {('Outcomes and lessons highlighted' if has_r else 'Add measurable results or retrospectives')}")

        if st.button("✨ Format Assembled Pitch Card", type="primary", use_container_width=True):
            if not (b_sit and b_task and b_act and b_res):
                st.warning("Fill in all four STAR fields to assemble your pitch card.")
            else:
                assembled_md = f"""
### 🎤 90-Second Interview Pitch Card: {story_title}

* **[Situation]** {b_sit.strip()}
* **[Task]** {b_task.strip()}
* **[Action]** {b_act.strip()}
* **[Result & Learning]** {b_res.strip()}

---
> **💡 Delivery Tip:** Spend 15 seconds on Situation & Task, 50 seconds walking through your Actions and technical decisions, and 20 seconds on the Result and what you learned!
                """
                st.markdown(assembled_md)
                st.download_button(
                    label="📥 Save STAR Card (.md)",
                    data=assembled_md,
                    file_name=f"star_story_{story_title.lower().replace(' ', '_')}.md",
                    mime="text/markdown",
                )


# ==============================================================================
# TAB 5: COMPREHENSIVE QUESTION BANK
# ==============================================================================
with tab_bank:
    st.header("📚 Comprehensive Interview Question Bank")
    st.markdown("Explore curated behavioral, technical, and project architecture questions across key disciplines.")

    b_type = st.radio(
        "Question Category",
        ["Behavioral Competencies (STAR)", "Role-Specific Technical Quizzes", "Project Architecture & Deep-Dive"],
        horizontal=True,
    )

    if b_type == "Behavioral Competencies (STAR)":
        st.subheader("Behavioral Prompts with Rubric Expectations")
        for q in BEHAVIORAL_QUESTIONS:
            with st.expander(f"📌 {q['competency']}: {q['question_text']}"):
                st.markdown(f"**Full Prompt:** {q['question_text']}")
                st.markdown(f"**Default Follow-up Question:** *\"{q['default_followup']}\"*")
                st.markdown("**What Interviewers Look For:**")
                for h in q["rubric_hints"]:
                    st.markdown(f"- {h}")

    elif b_type == "Role-Specific Technical Quizzes":
        st.subheader("Role-Specific Technical Question Pool")
        role_filter = st.selectbox("Select Domain:", list(TECHNICAL_QUESTIONS_BY_ROLE.keys()))
        t_list = TECHNICAL_QUESTIONS_BY_ROLE.get(role_filter, [])
        for q in t_list:
            with st.expander(f"⚙️ {q['topic']}: {q['question_text']}"):
                st.markdown(f"**Prompt:** {q['question_text']}")
                st.markdown(f"**Follow-Up Challenge:** *\"{q['default_followup']}\"*")
                st.markdown("**Core Technical Rubric Hints:**")
                for h in q["rubric_hints"]:
                    st.markdown(f"- {h}")

    else:
        st.subheader("Project Architecture & Engineering Retrospective Bank")
        for q in PROJECT_QUESTIONS:
            with st.expander(f"🏗️ {q['competency']}: {q['question_text']}"):
                st.markdown(f"**Architecture Prompt:** {q['question_text']}")
                st.markdown(f"**Follow-Up Probe:** *\"{q['default_followup']}\"*")
                st.markdown("**Architectural Expectations:**")
                for h in q["rubric_hints"]:
                    st.markdown(f"- {h}")


# ==============================================================================
# TAB 6: SYSTEM DESIGN & ENGINEERING PLAYBOOKS
# ==============================================================================
with tab_playbook:
    st.header("📖 System Design & Engineering Playbooks")
    st.markdown("Actionable reference guides to elevate your technical communication and interview confidence.")

    playbook_choice = st.selectbox(
        "Select Playbook:",
        [
            "Technical Architecture Trade-offs Matrix",
            "The 60-Second 'Tell Me About Yourself' Formula",
            "Top 8 Student Interview Trap Questions & How to Answer",
            "Pre-Interview Mental Reset & Body Language Checklist",
        ],
    )

    if playbook_choice == "Technical Architecture Trade-offs Matrix":
        st.markdown("### ⚖️ The Core Systems Engineering Trade-off Matrix")
        st.write("In technical interviews, there are no 'best' technologies—only trade-offs. Memorize these pairings:")

        tradeoff_data = [
            {"Technology Pair": "SQL (Relational) vs NoSQL (Document/KV)", "When to Choose Option A": "Strict ACID guarantees, complex joins, transactional financial records", "When to Choose Option B": "Flexible schema, high horizontal write throughput, document hierarchical data"},
            {"Technology Pair": "REST vs GraphQL", "When to Choose Option A": "Standard HTTP caching, simple predictable endpoints, lightweight clients", "When to Choose Option B": "Complex graph relationships, mobile clients needing zero over-fetching"},
            {"Technology Pair": "Monolith vs Microservices", "When to Choose Option A": "Early stage, small team (<15 engineers), rapid prototyping, simple deployments", "When to Choose Option B": "Independent scaling boundaries, large distinct teams, isolated failure blast radius"},
            {"Technology Pair": "Pessimistic vs Optimistic Locking", "When to Choose Option A": "High contention, frequent conflicting updates (prevents rollbacks)", "When to Choose Option B": "Low-to-medium contention, high read ratio, minimizes database row locks"},
            {"Technology Pair": "Client-Side (CSR) vs Server-Side (SSR)", "When to Choose Option A": "Rich internal interactive dashboards, lower server CPU usage", "When to Choose Option B": "Public search engine optimization (SEO), fast First Contentful Paint on mobile"},
        ]
        st.table(pd.DataFrame(tradeoff_data))

    elif playbook_choice == "The 60-Second 'Tell Me About Yourself' Formula":
        st.markdown("""
        ### ⏱️ The 3-Part "Present → Past → Future" Elevator Pitch

        Most students ramble through their high school resume or repeat their GPA. Use this 3-part framework instead:

        1. **Present (20s):** Who you are, your degree/focus, and your flagship project.
           > *"I'm a senior in Computer Science at State University, focusing on backend systems and distributed databases. Most recently, I built a high-throughput key-value store in Go with raft consensus..."*

        2. **Past (20s):** What ignited your technical curiosity and the core problems you love solving.
           > *"I fell in love with systems programming during an operating systems lab where we built a virtual memory manager from scratch. Since then, I've enjoyed diving into profiling, caching, and performance optimization..."*

        3. **Future (20s):** Why THIS specific company and team excites you.
           > *"I've followed your engineering blog posts on your migration to Kubernetes microservices, and I'd love to bring my systems foundation and curiosity to your infrastructure engineering team."*
        """)

    elif playbook_choice == "Top 8 Student Interview Trap Questions & How to Answer":
        st.markdown("""
        ### 🚨 Trap Questions & Authentic Formulas

        #### 1. "What is your greatest technical weakness?"
        - ❌ **Wrong:** *"I'm a perfectionist and work too hard."* (Generic cliché).
        - ✅ **Formula:** A real technical area you're actively learning + proof of growth.
          > *"Because my coursework focused heavily on backend algorithms in C and Java, I initially lacked frontend experience with modern build tools like Webpack and React state management. Over the past two semesters, I took a frontend elective and built an interactive dashboard to bridge that gap."*

        #### 2. "Why did you choose PostgreSQL over MongoDB for your project?"
        - ❌ **Wrong:** *"Because my professor told me to"* or *"Because Postgres is better."*
        - ✅ **Formula:** Constraint-driven justification.
          > *"Our data model had strict relational foreign keys between users, orders, and payment items. We needed transactional ACID guarantees to prevent inventory race conditions, which made Postgres the natural fit over a document store."*

        #### 3. "Have you ever disagreed with an engineering decision?"
        - ❌ **Wrong:** *"No, I get along with everyone."* (Indicates passive conformity).
        - ✅ **Formula:** Respectful debate grounded in empirical benchmarks.
          > *"Yes. In a group project, a teammate wanted to build custom auth from scratch. I advocated for using an established OAuth/JWT library due to security risks. I prepared a 10-minute comparison showing maintenance cost and vulnerability history, and we agreed to use the standard library."*
        """)

    else:
        st.markdown("""
        ### 🧘 Pre-Interview 10-Minute Confidence Routine

        1. **Physical Posture Check:** Sit up straight with shoulders relaxed. Leaning slightly forward signals active engagement.
        2. **The "Pause-and-Breathe" Technique:** When an interviewer asks a complex question, pause for 3 full seconds. Say: *"That's a great question. Let me take a moment to organize my thoughts."* This eliminates 'um', 'uh', and rambling.
        3. **Have 3 Flagship Projects at Hand:** Write down the 1 hardest bug for each project on a sticky note next to your monitor.
        4. **Eye Contact & Camera Alignment:** Look directly at the webcam when concluding your points to convey natural presence.
        """)


# ==============================================================================
# TAB 7: PRACTICE ANALYTICS & HISTORY
# ==============================================================================
with tab_analytics:
    st.header("📊 Student Practice Analytics & Local History")
    st.caption("All practice history is saved securely in your local SQLite database (`interview_iq.db`).")

    analytics = get_aggregate_analytics()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Sessions", analytics["total_sessions"])
    with col_m2:
        st.metric("Answers Logged", analytics["total_answers_submitted"])
    with col_m3:
        st.metric("Avg Session Score", f"{analytics['avg_session_score']} / 5.0")
    with col_m4:
        st.metric("Structure Average", f"{analytics['avg_structure']} / 5.0")

    st.markdown("---")
# ==============================================================================
# TAB 8: EXPORT PRACTICE REPORT
# ==============================================================================
with tab_report:
    st.header("📑 Export Practice Report")
    st.caption("Generate professional Markdown, printable HTML / PDF, and JSON summaries of your session.")

    current_sess = st.session_state.session
    if not current_sess:
        st.info("Start or complete an interview session to export your personalized diagnostic report.")
    else:
        md_report = generate_markdown_report(current_sess)
        html_report = generate_html_report(current_sess)
        json_report = json.dumps(current_sess.to_dict(), indent=2)

        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            st.download_button(
                label="📥 Download Markdown (.md)",
                data=md_report,
                file_name=f"interview_report_{current_sess.session_id}.md",
                mime="text/markdown",
                use_container_width=True,
            )
        with col_d2:
            st.download_button(
                label="🖨️ Download Printable HTML / PDF (.html)",
                data=html_report,
                file_name=f"interview_report_{current_sess.session_id}.html",
                mime="text/html",
                use_container_width=True,
            )
        with col_d3:
            st.download_button(
                label="📦 Download Raw JSON (.json)",
                data=json_report,
                file_name=f"interview_session_{current_sess.session_id}.json",
                mime="application/json",
                use_container_width=True,
            )

        st.markdown("---")
# ==============================================================================
# TAB 9: TRANSPARENT RUBRIC & ETHICAL GUARDRAILS
# ==============================================================================
with tab_rubric:
    st.header("⚖️ Transparent Rubric & Ethical Guardrails")
    st.markdown("""
    InterviewIQ believes that AI should empower students through **transparent criteria**
    and **ethical feedback**, rather than opaque 'pass/fail' black boxes.
    """)

    st.subheader("1. The 4-Part Visible Scoring Rubric")
    for crit_key, meta in RUBRIC_CRITERIA_META.items():
        with st.expander(f"📌 {meta['display_name']} (1.0 to 5.0)"):
            st.markdown(f"**Definition:** {meta['description']}")
            st.markdown("**Scoring Anchors:**")
            for lvl, text in meta["anchors"].items():
                st.markdown(f"- **Level {lvl}:** {text}")

    st.markdown("---")
