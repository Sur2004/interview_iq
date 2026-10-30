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
import re

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
from backend.browser_store import session_from_dict, session_summaries, analytics_from_sessions
from backend.report_generator import (
    generate_markdown_report,
    generate_html_report,
)
from backend.config import get_llm_config
from backend.career_review import (extract_resume_pdf, fetch_public_repository, evaluate_candidate_materials, calculate_ats_score, generate_resume_based_questions)
from backend.speech import transcribe_audio

# Page configuration
st.set_page_config(
    page_title="InterviewIQ - AI Technical Interview Studio",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

interview_monitor = components.declare_component("interviewiq_interview_monitor", path="components/interview_monitor_v2")
browser_store = components.declare_component("interviewiq_browser_store", path="components/browser_store")
_browser_read = browser_store(action="read", payload="", key="browser_store_reader")
if isinstance(_browser_read, dict) and not st.session_state.get("browser_data_loaded"):
    st.session_state.browser_data = {
        "profiles": _browser_read.get("profiles", {}) if isinstance(_browser_read.get("profiles", {}), dict) else {},
        "sessions": _browser_read.get("sessions", {}) if isinstance(_browser_read.get("sessions", {}), dict) else {},
    }
    st.session_state.browser_data_loaded = True
elif "browser_data" not in st.session_state:
    st.session_state.browser_data = {"profiles": {}, "sessions": {}}
if st.session_state.get("browser_data_dirty"):
    browser_store(
        action="write",
        payload=json.dumps(st.session_state.get("browser_data", {"profiles": {}, "sessions": {}}), ensure_ascii=False),
        key="browser_store_writer",
    )
    st.session_state.browser_data_dirty = False

# Minimal, accessible visual system
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
    :root { --iq-ink:#172033; --iq-muted:#667085; --iq-border:#e5e7eb; --iq-surface:#fff; --iq-soft:#f8fafc; --iq-accent:#3157d5; --iq-accent-soft:#eef2ff; }
    html, body, [class*="css"], [data-testid="stAppViewContainer"] { font-family:'DM Sans',-apple-system,BlinkMacSystemFont,sans-serif; }
    code, pre, [data-testid="stCode"] { font-family:'IBM Plex Mono',ui-monospace,monospace !important; }
    .block-container { max-width:1240px; padding-top:2rem; padding-bottom:3rem; }
    [data-testid="stSidebar"] { border-right:1px solid var(--iq-border); }
    [data-testid="stSidebar"] > div:first-child { padding-top:1.4rem; }
    /* Clear, scrollable workspace navigation */
    [data-testid="stTabs"] { margin-top: 1rem; }
    /* Streamlit/BaseWeb versions use different tab-list wrappers; target both. */
    [data-testid="stTabs"] [role="tablist"],
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        position: sticky; top: 0; z-index: 20;
        display: flex !important; flex-wrap: nowrap !important;
        gap: .35rem; width: 100%; max-width: 100%;
        overflow-x: auto !important; overflow-y: hidden !important;
        padding: .55rem .5rem; margin: 0 0 1.15rem;
        box-sizing: border-box;
        background: rgba(255,255,255,.97);
        border: 1px solid var(--iq-border); border-radius: 14px;
        box-shadow: 0 3px 12px rgba(15,23,42,.04);
        scrollbar-width: thin; scrollbar-color: #cbd5e1 transparent;
        -webkit-overflow-scrolling: touch; overscroll-behavior-x: contain;
        scroll-behavior: smooth;
    }
    [data-testid="stTabs"] [role="tablist"] > div,
    [data-testid="stTabs"] [data-baseweb="tab-list"] > div {
        flex: 0 0 auto !important; flex-wrap: nowrap !important;
        width: max-content !important; min-width: max-content !important;
    }
    [data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar,
    [data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar { height: 5px; }
    [data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar-thumb,
    [data-testid="stTabs"] [data-baseweb="tab-list"]::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 999px; }
    [data-testid="stTabs"] button[role="tab"] {
        flex: 0 0 auto; white-space: nowrap;
        min-height: 40px; padding: .55rem .85rem;
        border: 1px solid transparent; border-radius: 9px;
        color: var(--iq-muted); font-size: .88rem; font-weight: 600;
        transition: background .15s ease, color .15s ease, border-color .15s ease;
    }
    [data-testid="stTabs"] button[role="tab"]:hover {
        background: var(--iq-soft); color: var(--iq-ink);
        border-color: var(--iq-border);
    }
    [data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        color: var(--iq-accent); background: var(--iq-accent-soft);
        border-color: #c7d2fe;
    }
    [data-testid="stTabs"] button[role="tab"]:focus-visible {
        outline: 2px solid var(--iq-accent); outline-offset: 2px;
    }
    @media (max-width: 700px) {
        [data-testid="stTabs"] [role="tablist"] { top: 0; padding: .4rem; }
        [data-testid="stTabs"] button[role="tab"] { min-height: 38px; padding: .5rem .7rem; font-size: .82rem; }
    }
    .hero-banner-sky { background:var(--iq-surface); border:1px solid var(--iq-border); border-radius:18px; padding:30px 34px; color:var(--iq-ink); margin:0 0 22px; box-shadow:0 8px 28px rgba(15,23,42,.04); }
    .hero-title { font-size:clamp(1.9rem,3vw,2.5rem); line-height:1.15; font-weight:700; letter-spacing:-.045em; color:var(--iq-ink); margin-bottom:8px; }
    .hero-subtitle { font-size:1rem; color:var(--iq-muted); max-width:760px; line-height:1.65; }
    .tech-tag { display:inline-block; background:var(--iq-soft); color:#475467; border:1px solid var(--iq-border); border-radius:999px; padding:5px 10px; font-size:.76rem; margin:5px 5px 0 0; }
    .ai-online-badge { display:inline-block; background:var(--iq-accent-soft); color:var(--iq-accent); border:1px solid #dbe3ff; padding:6px 11px; border-radius:999px; font-size:.74rem; font-weight:700; letter-spacing:.04em; }
    .animated-question-card, .animated-followup-card, .telemetry-card { background:var(--iq-surface); border:1px solid var(--iq-border); border-radius:14px; padding:22px 24px; color:var(--iq-ink); box-shadow:0 4px 16px rgba(15,23,42,.035); margin-bottom:16px; animation:none !important; }
    .animated-followup-card { background:var(--iq-soft); }
    .telemetry-card h4 { color:var(--iq-ink) !important; } .telemetry-card p { color:var(--iq-muted) !important; }
    .notice-card-sky { background:#f8fafc; border:1px solid var(--iq-border); border-left:3px solid #94a3b8; padding:13px 16px; border-radius:10px; font-size:.88rem; color:#475467; margin:12px 0; }
    .ethics-card-sky { background:#f8fafc; border:1px solid var(--iq-border); border-left:3px solid #64748b; padding:13px 16px; border-radius:10px; font-size:.86rem; color:#475467; margin:12px 0 22px; }
    .score-badge-sky { font-size:.92rem; font-weight:700; padding:6px 12px; border-radius:999px; display:inline-block; background:var(--iq-accent-soft); color:var(--iq-accent); border:1px solid #dbe3ff; }
    .pacing-chip { display:inline-block; font-size:.8rem; font-weight:600; padding:4px 9px; border-radius:7px; margin-left:6px; }
    .pacing-ok { background:#ecfdf3; color:#027a48; border:1px solid #abefc6; } .pacing-warn { background:#fff7ed; color:#b54708; border:1px solid #fed7aa; }
    button[kind="primary"] { border-radius:10px; font-weight:650; min-height:2.65rem; }
    [data-testid="stTabs"] [role="tab"] { font-weight:600; padding-top:.75rem; padding-bottom:.75rem; }
    [data-testid="stMetric"] { background:var(--iq-soft); border:1px solid var(--iq-border); border-radius:12px; padding:12px 14px; }
    input, textarea, [data-baseweb="select"] > div { border-radius:9px !important; }
    button:focus-visible, a:focus-visible, input:focus-visible, textarea:focus-visible { outline:3px solid #a5b4fc !important; outline-offset:2px !important; }
    @media (max-width:800px) { .block-container { padding-top:1rem; padding-left:1rem; padding-right:1rem; } .hero-banner-sky { padding:22px 20px; } .hero-title { font-size:1.8rem; } }
    @media (prefers-reduced-motion:reduce) { *,*::before,*::after { animation-duration:.01ms !important; animation-iteration-count:1 !important; scroll-behavior:auto !important; transition-duration:.01ms !important; } }
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



# Candidate ID + PIN access. Profiles remain local to this browser.
from backend.candidate_auth import generate_candidate_id, hash_pin, verify_pin
if "authenticated_candidate_id" not in st.session_state:
    st.session_state.authenticated_candidate_id = ""
if not st.session_state.get("browser_data_loaded"):
    st.info("Loading your browser-local InterviewIQ profiles…")
    st.stop()
if not st.session_state.authenticated_candidate_id:
    st.markdown("## InterviewIQ Candidate Access")
    st.caption("Create a candidate ID or sign in. Profiles and interview history are stored in this browser only.")
    create_tab, login_tab = st.tabs(["Create Candidate ID", "Sign in"])
    with create_tab:
        with st.form("create_candidate_profile", clear_on_submit=True):
            new_name = st.text_input("Candidate name", max_chars=80)
            new_pin = st.text_input("Create a 6-digit PIN", type="password", max_chars=6)
            confirm_pin = st.text_input("Confirm PIN", type="password", max_chars=6)
            create_submit = st.form_submit_button("Create Candidate ID", type="primary", use_container_width=True)
        if create_submit:
            clean_name = new_name.strip()
            if not clean_name:
                st.error("Enter your name.")
            elif not (new_pin.isdigit() and len(new_pin) == 6):
                st.error("PIN must contain exactly 6 digits.")
            elif new_pin != confirm_pin:
                st.error("The PINs do not match.")
            else:
                data = st.session_state.setdefault("browser_data", {"profiles": {}, "sessions": {}})
                profiles = data.setdefault("profiles", {})
                candidate_id = generate_candidate_id(profiles)
                salt, pin_digest = hash_pin(new_pin)
                profiles[candidate_id] = {"candidate_id": candidate_id, "name": clean_name, "pin_salt": salt, "pin_hash": pin_digest, "created_at": time.time()}
                data.setdefault("sessions", {}).setdefault(candidate_id, [])
                st.session_state.authenticated_candidate_id = candidate_id
                st.session_state.authenticated_email = candidate_id
                st.session_state.browser_data_dirty = True
                st.session_state.new_candidate_id_notice = candidate_id
                st.rerun()
    with login_tab:
        with st.form("candidate_login"):
            candidate_id_input = st.text_input("Candidate ID", placeholder="IQ-XXXXXXXX")
            pin_input = st.text_input("6-digit PIN", type="password", max_chars=6)
            login_submit = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if login_submit:
            profiles = st.session_state.get("browser_data", {}).get("profiles", {})
            normalized_id = candidate_id_input.strip().upper()
            profile = profiles.get(normalized_id)
            if not profile or not verify_pin(pin_input, profile.get("pin_salt", ""), profile.get("pin_hash", "")):
                st.error("Candidate ID or PIN is incorrect. Profiles are available only in the browser where they were created.")
            else:
                st.session_state.authenticated_candidate_id = normalized_id
                st.session_state.authenticated_email = normalized_id
                st.session_state.sb_candidate_name = profile.get("name", "Student Candidate")
                st.session_state.session = None
                st.rerun()
    st.stop()

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
        "Groq Cloud — GPT-OSS 120B": "groq",
        "Google Gemini 3.8 Flash (Free tier available)": "gemini",
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
        "groq": "openai/gpt-oss-120b",
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
                persist_browser_session(session)
            st.success("Revision saved to session history and feedback updated.")
            st.rerun()




def persist_browser_data() -> None:
    """Write the current user's data to browser localStorage, not a server database."""
    st.session_state.browser_data_dirty = True


def persist_browser_session(session: InterviewSession) -> None:
    """Persist a session snapshot under the verified email in browser localStorage."""
    # Keep a single local browser profile in guest mode.
    email = st.session_state.get("authenticated_candidate_id") or st.session_state.get("authenticated_email", "local_guest")
    data = st.session_state.setdefault("browser_data", {"profiles": {}, "sessions": {}})
    all_sessions = data.setdefault("sessions", {}).setdefault(email, [])
    snapshot = session.to_dict()
    for index, saved in enumerate(all_sessions):
        if saved.get("session_id") == session.session_id:
            all_sessions[index] = snapshot
            break
    else:
        all_sessions.append(snapshot)
    profile = data.setdefault("profiles", {}).setdefault(email, {})
    profile["name"] = session.candidate_name
    profile["target_role"] = session.target_role
    profile["experience_level"] = session.experience_level
    profile["interview_type"] = session.interview_type
    profile["last_seen"] = time.time()
    persist_browser_data()


# Guest mode: no sign-in or email verification required.
_active_email = st.session_state.get("authenticated_candidate_id") or st.session_state.get("authenticated_email", "local_guest")
if st.session_state.get("session") is None:
    _saved_rows = session_summaries(st.session_state.get("browser_data", {}), _active_email)
    _unfinished = [row for row in _saved_rows if not row.get("is_finished")]
    if _unfinished:
        try:
            st.session_state.session = session_from_dict(_unfinished[-1])
        except (KeyError, TypeError, ValueError):
            st.session_state.session = None


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

    st.markdown("---")
    active_candidate_id = st.session_state.get("authenticated_candidate_id", "")
    if active_candidate_id:
        active_profile = st.session_state.get("browser_data", {}).get("profiles", {}).get(active_candidate_id, {})
        st.caption(f"Signed in: {active_profile.get('name', 'Candidate')}")
        st.code(active_candidate_id, language=None)
    if st.session_state.get("new_candidate_id_notice"):
        st.success(f"Save your Candidate ID: {st.session_state.new_candidate_id_notice}")
        st.session_state.pop("new_candidate_id_notice", None)
    st.subheader("\U0001f9ed Navigate InterviewIQ")
    st.caption("Choose a section first, then configure your interview below.")
    section_labels = {
        "mock_interview": "\U0001f3af  Practice: Mock Interview",
        "technical_challenge": "\u26a1  Practice: Technical Challenge",
        "question_bank": "\U0001f4da  Learn: Question Bank",
        "system_design": "\U0001f4d6  Learn: System Design",
        "star_builder": "\U0001f6e0\ufe0f  Practice: STAR Builder",
        "spot_the_flaw": "\U0001f3ae  Practice: Spot the Flaw",
        "progress": "\U0001f4ca  Progress & Performance",
        "export_report": "\U0001f4d1  Reports: Export Results",
        "rubric_guide": "\u2696\ufe0f  Learn: Scoring Rubric",
        "resume_review": "\U0001f4c4  Resume & Project Review",
    }
    active_section = st.selectbox(
        "Open a section",
        options=list(section_labels.keys()),
        format_func=lambda key: section_labels[key],
        key="workspace_navigation",
        label_visibility="collapsed",
        help="Choose a section to open it in the main workspace.",
    )
    st.caption("Select any section above to open it. Your session settings remain below.")
    st.markdown("---")

    with st.expander("⚙️ Interview Setup", expanded=(active_section == "mock_interview")):
        st.subheader("\u2699\ufe0f Session Setup")
    
        _active_user_id = st.session_state.get("authenticated_candidate_id") or st.session_state.get("authenticated_email", "local_guest")
        _active_profile = st.session_state.get("browser_data", {}).get("profiles", {}).get(_active_user_id, {})
        candidate_name = st.text_input(
            "Your Name",
            value=_active_profile.get("name", "Student Candidate"),
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
        with st.container(border=True):
            st.caption("LLM Provider & API Key")
            provider_opts = [
                "Auto (via .env / Secrets)",
                "Groq Cloud — GPT-OSS 120B",
                "Google Gemini 3.8 Flash (Free tier available)",
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
                session_id=uuid.uuid4().hex,
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
            st.session_state.pop("integrity_termination_reason", None)
            st.session_state.pop("session_ended_early", None)
            st.session_state.session = new_sess
            persist_browser_session(new_sess)
            st.success(f"\u2705 Round started - {len(questions)} questions queued!")
            st.rerun()
    
        if st.session_state.session and not st.session_state.session.is_finished:
            st.markdown("---")
            if st.button("\u23f9\ufe0f End Session Early", use_container_width=True):
                active_session = st.session_state.session
                active_session.is_finished = True
                active_session.completed_at = time.time()
                scored = [turn.turn_evaluation or turn.initial_evaluation for turn in active_session.turns]
                scored = [item for item in scored if item is not None]
                if scored:
                    active_session.overall_session_score = round(sum(item.overall_score for item in scored) / len(scored), 1)
                st.session_state["session_ended_early"] = True
                persist_browser_session(active_session)
                st.rerun()
    
    
    st.markdown("---")
    st.page_link("pages/1_History.py", label="\U0001f4da History & Performance", icon="\U0001f4ca")
    if active_candidate_id:
        st.markdown("---")
        if st.button("Sign out", key="candidate_sign_out", use_container_width=True):
            st.session_state.authenticated_candidate_id = ""
            st.session_state.authenticated_email = ""
            st.session_state.session = None
            st.session_state.pop("sb_candidate_name", None)
            st.session_state.pop("session_ended_early", None)
            st.rerun()


# ==============================================================================
# Minimal product header
st.markdown("""
<div class="hero-banner-sky">
    <div style="display:flex;justify-content:space-between;align-items:center;gap:20px;flex-wrap:wrap;">
        <div>
            <div class="hero-title">InterviewIQ</div>
            <div class="hero-subtitle">
                Build interview confidence through realistic practice, focused follow-up questions,
                and feedback you can act on.
            </div>
            <div style="margin-top:12px;">
                <span class="tech-tag">Structured feedback</span>
                <span class="tech-tag">Technical &amp; behavioral</span>
                <span class="tech-tag">Offline mode available</span>
            </div>
        </div>
        <div><span class="ai-online-badge">PRACTICE WORKSPACE</span></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown(
    f'<div class="notice-card-sky"><strong>\u2139\ufe0f Rubric Notice:</strong> {RUBRIC_DISCLAIMER}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="ethics-card-sky"><strong>\U0001f6e1\ufe0f Anti-Fabrication:</strong> {ETHICAL_OUTLINE_GUIDELINE}</div>',
    unsafe_allow_html=True,
)


# ==============================================================================
# TAB 1: MOCK INTERVIEW STUDIO
# ==============================================================================
if active_section == "mock_interview":
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
        termination_reason = st.session_state.get("integrity_termination_reason")
        if termination_reason:
            st.error(f"**Interview session terminated:** {termination_reason}")
        elif st.session_state.get("session_ended_early"):
            st.info("This interview was ended early by you. Submitted answers have been saved to browser history.")
        else:
            st.success("\\U0001f389 **Interview Round Completed!** Full diagnostic transcript compiled below.")

        valid_turns = [t for t in session.turns if t.turn_evaluation]
        if valid_turns:
            avg_score = round(sum(t.turn_evaluation.overall_score for t in valid_turns) / len(valid_turns), 1)
            session.overall_session_score = avg_score
            persist_browser_session(session)

            col_sc1, col_sc2, col_sc3 = st.columns([1, 1, 2])
            with col_sc1:
                st.markdown(f"**Round summary:** {len(valid_turns)} of {session.total_questions} questions scored · {session.target_role}")
            turn_scores = [
                {"Question": f"Q{idx + 1}", "Score": (turn.turn_evaluation or turn.initial_evaluation).overall_score}
                for idx, turn in enumerate(session.turns)
                if (turn.turn_evaluation or turn.initial_evaluation)
            ]
            if turn_scores:
                st.markdown("#### Score by question")
                st.line_chart(pd.DataFrame(turn_scores).set_index("Question"), y="Score", use_container_width=True)

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
                        st.markdown("#### Rubric breakdown")
                        rubric_rows = [{"Criterion": item.display_name, "Score": item.score} for item in t_eval.rubric_scores.values()]
                        if rubric_rows:
                            st.bar_chart(pd.DataFrame(rubric_rows).set_index("Criterion"), y="Score", use_container_width=True)
                            for item in t_eval.rubric_scores.values():
                                st.markdown(f"**{item.display_name}: {item.score:.1f}/5** — {item.feedback}")
                        st.markdown(t_eval.stronger_answer_outline)
                    render_answer_revision_editor(session, turn, f"finished_turn_{i}")
        else:
            st.warning("Session completed without submitted responses.")

        if st.button("\U0001f504 Start Fresh Practice Round"):
            st.session_state.session = None
            st.session_state.pop("session_ended_early", None)
            st.session_state.pop("integrity_termination_reason", None)
            st.rerun()

    else:
        # ACTIVE INTERVIEW ROUND IN PROGRESS
        st.markdown("### 🎙️ Audio + Text Interview Mode")
        if st.button("⏹️ End this interview now", key="end_interview_from_workspace"):
            session.is_finished = True
            session.completed_at = time.time()
            scored = [turn.turn_evaluation or turn.initial_evaluation for turn in session.turns]
            scored = [item for item in scored if item is not None]
            if scored:
                session.overall_session_score = round(sum(item.overall_score for item in scored) / len(scored), 1)
            st.session_state["session_ended_early"] = True
            persist_browser_session(session)
            st.rerun()
        st.info("Answer by audio or text. Audio transcription needs a working connection to a configured provider, so use typed answers if recording/transcription fails. A detected browser-tab/window visibility change terminates the round. Detection is not foolproof and normal browser apps cannot block every switch.")
        monitor_status = interview_monitor(key="interviewiq_monitor", default={"camera": "starting", "tab_switches": 0})
        if isinstance(monitor_status, dict):
            camera_status = monitor_status.get("camera", "starting")
            switch_count = int(monitor_status.get("tab_switches", 0) or 0)
            if camera_status == "active":
                st.success("Camera is on")
            elif camera_status == "denied":
                st.warning("Camera permission is unavailable. Allow camera permission and reload.")
            else:
                st.caption("Waiting for camera permission…")
            st.metric("Tab switches detected", switch_count)
            if switch_count:
                session.is_finished = True
                session.completed_at = time.time()
                st.session_state["integrity_termination_reason"] = (
                    f"Session terminated after {switch_count} browser visibility change(s)."
                )
                persist_browser_session(session)
                st.error(
                    "Interview session terminated because a browser tab/window visibility change was detected. "
                    "A normal browser app cannot technically block tab switching, and detection is not foolproof."
                )
                st.rerun()
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
            st.markdown("#### 🎙️ Answer the Question")
            st.caption("Record an audio answer or type your response below. Use text if your microphone, transcription, or connection to the speech provider fails.")
            audio_answer = st.audio_input("Record your answer (optional)", key="audio_answer_" + str(curr_idx))
            if audio_answer is not None:
                st.audio(audio_answer)
            typed_answer = st.text_area(
                "Or type your answer",
                key="typed_answer_" + str(curr_idx),
                height=140,
                placeholder="Enter your answer here if you cannot record or transcribe audio.",
            )

            if st.button("Submit Typed Answer", use_container_width=True, key="submit_typed_" + str(curr_idx)):
                if not typed_answer.strip():
                    st.warning("Type an answer before submitting.")
                else:
                    turn.initial_answer = typed_answer.strip()
                    try:
                        with st.spinner("Evaluating your answer and generating a follow-up…"):
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
                            persist_browser_session(session)
                            st.rerun()
                    except (ValueError, RuntimeError) as exc:
                        st.error(f"Evaluation failed: {exc}. Check your connection/provider or try again.")

            if st.button("Transcribe & Submit Answer", type="primary", use_container_width=True, key="submit_audio_" + str(curr_idx)):
                if audio_answer is None:
                    st.warning("Record an audio answer, or use the typed-answer option above.")
                else:
                    try:
                        settings = get_active_llm_settings()
                        transcript = transcribe_audio(
                            audio_answer.getvalue(),
                            getattr(audio_answer, "type", None) or "audio/wav",
                            settings.get("provider", "heuristic"),
                            settings.get("api_key"),
                            settings.get("model_name"),
                        )
                        turn.initial_answer = transcript
                        with st.spinner("Evaluating your spoken answer and generating a follow-up…"):
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
                            persist_browser_session(session)
                            st.rerun()
                    except (ValueError, RuntimeError) as exc:
                        st.error(f"Audio transcription or evaluation failed: {exc}. You can still submit a typed answer.")

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

            st.markdown("#### 🎙️ Answer the Follow-Up")
            st.caption("Record a follow-up answer or type it if audio recording/transcription is unavailable.")
            followup_audio = st.audio_input("Record your follow-up answer (optional)", key="followup_audio_" + str(curr_idx))
            if followup_audio is not None:
                st.audio(followup_audio)
            typed_followup = st.text_area(
                "Or type your follow-up answer",
                key="typed_followup_" + str(curr_idx),
                height=120,
                placeholder="Type your response here if audio is unavailable.",
            )
            if st.button("Submit Typed Follow-Up & Score Turn", use_container_width=True, key="submit_typed_followup_" + str(curr_idx)):
                if not typed_followup.strip():
                    st.warning("Type a follow-up answer before submitting.")
                else:
                    turn.followup_answer = typed_followup.strip()
                    try:
                        with st.spinner("Scoring your answers against the four-part rubric…"):
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
                            persist_browser_session(session)
                            st.rerun()
                    except (ValueError, RuntimeError) as exc:
                        st.error(f"Evaluation failed: {exc}. Check your connection/provider or try again.")

            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                if st.button("Transcribe Follow-Up & Score Turn 🎯", type="primary", use_container_width=True, key="submit_followup_audio_" + str(curr_idx)):
                    if followup_audio is None:
                        st.warning("Record a follow-up answer, or use the typed-answer option above.")
                    else:
                        try:
                            settings = get_active_llm_settings()
                            transcript = transcribe_audio(
                                followup_audio.getvalue(),
                                getattr(followup_audio, "type", None) or "audio/wav",
                                settings.get("provider", "heuristic"),
                                settings.get("api_key"),
                                settings.get("model_name"),
                            )
                            turn.followup_answer = transcript
                            st.markdown("**Follow-up transcript to be evaluated**")
                            st.write(transcript)
                            with st.spinner("Scoring your spoken answers against the four-part rubric…"):
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
                                persist_browser_session(session)
                                st.rerun()
                        except (ValueError, RuntimeError) as exc:
                            st.error(str(exc))
            with col_f2:
                if st.button("Skip Follow-Up", use_container_width=True):
                    turn.followup_answer = "[Skipped]"
                    turn.turn_evaluation = turn.initial_evaluation
                    turn.completed = True
                    session.in_followup = False
                    persist_browser_session(session)
                    st.rerun()

        elif turn.completed and turn.turn_evaluation:
            t_eval = turn.turn_evaluation
            st.markdown("### Turn diagnostic results")
            st.markdown(f"**Overall score:** {t_eval.overall_score:.1f} / 5.0")

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

            st.markdown("#### Rubric breakdown")
            rubric_rows = [{"Criterion": item.display_name, "Score": item.score} for item in t_eval.rubric_scores.values()]
            if rubric_rows:
                st.bar_chart(pd.DataFrame(rubric_rows).set_index("Criterion"), y="Score", use_container_width=True)
                for item in t_eval.rubric_scores.values():
                    st.markdown(f"**{item.display_name}: {item.score:.1f}/5** — {item.feedback}")

            st.markdown(t_eval.stronger_answer_outline)

            render_answer_revision_editor(session, turn, f"current_turn_{curr_idx}")

            st.markdown("---")
            is_last = (curr_idx + 1) >= session.total_questions
            btn_label = "Conclude Round & Export Report \U0001f389" if is_last else "Next Question \u27a1\ufe0f"
            if st.button(btn_label, type="primary", use_container_width=True):
                if is_last:
                    session.is_finished = True
                    session.completed_at = time.time()
                    persist_browser_session(session)
                    st.rerun()
                else:
                    session.current_turn_index += 1
                    session.in_followup = False
                    persist_browser_session(session)
                    st.rerun()


# TAB 2: AI TECHNICAL GENERATOR & DEEP-DIVE STUDIO (NEW & TECHNICAL)
# ==============================================================================
if active_section == "technical_challenge":
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
                    focus_angles = [
                        "production incident diagnosis, logs, and observability",
                        "scaling bottlenecks, capacity planning, and performance",
                        "security, data integrity, and recovery from failure",
                        "concurrency, consistency, and difficult edge cases",
                        "cost, maintainability, and comparison with simpler alternatives",
                    ]
                    previous_focus = st.session_state.get("last_challenge_focus")
                    available_focuses = [item for item in focus_angles if item != previous_focus]
                    selected_focus = available_focuses[uuid.uuid4().int % len(available_focuses)]
                    st.session_state["last_challenge_focus"] = selected_focus
                    dyn_q = generate_dynamic_ai_technical_question(
                        topic=custom_topic.strip(),
                        variation_hint=selected_focus,
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
                rubric_rows = [{"Criterion": rubric.display_name, "Score": rubric.score} for rubric in result.rubric_scores.values()]
                st.bar_chart(pd.DataFrame(rubric_rows).set_index("Criterion"), y="Score", use_container_width=True)
                for rubric in result.rubric_scores.values():
                    st.markdown(f"**{rubric.display_name}: {rubric.score:.1f}/5** — {rubric.feedback}")

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
if active_section == "spot_the_flaw":
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
if active_section == "star_builder":
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
        st.subheader("2. Story structure and delivery feedback")

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

        if st.button("Build structured story", type="primary", use_container_width=True):
            if not all(value.strip() for value in (story_title, b_sit, b_task, b_act, b_res)):
                st.warning("Complete the project name and all four STAR sections first.")
            else:
                assembled_md = f"""# {story_title.strip()}

## Situation
{b_sit.strip()}

## Task
{b_task.strip()}

## Action
{b_act.strip()}

## Result and learning
{b_res.strip()}

**Delivery guidance:** Keep the context concise, spend most of the answer explaining your own actions and decisions, and finish with the result and lesson learned.
"""
                st.markdown(assembled_md)
                st.download_button(
                    label="Download structured story (.md)",
                    data=assembled_md,
                    file_name=f"star_story_{story_title.lower().replace(' ', '_')}.md",
                    mime="text/markdown",
                )


# ==============================================================================
# TAB 5: COMPREHENSIVE QUESTION BANK
# ==============================================================================
if active_section == "question_bank":
    st.header("📚 Comprehensive Interview Question Bank")
    st.markdown("Explore curated behavioral, technical, and project architecture questions across key disciplines.")

    b_type = st.radio(
        "Question Category",
        ["Behavioral Competencies (STAR)", "Role-Specific Technical Quizzes", "Project Architecture & Deep-Dive"],
        horizontal=True,
    )

    category_track = {
        "Behavioral Competencies (STAR)": InterviewType.BEHAVIORAL.value,
        "Role-Specific Technical Quizzes": InterviewType.TECHNICAL.value,
        "Project Architecture & Deep-Dive": InterviewType.PROJECT_EXPLANATION.value,
    }
    default_track = category_track[b_type]
    track_options = (
        [InterviewType.TECHNICAL.value, InterviewType.COMPREHENSIVE.value]
        if b_type == "Role-Specific Technical Quizzes"
        else [default_track]
    )

    st.subheader("Generated 5–8 Question Practice Session")
    st.caption("All three question-bank categories now generate a complete practice set. Select the role, difficulty, and question count, then answer and submit for rubric feedback.")

    role_filter = st.selectbox("Target role / domain", [item.value for item in TargetRole], key="qb_role_filter")
    quiz_track = st.selectbox("Interview format", track_options, key="qb_interview_track")
    quiz_level = st.selectbox("Candidate level", [item.value for item in ExperienceLevel], key="qb_candidate_level")
    quiz_count = st.slider("Questions in this session", min_value=5, max_value=8, value=6, key="qb_question_count")
    quiz_config = (b_type, role_filter, quiz_track, quiz_level, quiz_count)

    def _create_question_bank_quiz():
        previous = st.session_state.get("question_bank_quiz", {})
        previous_ids = {item.id for item in previous.get("questions", [])}
        fresh_questions = []
        for _ in range(12):
            fresh_questions = build_interview_plan(
                target_role=role_filter,
                experience_level=quiz_level,
                interview_type=quiz_track,
                num_questions=quiz_count,
            )
            if {item.id for item in fresh_questions} != previous_ids:
                break
        st.session_state["question_bank_quiz"] = {
            "config": quiz_config, "questions": fresh_questions, "token": uuid.uuid4().hex[:10]
        }
        st.session_state.pop("question_bank_quiz_results", None)

    current_quiz = st.session_state.get("question_bank_quiz")
    if not current_quiz or current_quiz.get("config") != quiz_config:
        _create_question_bank_quiz()
    if st.button("🔄 Generate New Quiz", type="primary", use_container_width=True, key="generate_question_bank_quiz"):
        _create_question_bank_quiz()
        st.rerun()

    current_quiz = st.session_state["question_bank_quiz"]
    quiz_questions, quiz_token = current_quiz["questions"], current_quiz["token"]
    st.success(f"{len(quiz_questions)} questions generated · {b_type} · {role_filter}")
    with st.form(f"question_bank_quiz_form_{quiz_token}"):
        quiz_answers = {}
        for idx, question in enumerate(quiz_questions, 1):
            st.markdown(f"**Question {idx} · {question.competency_or_topic}**")
            st.write(question.question_text)
            quiz_answers[question.id] = st.text_area(
                f"Your answer to question {idx}", key=f"qb_answer_{quiz_token}_{idx}",
                height=110, placeholder="Explain the concept, reasoning, example, and trade-offs..."
            )
            if question.default_followup:
                st.caption(f"Possible follow-up: {question.default_followup}")
            st.divider()
        submitted_quiz = st.form_submit_button("Submit session and evaluate answers", type="primary", use_container_width=True)

    if submitted_quiz:
        quiz_results, active_quiz_settings = [], get_active_llm_settings()
        with st.spinner("Evaluating your answers..."):
            for question in quiz_questions:
                answer = (quiz_answers.get(question.id) or "").strip()
                if not answer:
                    quiz_results.append({"question": question, "answer": "", "evaluation": None, "error": "No answer submitted."})
                    continue
                try:
                    evaluation = evaluate_with_llm(
                        question, answer,
                        candidate_context=st.session_state.get("sb_candidate_context", "").strip(),
                        **active_quiz_settings,
                    )
                    quiz_results.append({"question": question, "answer": answer, "evaluation": evaluation, "error": None})
                except (ValueError, RuntimeError) as exc:
                    quiz_results.append({"question": question, "answer": answer, "evaluation": None, "error": str(exc)})
        st.session_state["question_bank_quiz_results"] = {"token": quiz_token, "results": quiz_results}

    saved_results = st.session_state.get("question_bank_quiz_results")
    if saved_results and saved_results.get("token") == quiz_token:
        scores = [row["evaluation"].overall_score for row in saved_results["results"] if row.get("evaluation")]
        if scores:
            st.metric("Overall practice score", f"{sum(scores) / len(scores):.1f} / 5.0")
            st.caption(f"{len(scores)} of {len(quiz_questions)} answers evaluated.")
        for idx, row in enumerate(saved_results["results"], 1):
            question, evaluation = row["question"], row.get("evaluation")
            with st.expander(f"Question {idx} feedback · {question.competency_or_topic}"):
                st.write(question.question_text)
                if not evaluation:
                    st.warning(row.get("error") or "Answer not evaluated.")
                else:
                    st.metric("Practice score", f"{evaluation.overall_score:.1f} / 5.0")
                    for criterion in evaluation.rubric_scores.values():
                        st.markdown(f"**{criterion.display_name}: {criterion.score:.1f}/5** — {criterion.feedback}")
                    st.markdown("**Strengths**")
                    for strength in evaluation.key_strengths:
                        st.markdown(f"- {strength}")
                    st.markdown("**Improvements**")
                    for improvement in evaluation.actionable_improvements:
                        st.markdown(f"- {improvement}")


# ==============================================================================
# TAB 6: SYSTEM DESIGN & ENGINEERING PLAYBOOKS
# ==============================================================================
if active_section == "system_design":
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
if active_section == "progress":
    st.header("Practice history & performance")
    st.caption("Charts use the sessions saved in this browser's local storage. No performance database is queried.")
    current_email = st.session_state.get("authenticated_candidate_id") or st.session_state.get("authenticated_email", "")
    history_rows = session_summaries(st.session_state.get("browser_data", {}), current_email)
    if not history_rows:
        st.info("Your history is empty. Complete a practice round to build your personal progress charts.")
    else:
        session_chart_rows = []
        rubric_chart_rows = []
        category_chart_rows = []
        for saved in history_rows:
            stamp = float(saved.get("completed_at") or saved.get("created_at") or time.time())
            scored = saved.get("overall_session_score")
            if scored is not None:
                session_chart_rows.append({
                    "Date": time.strftime("%Y-%m-%d", time.localtime(stamp)),
                    "Session": str(saved.get("session_id", ""))[:8],
                    "Score": float(scored),
                })
            for turn in saved.get("turns", []) or []:
                evaluation = turn.get("turn_evaluation") or turn.get("initial_evaluation") or {}
                rubric = evaluation.get("rubric_scores") or {}
                for key, value in rubric.items():
                    try:
                        rubric_chart_rows.append({"Criterion": key.title(), "Score": float(value.get("score", 0))})
                    except (TypeError, ValueError):
                        pass
                question = turn.get("question") or {}
                if evaluation.get("overall_score") is not None:
                    category_chart_rows.append({
                        "Category": str(question.get("category", "other")).title(),
                        "Score": float(evaluation["overall_score"]),
                    })
        if session_chart_rows:
            st.subheader("Score trend by practice session")
            trend = pd.DataFrame(session_chart_rows)
            trend["Session label"] = trend["Date"] + " · " + trend["Session"]
            st.line_chart(trend.set_index("Session label")[["Score"]], y="Score", use_container_width=True)
        if rubric_chart_rows:
            st.subheader("Rubric strengths and improvement areas")
            rubric_df = pd.DataFrame(rubric_chart_rows).groupby("Criterion", as_index=False)["Score"].mean().sort_values("Score")
            st.bar_chart(rubric_df.set_index("Criterion"), y="Score", use_container_width=True)
        if category_chart_rows:
            st.subheader("Performance by interview category")
            category_df = pd.DataFrame(category_chart_rows).groupby("Category", as_index=False)["Score"].mean().sort_values("Score")
            st.bar_chart(category_df.set_index("Category"), y="Score", use_container_width=True)
        st.subheader("Session history")
        for saved in reversed(history_rows):
            created = time.strftime("%d %b %Y, %H:%M", time.localtime(float(saved.get("created_at") or 0)))
            score = saved.get("overall_session_score")
            st.markdown(
                f"**{created} · {saved.get('target_role', 'Practice')}** — "
                f"{'%.1f / 5' % float(score) if score is not None else 'Not scored'} · "
                f"{'Completed' if saved.get('is_finished') else 'In progress'}"
            )
            st.caption(f"{saved.get('interview_type', '')} · {len(saved.get('turns', []) or [])} questions · Session {str(saved.get('session_id', ''))[:8]}")
    st.warning("Browser-only storage is not a cloud backup. Data stays in this browser profile, may not appear on another device, and can be deleted when browser data is cleared. Export reports regularly if you need a durable copy.")
# ==============================================================================
# TAB 8: EXPORT PRACTICE REPORT
# ==============================================================================
if active_section == "export_report":
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
if active_section == "rubric_guide":
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


# ==============================================================================
# TAB 10: RESUME + PUBLIC PROJECT REVIEW
# ==============================================================================
if active_section == "resume_review":
    st.header("Resume & Project Review")
    st.markdown("Upload a resume PDF, add a **public GitHub repository**, or use both. InterviewIQ reviews role alignment, project evidence, engineering practices, and likely interview follow-ups.")
    st.caption("Private repositories and access tokens are not supported. Repository files are read as text only; code is not executed.")

    review_resume = st.file_uploader(
        "Resume (PDF, optional)",
        type=["pdf"],
        help="Text-based PDF only; maximum 8 MB. The review extracts text from up to 8 pages.",
        key="career_review_resume_pdf",
    )
    review_repo_url = st.text_input(
        "Public GitHub repository URL (optional)",
        placeholder="https://github.com/owner/repository",
        help="Only public GitHub repositories are fetched. Up to 12 small text files are reviewed.",
        key="career_review_repo_url",
    )
    st.caption("Choose at least one input. If a hosted free-tier model is configured, extracted resume text and selected public repository snippets are sent to that provider for feedback. Remove sensitive personal details first.")
    review_role = st.selectbox(
        "Target role for this review",
        [r.value for r in TargetRole],
        index=[r.value for r in TargetRole].index(st.session_state.get("sb_target_role", TargetRole.SOFTWARE_ENGINEERING.value))
        if st.session_state.get("sb_target_role", TargetRole.SOFTWARE_ENGINEERING.value) in [r.value for r in TargetRole] else 0,
        key="career_review_role",
    )
    review_job_description = st.text_area(
        "Job description (optional, improves ATS keyword matching)",
        placeholder="Paste the job description here to compare relevant skills and keywords with your resume.",
        height=150,
        key="career_review_job_description",
    )

    if st.button("Review Resume & Project", type="primary", use_container_width=True, key="run_career_review"):
        if not review_resume and not review_repo_url.strip():
            st.warning("Upload a resume PDF, enter a public GitHub repository URL, or both.")
        else:
            try:
                with st.spinner("Reading your materials and preparing the review..."):
                    resume_text = extract_resume_pdf(review_resume) if review_resume else ""
                    repo_data = fetch_public_repository(review_repo_url.strip()) if review_repo_url.strip() else None
                    active = get_active_llm_settings()
                    review_config = {
                        "provider": active.get("provider", "heuristic"),
                        "model_name": None if active.get("provider") == "gemini" else active.get("model_name"),
                        "gemini_api_key": active.get("api_key") if active.get("provider") == "gemini" else None,
                        "groq_api_key": active.get("api_key") if active.get("provider") == "groq" else None,
                        "openai_api_key": active.get("api_key") if active.get("provider") == "openai" else None,
                    }
                    review_result = evaluate_candidate_materials(resume_text, repo_data, review_role, review_config)
                    ats_result = calculate_ats_score(resume_text, review_role, review_job_description) if resume_text else None
                    resume_questions = generate_resume_based_questions(resume_text, review_role, repo_data) if resume_text else []
                    st.session_state["career_review_result"] = review_result
                    st.session_state["career_review_ats_result"] = ats_result
                    st.session_state["career_review_resume_questions"] = resume_questions
                    st.session_state["career_review_repo_meta"] = (
                        {k: v for k, v in repo_data.items() if k != "files"} if repo_data else None
                    )
                st.success("Review ready.")
            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Could not complete the review: {exc}. Check the repository URL or try again later.")

    review_result = st.session_state.get("career_review_result")
    if review_result:
        st.markdown("---")
        st.subheader("Review summary")
        st.caption(f"Evaluation method: {review_result.get('provider', 'Unknown')}")
        st.write(review_result.get("summary", ""))
        st.info(review_result.get("role_fit", ""))

        ats_result = st.session_state.get("career_review_ats_result")
        if ats_result and ats_result.get("score") is not None:
            st.markdown("### ATS readiness score")
            ats_col1, ats_col2 = st.columns([1, 3])
            with ats_col1:
                st.metric("Checklist score", f"{ats_result['score']}/100")
                st.caption(ats_result.get("label", "Heuristic estimate"))
            with ats_col2:
                st.progress(min(100, max(0, int(ats_result["score"]))) / 100)
                st.caption(ats_result.get("method", "Heuristic checklist; not an employer ATS score"))
            st.markdown("**Score breakdown**")
            breakdown_df = pd.DataFrame([
                {"Category": item["category"], "Score": f"{item['score']}/{item['max_score']}", "What was checked": item["detail"]}
                for item in ats_result.get("breakdown", [])
            ])
            st.dataframe(breakdown_df, use_container_width=True, hide_index=True)
            with st.expander("ATS improvement checklist", expanded=True):
                for suggestion in ats_result.get("suggestions", []):
                    st.markdown(f"- {suggestion}")
            if ats_result.get("matched_keywords"):
                st.markdown("**Detected role keywords:** " + ", ".join(ats_result["matched_keywords"]))
            if ats_result.get("missing_keywords"):
                st.markdown("**Potentially relevant missing keywords:** " + ", ".join(ats_result["missing_keywords"]))
            st.caption("This is a transparent heuristic checklist, not a score from an employer's ATS. Match your resume to the actual job description and never add skills you do not have.")

        resume_questions = st.session_state.get("career_review_resume_questions", [])
        if resume_questions:
            st.markdown("### Resume-based interview questions")
            st.caption("Questions below are generated from extracted resume claims, project descriptions, metrics, and skills. Be ready to explain every claim.")
            for idx, question in enumerate(resume_questions, 1):
                st.markdown(f"**{idx}.** {question}")

        review_repo_meta = st.session_state.get("career_review_repo_meta")
        if review_repo_meta:
            st.markdown(f"**Repository:** [{review_repo_meta.get('name', 'GitHub repository')}]({review_repo_meta.get('url', '')})")
            st.caption(f"Primary language: {review_repo_meta.get('language', 'Not specified')} · Files reviewed: {review_repo_meta.get('file_count', 'up to 12')} · Stars: {review_repo_meta.get('stars', 0)}")

        review_sections = [
            ("Resume strengths", "resume_strengths"),
            ("Resume improvements", "resume_improvements"),
            ("Project review", "project_review"),
            ("Potential claims to verify", "potential_claims_to_verify"),
            ("Interview questions to prepare", "interview_questions"),
            ("Priority actions", "priority_actions"),
        ]
        for title, key in review_sections:
            items = review_result.get(key, [])
            if items:
                with st.expander(title, expanded=title in {"Resume improvements", "Project review", "Priority actions"}):
                    for item in items:
                        st.markdown(f"- {item}")
        st.caption(review_result.get("disclaimer", "Practice feedback only."))
        review_download_payload = dict(review_result)
        review_download_payload["ats_readiness"] = st.session_state.get("career_review_ats_result")
        review_download_payload["resume_based_questions"] = st.session_state.get("career_review_resume_questions", [])
        st.download_button(
            "Download review (.json)",
            data=json.dumps(review_download_payload, indent=2, ensure_ascii=False),
            file_name="interviewiq_resume_project_review.json",
            mime="application/json",
            key="download_career_review_json",
        )
