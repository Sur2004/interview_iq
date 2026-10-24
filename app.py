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
from backend.config import (
    get_setting,
    validate_secrets,
    get_llm_config,
)

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
    if words < 40:
        return '<span class="pacing-chip pacing-warn">⚠️ Too Brief (&lt;40 words)</span>'
    elif words <= 240:
        return '<span class="pacing-chip pacing-ok">✨ Sweet Spot (60–200 words)</span>'
    else:
        return '<span class="pacing-chip pacing-warn">⚠️ Verbose / Wordy (&gt;240 words)</span>'


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


# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
with st.sidebar:
    st.markdown('<span class="ai-online-badge">● AI ENGINE ONLINE</span>', unsafe_allow_html=True)
    st.title("InterviewIQ Studio")
    st.caption("AI-Powered Technical & Behavioral Interview Simulator")
    st.markdown("---")

    st.subheader("⚙️ Session Configuration")

    candidate_name = st.text_input(
        "Candidate Name",
        value="Student Candidate",
        help="Personalizes practice reports and rubric summaries",
    )

    target_role = st.selectbox(
        "Target Role",
        [r.value for r in TargetRole],
        index=0,
        help="Calibrates technical depth, systems questions, and rubric expectations",
    )

    experience_level = st.selectbox(
        "Experience Level",
        [e.value for e in ExperienceLevel],
        index=0,
        help="Tailors scoring criteria and question complexity",
    )

    interview_type = st.selectbox(
        "Interview Type",
        [t.value for t in InterviewType],
        index=0,
        help="Select between Comprehensive (Mixed), Technical Deep-Dive, Behavioral, or Architecture",
    )

    interviewer_persona = st.selectbox(
        "AI Interviewer Persona",
        [
            "Jordan (Principal Architect / Scale, Latency & Failure Modes)",
            "Alex (Staff Engineer / Algorithmic Trade-offs & Clean Code)",
            "Taylor (VP of Engineering / System Vision & Culture Fit)",
        ],
        index=0,
        help="Shapes the style, tone, and technical rigor of follow-up questions",
    )
    st.session_state.interviewer_persona = interviewer_persona

    num_questions = st.slider(
        "Questions in Round",
        min_value=5,
        max_value=8,
        value=6,
        help="5–8 questions simulate the stamina of an actual 45-minute technical loop",
    )

    candidate_context = st.text_area(
        "Your Real Projects / Coursework (Optional)",
        placeholder="e.g. Distributed Key-Value Store in Go; Virtual Memory Manager in C; React & PostgreSQL e-commerce capstone; PyTorch RAG pipeline...",
        help="Anchors AI outlines and follow-ups to your genuine technical background without fabricating experience.",
        height=90,
    )

    llm_conf = get_llm_config()
    secret_val = validate_secrets()

    with st.expander("🤖 AI Engine & Secret Settings", expanded=False):
        st.caption(f"Status: {secret_val['message']}")

        provider_opts = [
            "Auto (Configured via .env / Secrets)",
            "Groq Cloud (Llama 3.3 70B)",
            "Google Gemini (1.5 Flash)",
            "OpenAI (GPT-4o Mini)",
            "Built-In Offline Engine (No Key Required)",
        ]
        chosen_provider = st.selectbox(
            "Active LLM Provider",
            provider_opts,
            index=0,
            help="Select provider. Keys can be set in .env (local) or Streamlit Secrets (cloud).",
        )

        manual_key = st.text_input(
            "API Key Override (Optional)",
            value="",
            type="password",
            placeholder="Paste key to override .env / secrets...",
            help="Never committed or logged. Overrides active session only.",
        )
        if manual_key:
            st.session_state.api_key = manual_key

    st.markdown("---")
    if st.button("🚀 Initialize AI Interview Round", type="primary", use_container_width=True):
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
        st.success(f"AI Round Initialized with {len(questions)} balanced questions!")
        st.rerun()

    if st.session_state.session and not st.session_state.session.is_finished:
        if st.button("⏹️ Conclude Session Early", use_container_width=True):
            st.session_state.session.is_finished = True
            st.session_state.session.completed_at = time.time()
            save_session(st.session_state.session)
            st.rerun()


