"""
InterviewIQ - AI Mock Interview & Diagnostic Rubric Studio
Interactive, student-centric interview practice platform for internship and graduate-job applicants.
"""

import streamlit as st
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

# Page configuration
st.set_page_config(
    page_title="InterviewIQ - Mock Interview & Practice Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
init_db()

# Custom CSS for vibrant, student-friendly UI
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    .hero-container {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 50%, #6366f1 100%);
        border-radius: 16px;
        padding: 30px 36px;
        color: white;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(59, 130, 246, 0.25);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        margin-bottom: 6px;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        opacity: 0.92;
        max-width: 850px;
        line-height: 1.5;
    }
    
    .notice-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-left: 5px solid #3b82f6;
        padding: 14px 18px;
        border-radius: 10px;
        font-size: 0.88rem;
        color: #334155;
        margin-bottom: 16px;
    }
    .ethics-card {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 5px solid #10b981;
        padding: 12px 18px;
        border-radius: 10px;
        font-size: 0.86rem;
        color: #14532d;
        margin-bottom: 22px;
    }
    
    .question-box {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 26px 30px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.04);
        margin-bottom: 20px;
    }
    .followup-box {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-left: 6px solid #f59e0b;
        padding: 22px 26px;
        border-radius: 12px;
        margin: 20px 0;
        box-shadow: 0 4px 12px rgba(245, 158, 11, 0.06);
    }
    
    .score-badge {
        font-size: 0.95rem;
        font-weight: 700;
        padding: 5px 14px;
        border-radius: 9999px;
        display: inline-block;
    }
    .badge-advanced { background: #dcfce7; color: #15803d; border: 1px solid #86efac; }
    .badge-proficient { background: #dbeafe; color: #1d4ed8; border: 1px solid #93c5fd; }
    .badge-developing { background: #fef3c7; color: #b45309; border: 1px solid #fcd34d; }
    
    .pacing-pill {
        display: inline-block;
        font-size: 0.82rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 6px;
        margin-left: 8px;
    }
    .pill-short { background: #fee2e2; color: #b91c1c; }
    .pill-sweet { background: #dcfce7; color: #15803d; }
    .pill-long { background: #fef3c7; color: #b45309; }
    
    .feature-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.02);
        transition: transform 0.15s ease, box-shadow 0.15s ease;
    }
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 18px rgba(0,0,0,0.06);
    }
</style>
""", unsafe_allow_html=True)


# Session state initialization
if "session" not in st.session_state:
    st.session_state.session = None
if "api_key" not in st.session_state:
    st.session_state.api_key = os.environ.get("GEMINI_API_KEY", "") or os.environ.get("OPENAI_API_KEY", "")
if "eval_mode" not in st.session_state:
    st.session_state.eval_mode = "Intelligent Offline Diagnostic"
if "interviewer_persona" not in st.session_state:
    st.session_state.interviewer_persona = "Jordan (Principal Engineer / Rigorous)"
if "star_builder_step" not in st.session_state:
    st.session_state.star_builder_step = 1


def get_performance_badge(score: float) -> str:
    if score >= 4.2:
        return '<span class="score-badge badge-advanced">🌟 Advanced Mastery (4.2 – 5.0)</span>'
    elif score >= 3.2:
        return '<span class="score-badge badge-proficient">📈 Proficient Communicator (3.2 – 4.1)</span>'
    else:
        return '<span class="score-badge badge-developing">🌱 Developing Skills (1.0 – 3.1)</span>'


def get_word_pacing_pill(words: int) -> str:
    if words < 40:
        return '<span class="pacing-pill pill-short">⚠️ Too Brief (&lt;40 words)</span>'
    elif words <= 220:
        return '<span class="pacing-pill pill-sweet">✨ Sweet Spot (60–200 words)</span>'
    else:
        return '<span class="pacing-pill pill-long">⚠️ Slightly Wordy (&gt;220 words)</span>'


# ==============================================================================
# SIDEBAR CONTROLS
# ==============================================================================
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/interview.png", width=60)
    st.markdown("### **InterviewIQ Studio**")
    st.caption("AI Practice & Diagnostic Rubrics for Students")
    st.markdown("---")

    st.subheader("🎯 Setup Your Mock Interview")

    candidate_name = st.text_input(
        "Your Name",
        value="Student Candidate",
        help="Used to personalize practice reports and feedback summaries",
    )

    target_role = st.selectbox(
        "Target Role",
        [r.value for r in TargetRole],
        index=0,
        help="Customizes role-specific technical questions and evaluation anchors",
    )

    experience_level = st.selectbox(
        "Experience Level",
        [e.value for e in ExperienceLevel],
        index=0,
        help="Calibrates the expected depth and technical ownership",
    )

    interview_type = st.selectbox(
        "Interview Type",
        [t.value for t in InterviewType],
        index=0,
        help="Select between balanced mixed, pure behavioral (STAR), or technical deep-dives",
    )

    interviewer_persona = st.selectbox(
        "Interviewer Persona",
        [
            "Jordan (Principal Engineer / Rigorous on scale & trade-offs)",
            "Alex (Friendly Mentor / Encouraging & coaching)",
            "Taylor (Bar Raiser / Culture, ownership & ambiguity)",
        ],
        index=0,
        help="Shapes the style of follow-up questions",
    )
    st.session_state.interviewer_persona = interviewer_persona

    num_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=8,
        value=6,
        help="5–8 questions simulate the stamina and pacing of an actual 45-minute round",
    )

    candidate_context = st.text_area(
        "Your Real Projects / Coursework (Optional)",
        placeholder="e.g. Distributed Key-Value Store in Go; OS memory manager in C; React & PostgreSQL full-stack capstone; Hackathon NLP project...",
        help="Allows the AI to tailor outlines to your ACTUAL projects so you never fabricate experience.",
        height=90,
    )

    with st.expander("🤖 Evaluation Engine Settings"):
        eval_engine = st.radio(
            "Engine Mode",
            ["Intelligent Offline Diagnostic (Zero Setup)", "Live LLM (Gemini / OpenAI)"],
            index=0 if not st.session_state.api_key else 1,
        )
        api_key_input = st.text_input(
            "API Key (Optional)",
            value=st.session_state.api_key,
            type="password",
            help="Optional. The app operates 100% offline with full rubric diagnostics if blank.",
        )
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input

    st.markdown("---")
    if st.button("🚀 Start Mock Interview Session", type="primary", use_container_width=True):
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
        st.success(f"Session ready! {len(questions)} balanced questions loaded.")
        st.rerun()

    if st.session_state.session and not st.session_state.session.is_finished:
        if st.button("⏹️ Conclude Session Early", use_container_width=True):
            st.session_state.session.is_finished = True
            st.session_state.session.completed_at = time.time()
            save_session(st.session_state.session)
            st.rerun()


# ==============================================================================
# HERO HEADER BANNER
# ==============================================================================
st.markdown("""
<div class="hero-container">
    <div class="hero-title">🎯 InterviewIQ Practice Studio</div>
    <div class="hero-subtitle">
        Master internship and graduate-level interviews through repeatable practice, probing follow-up questions,
        and visible diagnostic rubrics. Build genuine confidence without memorizing scripts.
    </div>
</div>
""", unsafe_allow_html=True)

# Transparent Rubric & Anti-Fabrication Notice Banners
st.markdown(
    f'<div class="notice-card"><strong>ℹ️ Transparent Rubric Notice:</strong> {RUBRIC_DISCLAIMER}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="ethics-card"><strong>🛡️ Anti-Fabrication Commitment:</strong> {ETHICAL_OUTLINE_GUIDELINE}</div>',
    unsafe_allow_html=True,
)


# ==============================================================================
# MAIN NAVIGATION TABS
# ==============================================================================
tab_studio, tab_flaw_game, tab_star_builder, tab_bank, tab_playbook, tab_analytics, tab_report, tab_rubric = st.tabs([
    "🎯 Mock Interview Studio",
    "🎮 Spot the Flaw Game",
    "🛠️ STAR Story Builder",
    "📚 Question Bank",
    "📖 Interview Playbooks",
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
        st.markdown("### 👋 Ready to Practice? Let's Get Started!")
        st.write("Configure your target role in the left sidebar and click **'Start Mock Interview Session'**.")

        # Interactive Feature Preview Cards
        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            st.markdown("""
            <div class="feature-card">
                <h4 style="color:#1e3a8a; margin-top:0;">💻 Role-Specific Depth</h4>
                <p style="font-size:0.92rem; color:#475569;">
                    Deep technical questions for Software Engineering, Frontend, Data Science/ML, AI/LLMs, Cybersecurity, and Product.
                </p>
                <span style="font-size:0.8rem; font-weight:700; color:#2563eb;">Explores Trade-offs & Scale →</span>
            </div>
            """, unsafe_allow_html=True)

        with col_f2:
            st.markdown("""
            <div class="feature-card">
                <h4 style="color:#1e3a8a; margin-top:0;">🧭 Real Follow-Up Probes</h4>
                <p style="font-size:0.92rem; color:#475569;">
                    Just like a real interviewer, InterviewIQ asks a tailored follow-up question to test edge cases, trade-offs, and metrics.
                </p>
                <span style="font-size:0.8rem; font-weight:700; color:#2563eb;">No Script Memorization →</span>
            </div>
            """, unsafe_allow_html=True)

        with col_f3:
            st.markdown("""
            <div class="feature-card">
                <h4 style="color:#1e3a8a; margin-top:0;">⚖️ 4-Part Visible Rubric</h4>
                <p style="font-size:0.92rem; color:#475569;">
                    Every answer is scored on Relevance, Structure, Evidence, and Clarity. See exactly where you excel and where to tighten up.
                </p>
                <span style="font-size:0.8rem; font-weight:700; color:#2563eb;">Formative Practice Feedback →</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 💡 Quick Pro-Tips for High-Scoring Answers:")
        st.markdown("""
        1. **Use "I" instead of "We":** Interviewers hire you, not your university group. State what YOU decided, coded, and tested.
        2. **Quantify Results Honestly:** Mention approximate time saved, test coverage added, or latency improved without making up ridiculous numbers.
        3. **Admit What You Learned:** Acknowledge what went wrong or what you'd do differently today. In interviews, technical self-awareness is gold.
        """)

    elif session.is_finished:
        st.success("🎉 **Interview Session Completed!** Outstanding work investing in your preparation.")

        valid_turns = [t for t in session.turns if t.turn_evaluation]
        if valid_turns:
            avg_score = round(sum(t.turn_evaluation.overall_score for t in valid_turns) / len(valid_turns), 1)
            session.overall_session_score = avg_score
            save_session(session)

            col_sc1, col_sc2, col_sc3 = st.columns([1, 1, 2])
            with col_sc1:
                st.metric("Overall Practice Score", f"{avg_score} / 5.0")
            with col_sc2:
                st.markdown("**Proficiency Level:**")
                st.markdown(get_performance_badge(avg_score), unsafe_allow_html=True)
            with col_sc3:
                st.markdown(f"**Session Summary:** Completed {len(valid_turns)} of {session.total_questions} questions with follow-ups for **{session.target_role}**.")

            st.markdown("### 📝 Turn-by-Turn Diagnostic Review")
            for i, turn in enumerate(session.turns):
                t_eval = turn.turn_evaluation or turn.initial_evaluation
                score_str = f"{t_eval.overall_score}/5.0" if t_eval else "N/A"
                with st.expander(f"Question {i+1}: {turn.question.question_text[:75]}... (Score: {score_str})"):
                    st.markdown(f"**Question:** {turn.question.question_text}")
                    st.markdown(f"**Your Initial Answer:**\n> {turn.initial_answer}")
                    if turn.followup_question:
                        st.markdown(f"**Follow-Up Question:**\n> *\"{turn.followup_question}\"*")
                        st.markdown(f"**Your Follow-Up Answer:**\n> {turn.followup_answer or 'N/A'}")

                    if t_eval:
                        st.markdown("#### Rubric Breakdown")
                        cols_r = st.columns(4)
                        for idx, (k, r_crit) in enumerate(t_eval.rubric_scores.items()):
                            with cols_r[idx]:
                                st.metric(r_crit.display_name, f"{r_crit.score} / 5.0")
                                st.caption(r_crit.feedback)

                        st.markdown("#### 🌟 Key Strengths")
                        for s in t_eval.key_strengths:
                            st.write(f"- {s}")

                        st.markdown("#### 🚀 Priority Improvements")
                        for imp in t_eval.actionable_improvements:
                            st.write(f"- {imp}")

                        st.markdown(t_eval.stronger_answer_outline)
        else:
            st.warning("Session finished without recorded answers.")

        if st.button("🔄 Start Fresh Practice Round"):
            st.session_state.session = None
            st.rerun()

    else:
        # ACTIVE INTERVIEW ROUND
        curr_idx = session.current_turn_index
        turn = session.turns[curr_idx]
        q_item = turn.question

        # Progress bar
        progress_val = (curr_idx) / session.total_questions
        st.progress(progress_val)
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            st.caption(f"Question {curr_idx + 1} of {session.total_questions} | {session.target_role} • {session.experience_level}")
        with col_p2:
            cat_badge = "🧭 Behavioral (STAR)" if q_item.category == QuestionCategory.BEHAVIORAL else "💻 Technical Concept" if q_item.category == QuestionCategory.TECHNICAL else "🏗️ Project Architecture"
            st.markdown(f"**Domain:** `{cat_badge}`")

        # Question Presentation Box
        st.markdown(f"""
        <div class="question-box">
            <span style="font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#2563eb; letter-spacing:0.05em;">
                Question {curr_idx + 1} • {q_item.competency_or_topic}
            </span>
            <p style="font-size:1.25rem; font-weight:700; color:#0f172a; margin-top:8px; line-height:1.5;">
                {q_item.question_text}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Scaffolding Guidance Expander
        with st.expander("💡 Structural Guidance & Framework Checklist", expanded=False):
            st.markdown("**What Interviewers Look For:**")
            for h in q_item.rubric_hints:
                st.markdown(f"- {h}")

            if q_item.category == QuestionCategory.BEHAVIORAL:
                st.info("**STAR Breakdown:**\n- **S (Situation):** Project context & deadline (15%)\n- **T (Task):** Your specific mandate (10%)\n- **A (Action):** What YOU decided, coded, and did (60%)\n- **R (Result):** Observable outcome and takeaway (15%)")
            elif q_item.category == QuestionCategory.TECHNICAL:
                st.info("**Technical Answer Progression:**\n1. Core definition\n2. Internal mechanics & complexity (O-notation)\n3. Real-world trade-offs (space vs time, write vs read)\n4. Concrete example from your project")
            else:
                st.info("**Project Deep-Dive Structure:**\n1. Problem & high-level architecture\n2. Why this stack over alternatives\n3. Hardest technical bug or bottleneck YOU solved\n4. What you would architect differently today")

        # STAGE A: PRIMARY ANSWER INPUT
        if not session.in_followup and not turn.completed:
            st.markdown("#### ✍️ Type Your Response")
            user_input = st.text_area(
                "Your Response:",
                value=turn.initial_answer,
                height=180,
                placeholder="Type your response here in your authentic voice. Use 'I' to highlight your personal actions and decisions...",
                key=f"ans_input_{curr_idx}",
            )

            word_count = len(user_input.strip().split()) if user_input.strip() else 0
            pacing_html = get_word_pacing_pill(word_count)
            st.markdown(f"**Pacing:** {word_count} words {pacing_html}", unsafe_allow_html=True)

            col_sub1, col_sub2 = st.columns([1, 4])
            with col_sub1:
                if st.button("Submit Answer 💬", type="primary", use_container_width=True):
                    if not user_input.strip():
                        st.warning("Please type your answer before submitting.")
                    else:
                        turn.initial_answer = user_input.strip()
                        with st.spinner(f"{st.session_state.interviewer_persona.split('(')[0]} is listening and formulating a follow-up probe..."):
                            if "Live LLM" in eval_engine and st.session_state.api_key:
                                init_eval = evaluate_with_llm(
                                    q_item,
                                    turn.initial_answer,
                                    candidate_context=session.candidate_context,
                                    api_key=st.session_state.api_key,
                                )
                            else:
                                init_eval = evaluate_heuristically(
                                    q_item,
                                    turn.initial_answer,
                                    candidate_context=session.candidate_context,
                                )

                            turn.initial_evaluation = init_eval
                            if init_eval.suggested_followup_question:
                                turn.followup_question = init_eval.suggested_followup_question

                            session.in_followup = True
                            save_session(session)
                            st.rerun()

        # STAGE B: FOLLOW-UP PROBE & FINAL TURN EVALUATION
        elif session.in_followup and not turn.completed:
            with st.expander("📄 Review Your Initial Response", expanded=False):
                st.write(turn.initial_answer)

            persona_name = st.session_state.interviewer_persona.split("(")[0].strip()
            st.markdown(f"""
            <div class="followup-box">
                <span style="font-size:0.8rem; font-weight:700; color:#b45309; text-transform:uppercase; letter-spacing:0.05em;">
                    ⚡ {persona_name}'s Follow-Up Question
                </span>
                <p style="font-size:1.18rem; font-weight:700; color:#78350f; margin-top:6px; margin-bottom:0;">
                    "{turn.followup_question or q_item.default_followup}"
                </p>
            </div>
            """, unsafe_allow_html=True)

            followup_input = st.text_area(
                "Your Follow-Up Response:",
                value=turn.followup_answer,
                height=140,
                placeholder="Address the follow-up question directly. Elaborate on the trade-offs, edge cases, or metrics...",
                key=f"followup_input_{curr_idx}",
            )
            f_word_count = len(followup_input.strip().split()) if followup_input.strip() else 0
            st.caption(f"Follow-up length: {f_word_count} words")

            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                if st.button("Submit Follow-Up & Complete Turn 🎯", type="primary", use_container_width=True):
                    turn.followup_answer = followup_input.strip()
                    with st.spinner("Scoring combined response against visible 4-part rubric..."):
                        if "Live LLM" in eval_engine and st.session_state.api_key:
                            full_eval = evaluate_with_llm(
                                q_item,
                                turn.initial_answer,
                                followup_answer=turn.followup_answer,
                                candidate_context=session.candidate_context,
                                api_key=st.session_state.api_key,
                            )
                        else:
                            full_eval = evaluate_heuristically(
                                q_item,
                                turn.initial_answer,
                                followup_answer=turn.followup_answer,
                                candidate_context=session.candidate_context,
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

        # STAGE C: DIAGNOSTIC RUBRIC FEEDBACK DISPLAY
        elif turn.completed and turn.turn_evaluation:
            t_eval = turn.turn_evaluation

            st.markdown("### 📊 Turn Diagnostic Results")
            col_sc, col_badge = st.columns([1, 2])
            with col_sc:
                st.metric("Turn Score", f"{t_eval.overall_score} / 5.0")
            with col_badge:
                st.markdown("**Performance Level:**")
                st.markdown(get_performance_badge(t_eval.overall_score), unsafe_allow_html=True)

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

            # Strengths & Actionable Improvements
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
            with st.expander("🧭 View Stronger Answer Structural Blueprint (Authentic Framing)", expanded=True):
                st.markdown(t_eval.stronger_answer_outline)

            st.markdown("---")
            is_last = (curr_idx + 1) >= session.total_questions
            btn_label = "Conclude Interview & View Final Report 🎉" if is_last else "Proceed to Next Question ➡️"
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
# TAB 2: SPOT THE FLAW INTERACTIVE GAME (NEW & EXPLORATIVE)
# ==============================================================================
with tab_flaw_game:
    st.header("🎮 Spot the Interview Flaw: Interviewer Eye Training")
    st.markdown("""
    The fastest way to improve your own interview answers is learning to spot common red flags in other candidates' responses.
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
# TAB 3: INTERACTIVE STAR STORY BUILDER (NEW & EXPLORATIVE)
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

        # Live STAR Component Checklist
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
# TAB 4: COMPREHENSIVE QUESTION BANK
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
# TAB 5: INTERVIEW PLAYBOOKS & CHEAT SHEETS (NEW & EXPLORATIVE)
# ==============================================================================
with tab_playbook:
    st.header("📖 Student Interview Playbooks & Cheat Sheets")
    st.markdown("Actionable reference guides to elevate your technical communication and interview confidence.")

    playbook_choice = st.selectbox(
        "Select Playbook:",
        [
            "The 60-Second 'Tell Me About Yourself' Formula",
            "Technical Architecture Trade-offs Matrix",
            "Top 8 Student Interview Trap Questions & How to Answer",
            "Pre-Interview Mental Reset & Body Language Checklist",
        ],
    )

    if playbook_choice == "The 60-Second 'Tell Me About Yourself' Formula":
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

    elif playbook_choice == "Technical Architecture Trade-offs Matrix":
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
# TAB 6: PRACTICE ANALYTICS & HISTORY
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
# TAB 7: EXPORT PRACTICE REPORT
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
# TAB 8: TRANSPARENT RUBRIC & ETHICAL GUARDRAILS
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