# ==============================================================================
# HERO HEADER BANNER (SKY BLUE, WHITE, BLACK)
# ==============================================================================
st.markdown("""
<div class="hero-banner-sky">
    <div style="display: flex; justify-content: space-between; align-items: flex-start;">
        <div>
            <div class="hero-title">⚡ InterviewIQ: AI Technical Studio</div>
            <div class="hero-subtitle">
                High-fidelity, repeatable technical interview practice with automated Big-O complexity analysis,
                live follow-up probing, and transparent rubric diagnostics. Built for ambitious students & engineers.
            </div>
        </div>
        <span class="ai-online-badge">⚡ NEURAL ENGINE ACTIVE</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Transparent Notices
st.markdown(
    f'<div class="notice-card-sky"><strong>ℹ️ Transparent Rubric Notice:</strong> {RUBRIC_DISCLAIMER}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="ethics-card-sky"><strong>🛡️ Anti-Fabrication Guarantee:</strong> {ETHICAL_OUTLINE_GUIDELINE}</div>',
    unsafe_allow_html=True,
)


# ==============================================================================
# MAIN NAVIGATION TABS
# ==============================================================================
tab_studio, tab_dynamic_ai, tab_flaw_game, tab_star_builder, tab_bank, tab_playbook, tab_analytics, tab_report, tab_rubric = st.tabs([
    "🎯 Mock Interview Studio",
    "⚡ AI Technical Generator",
    "🎮 Spot the Flaw Game",
    "🛠️ STAR Story Builder",
    "📚 Question Bank",
    "📖 System Design Playbooks",
    "📊 Practice Analytics",
    "📑 Export Practice Report",
    "⚖️ Transparent Rubric",
])


# ==============================================================================
# TAB 1: MOCK INTERVIEW STUDIO
# ==============================================================================
with tab_studio:
    session: InterviewSession = st.session_state.session

    if session is None:
        st.markdown("### 👋 Welcome to the Technical Interview Simulator")
        st.write("Configure your profile in the left sidebar and click **'Initialize AI Interview Round'** to begin.")

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
        st.markdown("#### ⚡ Architecture Visualizer Preview")
        st.caption("When you describe your system, InterviewIQ automatically maps your components into a live Mermaid graph:")
        sample_mermaid = """graph TD
    Client ["Client (Browser / Mobile)"] --> Gateway ["API Gateway / Reverse Proxy"]
    Gateway --> Service ["Backend Application Service (FastAPI)"]
    Service -.->|Cache-Aside Check| Cache [("In-Memory Cache (Redis)")]
    Service -->|Persistent Queries| DB [("Primary Database (PostgreSQL)")]"""
        render_mermaid(sample_mermaid, height=240)

    elif session.is_finished:
        st.success("🎉 **Interview Round Completed!** Full diagnostic transcript compiled below.")

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

            st.markdown("### 📝 Turn-by-Turn Diagnostic Review")
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
                        # Technical Telemetry
                        if t_eval.technical_breakdown:
                            tb = t_eval.technical_breakdown
                            st.markdown("#### 🔬 Technical Depth Telemetry")
                            col_t1, col_t2, col_t3 = st.columns(3)
                            with col_t1:
                                st.write("**Time Complexity:**", ", ".join(tb.get("time_complexity", [])) or "None explicit")
                            with col_t2:
                                st.write("**Concurrency:**", ", ".join(tb.get("concurrency_primitives", [])) or "None explicit")
                            with col_t3:
                                st.write("**Patterns:**", ", ".join(tb.get("architectural_patterns", [])) or "None explicit")

                        if t_eval.architecture_diagram_mermaid:
                            st.markdown("#### 🗺️ Architecture Diagram (Derived from Answer)")
                            render_mermaid(t_eval.architecture_diagram_mermaid, height=240)

                        st.markdown("#### ⚖️ Rubric Breakdown")
                        cols_r = st.columns(4)
                        for idx, (k, r_crit) in enumerate(t_eval.rubric_scores.items()):
                            with cols_r[idx]:
                                st.metric(r_crit.display_name, f"{r_crit.score} / 5.0")
                                st.caption(r_crit.feedback)

                        st.markdown(t_eval.stronger_answer_outline)
        else:
            st.warning("Session completed without submitted responses.")

        if st.button("🔄 Start Fresh Practice Round"):
            st.session_state.session = None
            st.rerun()

    else:
        # ACTIVE INTERVIEW ROUND IN PROGRESS
        curr_idx = session.current_turn_index
        turn = session.turns[curr_idx]
        q_item = turn.question

        # Animated progress bar
        progress_val = (curr_idx) / session.total_questions
        st.progress(progress_val)
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            st.caption(f"Question {curr_idx + 1} of {session.total_questions} | {session.target_role} • {session.experience_level}")
        with col_p2:
            st.markdown(f"<span class='tech-tag'>{q_item.category.value.upper()}</span>", unsafe_allow_html=True)

        # Dynamic Animated Question Card (White with Sky-Blue Glow)
        st.markdown(f"""
        <div class="animated-question-card">
            <span style="font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#0284c7; letter-spacing:0.05em;">
                ⚡ Question {curr_idx + 1} • Focus: {q_item.competency_or_topic}
            </span>
            <p style="font-size:1.26rem; font-weight:700; color:#000000; margin-top:8px; line-height:1.5;">
                {q_item.question_text}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Scaffolding Guidance Expander
        with st.expander("💡 Technical Expectations & Evaluation Hints", expanded=False):
            st.markdown("**What Interviewers Look For:**")
            for h in q_item.rubric_hints:
                st.markdown(f"- {h}")

            if q_item.category == QuestionCategory.BEHAVIORAL:
                st.info("**STAR Framework:**\n- **S (Situation):** Context, timeline & constraints (15%)\n- **T (Task):** Your specific mandate (10%)\n- **A (Action):** What YOU decided, coded, and did (60%)\n- **R (Result):** Observable outcome, metrics, and retrospective (15%)")
            elif q_item.category == QuestionCategory.TECHNICAL:
                st.info("**Technical Architecture Flow:**\n1. Core definition\n2. Internal mechanics & complexity (O-notation)\n3. Real-world trade-offs (space vs time, write vs read)\n4. Concrete example from your own codebase")
            else:
                st.info("**Project Architecture Flow:**\n1. Problem & topology\n2. Stack choices vs alternatives\n3. Hardest technical bug or bottleneck YOU solved\n4. Hindsight redesign")

        # STAGE A: PRIMARY ANSWER SUBMISSION
        if not session.in_followup and not turn.completed:
            st.markdown("#### ✍️ Type Your Response")

            user_input = st.text_area(
                "Your Answer:",
                value=turn.initial_answer,
                height=180,
                placeholder="State your answer clearly. Explain your technical choices, complexity trade-offs, and use 'I' to highlight your individual agency...",
                key=f"ans_input_{curr_idx}",
            )

            word_count = len(user_input.strip().split()) if user_input.strip() else 0
            pacing_chip = get_word_pacing_chip(word_count)
            st.markdown(f"**Word Count:** `{word_count} words` {pacing_chip}", unsafe_allow_html=True)

            # Optional Code Snippet input for technical depth
            with st.expander("💻 Include Code Snippet / Pseudocode (Optional)"):
                code_input = st.text_area(
                    "Code / Implementation Snippet:",
                    height=110,
                    placeholder="def solve(stream):\n    cache = {}\n    # Mutex lock / atomic CAS...",
                    key=f"code_snippet_{curr_idx}",
                )

            col_sub1, col_sub2 = st.columns([1, 4])
            with col_sub1:
                if st.button("Submit Answer 💬", type="primary", use_container_width=True):
                    if not user_input.strip():
                        st.warning("Please type your response before submitting.")
                    else:
                        full_content = user_input.strip()
                        if code_input.strip():
                            full_content += f"\n\n[Candidate Code Implementation]:\n```\n{code_input.strip()}\n```"
                        turn.initial_answer = full_content

                        with st.spinner(f"{st.session_state.interviewer_persona.split('(')[0]} is analyzing your architecture and formulating a follow-up..."):
                            init_eval = evaluate_with_llm(
                                q_item,
                                turn.initial_answer,
                                candidate_context=session.candidate_context,
                                api_key=st.session_state.api_key or None,
                            )

                            turn.initial_evaluation = init_eval
                            if init_eval.suggested_followup_question:
                                turn.followup_question = init_eval.suggested_followup_question

                            session.in_followup = True
                            save_session(session)
                            st.rerun()

        # STAGE B: FOLLOW-UP QUESTION & TURN COMPLETION
        elif session.in_followup and not turn.completed:
            with st.expander("📄 Review Your Initial Response", expanded=False):
                st.markdown(turn.initial_answer)

            persona_name = st.session_state.interviewer_persona.split("(")[0].strip()
            # High-tech Black & Sky Blue Follow-up Card
            st.markdown(f"""
            <div class="animated-followup-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:0.8rem; font-weight:700; color:#38bdf8; text-transform:uppercase; letter-spacing:0.06em;">
                        ⚡ {persona_name}'s Follow-Up Challenge
                    </span>
                    <span class="ai-online-badge">PROBING TRADE-OFFS</span>
                </div>
                <p style="font-size:1.22rem; font-weight:700; color:#ffffff; margin-top:8px; margin-bottom:0; line-height:1.5;">
                    "{turn.followup_question or q_item.default_followup}"
                </p>
            </div>
            """, unsafe_allow_html=True)

            followup_input = st.text_area(
                "Your Follow-Up Response:",
                value=turn.followup_answer,
                height=140,
                placeholder="Elaborate on the specific failure modes, concurrency race conditions, or edge case trade-offs...",
                key=f"followup_input_{curr_idx}",
            )
            f_word_count = len(followup_input.strip().split()) if followup_input.strip() else 0
            st.caption(f"Follow-up length: {f_word_count} words")

            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                if st.button("Submit Follow-Up & Score Turn 🎯", type="primary", use_container_width=True):
                    turn.followup_answer = followup_input.strip()
                    with st.spinner("Executing full 4-part rubric and complexity telemetry..."):
                        full_eval = evaluate_with_llm(
                            q_item,
                            turn.initial_answer,
                            followup_answer=turn.followup_answer,
                            candidate_context=session.candidate_context,
                            api_key=st.session_state.api_key or None,
                        )
                        turn.turn_evaluation = full_eval
                        turn.completed = True
                        session.in_followup = False
                        save_session(session)
                        st.rerun()

            with col_f2:
                if st.button("Skip Follow-Up", use_container_width=True):
                    turn.followup_answer = "[Candidate skipped follow-up]"
                    turn.turn_evaluation = turn.initial_evaluation
                    turn.completed = True
                    session.in_followup = False
                    save_session(session)
                    st.rerun()

        # STAGE C: DIAGNOSTIC RUBRIC FEEDBACK & TELEMETRY
        elif turn.completed and turn.turn_evaluation:
            t_eval = turn.turn_evaluation

            st.markdown("### 📊 Turn Diagnostic Results")
            col_sc, col_badge = st.columns([1, 2])
            with col_sc:
                st.metric("Turn Practice Score", f"{t_eval.overall_score} / 5.0")
            with col_badge:
                st.markdown("**Mastery Level:**")
                st.markdown(get_performance_badge(t_eval.overall_score), unsafe_allow_html=True)

            # Dynamic Technical Telemetry Dashboard
            if t_eval.technical_breakdown:
                tb = t_eval.technical_breakdown
                st.markdown("#### 🔬 Dynamic Technical Telemetry")
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    time_comp = ", ".join(tb.get("time_complexity", [])) or "None explicitly detected"
                    st.markdown(f"""
                    <div class="telemetry-card">
                        <span style="color:#38bdf8; font-size:0.8rem; font-weight:700;">ALGORITHMIC COMPLEXITY</span>
                        <div style="font-size:1.1rem; font-weight:700; color:#ffffff; margin:4px 0;">{time_comp}</div>
                        <span style="font-size:0.75rem; color:#94a3b8;">Space analysis: {'✅ Detected' if tb.get('space_complexity_detected') else '⚪ Omitted'}</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col_m2:
                    concurrency = ", ".join(tb.get("concurrency_primitives", [])) or "No concurrency terms"
                    st.markdown(f"""
                    <div class="telemetry-card">
                        <span style="color:#38bdf8; font-size:0.8rem; font-weight:700;">CONCURRENCY PRIMITIVES</span>
                        <div style="font-size:1.05rem; font-weight:700; color:#ffffff; margin:4px 0;">{concurrency}</div>
                        <span style="font-size:0.75rem; color:#94a3b8;">Race condition safety analysis</span>
                    </div>
                    """, unsafe_allow_html=True)

                with col_m3:
                    arch_pats = ", ".join(tb.get("architectural_patterns", [])) or "No patterns detected"
                    st.markdown(f"""
                    <div class="telemetry-card">
                        <span style="color:#38bdf8; font-size:0.8rem; font-weight:700;">SYSTEM PATTERNS</span>
                        <div style="font-size:1.05rem; font-weight:700; color:#ffffff; margin:4px 0;">{arch_pats}</div>
                        <span style="font-size:0.75rem; color:#94a3b8;">Depth Rating: {tb.get('depth_score', 3.0)}/5.0</span>
                    </div>
                    """, unsafe_allow_html=True)

            # Dynamic Mermaid Architecture Diagram
            if t_eval.architecture_diagram_mermaid:
                st.markdown("#### 🗺️ AI-Derived Architecture Diagram")
                render_mermaid(t_eval.architecture_diagram_mermaid, height=240)

            # Rubric Breakdown Grid
            st.markdown("#### 4-Part Visible Rubric Breakdown")
            c_r1, c_r2, c_r3, c_r4 = st.columns(4)
            r_keys = ["relevance", "structure", "evidence", "clarity"]
            cols_list = [c_r1, c_r2, c_r3, c_r4]
            for idx, k in enumerate(r_keys):
                if k in t_eval.rubric_scores:
                    crit = t_eval.rubric_scores[k]
                    with cols_list[idx]:
                        st.metric(crit.display_name, f"{crit.score} / 5.0")
                        st.caption(crit.feedback)

            # Strengths & Actionable Growth
            col_str, col_imp = st.columns(2)
            with col_str:
                st.markdown("#### 🌟 Key Strengths")
                for s in t_eval.key_strengths:
                    st.markdown(f"- {s}")
            with col_imp:
                st.markdown("#### 🚀 Actionable Growth Advice")
                for imp in t_eval.actionable_improvements:
                    st.markdown(f"- {imp}")

            # Stronger Answer Structural Blueprint
            with st.expander("🧭 View Stronger Answer Structural Blueprint (Authentic Scaffolding)", expanded=True):
                st.markdown(t_eval.stronger_answer_outline)

            st.markdown("---")
            is_last = (curr_idx + 1) >= session.total_questions
            btn_label = "Conclude Round & Export Report 🎉" if is_last else "Proceed to Next Question ➡️"
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


# ==============================================================================
# TAB 2: AI TECHNICAL GENERATOR & DEEP-DIVE STUDIO (NEW & TECHNICAL)
# ==============================================================================
with tab_dynamic_ai:
    st.header("⚡ Dynamic AI Technical Problem Generator")
    st.markdown("""
    Want to test yourself on an ultra-niche technical topic? Enter any engineering subject below
    and the AI will dynamically synthesize a FAANG/Principal-level interview question with rubric constraints.
    """)

    col_g1, col_g2 = st.columns([2, 1])
    with col_g1:
        custom_topic = st.text_input(
            "Target Engineering Topic / System Subsystem:",
            value="Kafka Partition Rebalancing & Consumer Lag",
            placeholder="e.g. Postgres MVCC Vacuuming, Redis Cluster Sentinel, RAG Vector Search with HNSW, Raft Consensus...",
        )
    with col_g2:
        custom_difficulty = st.selectbox(
            "Target Seniority Level:",
            ["Internship / Entry-Level", "Mid-Level Engineer", "Staff / Principal Architect"],
            index=0,
        )

    if st.button("⚡ Generate AI Technical Challenge", type="primary"):
        with st.spinner("Synthesizing technical question, edge-case rubric, and follow-up challenge..."):
            dyn_q = generate_dynamic_ai_technical_question(
                topic=custom_topic,
                role=target_role,
                experience_level=custom_difficulty,
                api_key=st.session_state.api_key,
            )
            st.session_state.current_dyn_q = dyn_q

    if "current_dyn_q" in st.session_state:
        dq: QuestionItem = st.session_state.current_dyn_q
        st.markdown(f"""
        <div class="animated-question-card">
            <span style="font-size:0.8rem; font-weight:700; color:#0284c7; text-transform:uppercase;">
                ⚡ AI-Generated Technical Challenge • {dq.competency_or_topic}
            </span>
            <p style="font-size:1.25rem; font-weight:700; color:#000000; margin-top:8px;">
                {dq.question_text}
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="animated-followup-card">
            <span style="font-size:0.8rem; font-weight:700; color:#38bdf8; text-transform:uppercase;">
                ⚡ Probing Follow-Up Challenge
            </span>
            <p style="font-size:1.15rem; font-weight:700; color:#ffffff; margin-top:6px;">
                "{dq.default_followup}"
            </p>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("##### 💡 Technical Rubric Constraints:")
        for h in dq.rubric_hints:
            st.markdown(f"- `{h}`")

        st.markdown("---")
        st.subheader("🧪 Test Your Response Against the AI Evaluator")
        test_ans = st.text_area("Draft your technical answer:", height=150, placeholder="Explain data structures, complexity, trade-offs...")
        if st.button("Evaluate Against Technical Rubric"):
            if not test_ans.strip():
                st.warning("Type a response to evaluate.")
            else:
                with st.spinner("Analyzing technical complexity and generating architecture..."):
                    res = evaluate_heuristically(dq, test_ans)
                    st.metric("Rubric Score", f"{res.overall_score} / 5.0")
                    st.markdown(get_performance_badge(res.overall_score), unsafe_allow_html=True)

                    if res.technical_breakdown:
                        tb = res.technical_breakdown
                        st.write("**Detected Complexities:**", ", ".join(tb.get("time_complexity", [])) or "None")
                        st.write("**Architectural Concepts:**", ", ".join(tb.get("architectural_patterns", [])) or "None")

                    if res.architecture_diagram_mermaid:
                        st.markdown("#### 🗺️ Architecture Derived:")
                        render_mermaid(res.architecture_diagram_mermaid, height=240)


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

    if analytics["total_sessions"] > 0:
        st.subheader("📈 Rubric Dimension Breakdown")
        rubric_df = pd.DataFrame({
            "Rubric Dimension": ["Relevance", "Structure", "Evidence", "Clarity"],
            "Average Score (1.0 to 5.0)": [
                analytics["avg_relevance"],
                analytics["avg_structure"],
                analytics["avg_evidence"],
                analytics["avg_clarity"],
            ]
        })
        st.bar_chart(rubric_df.set_index("Rubric Dimension"))

    st.subheader("📜 Recorded Practice Sessions")
    past_sessions = list_sessions(limit=30)
    if not past_sessions:
        st.info("No recorded sessions found yet. Start a session to build your history!")
    else:
        table_data = []
        for s_row in past_sessions:
            table_data.append({
                "Session ID": s_row["session_id"],
                "Candidate": s_row["candidate_name"],
                "Target Role": s_row["target_role"].split("(")[0],
                "Interview Type": s_row["interview_type"].split("(")[0],
                "Score": f"{s_row['overall_score'] or 'N/A'}",
                "Status": "Completed" if s_row["is_finished"] else "In Progress",
            })
        st.dataframe(pd.DataFrame(table_data), use_container_width=True)

        st.markdown("#### 🔍 Load & Inspect Past Transcript")
        select_sess_id = st.selectbox("Select Session ID:", [s["session_id"] for s in past_sessions])
        if st.button("Load Full Session Transcript"):
            sess_data = get_session(select_sess_id)
            if sess_data:
                st.json(sess_data)


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
        st.subheader("Live Report Preview")
        st.markdown(md_report)


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
    st.subheader("2. Formative Practice vs Predictive Hiring Notice")
    st.warning(f"**Official Disclaimer:**\n\n{RUBRIC_DISCLAIMER}")
    st.write("""
    **Why this distinction matters:** Real hiring decisions depend on team culture, specific tech stack nuances,
    unconscious biases, and hiring manager preferences that no AI can or should attempt to predict. InterviewIQ
    functions strictly as a **skill-building gym**, helping you communicate clearly and organize your authentic experiences.
    """)

    st.markdown("---")
    st.subheader("3. Ethical Anti-Fabrication Commitment")
    st.success(f"**Our Pledge:**\n\n{ETHICAL_OUTLINE_GUIDELINE}")
    st.write("""
    - **No Fake Employers:** We never invent fictional companies or unearned internships in our answer outlines.
    - **No Inflated Metrics:** We never advise inventing false metrics (e.g., claiming you improved enterprise revenue by $5M).
    - **Scaffolding Real Work:** Outlines guide you on how to slot in your **actual course projects, open-source work, and hackathons**, teaching you how to communicate genuine technical trade-offs.
    """)
