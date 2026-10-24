"""
InterviewIQ - AI Mock Interview & Diagnostic Rubric Studio
Streamlit Application for internship and graduate-job applicants.
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
    page_title="InterviewIQ - Mock Interview & Practice Rubric Studio",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize database
init_db()

# Custom CSS for polished typography, badges, and card containers
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .disclaimer-banner {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 12px 18px;
        border-radius: 6px;
        font-size: 0.88rem;
        color: #1e293b;
        margin-bottom: 1.5rem;
    }
    .ethics-banner {
        background-color: #f0fdf4;
        border-left: 4px solid #10b981;
        padding: 10px 16px;
        border-radius: 6px;
        font-size: 0.85rem;
        color: #065f46;
        margin-bottom: 1.2rem;
    }
    .question-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        margin-bottom: 1.5rem;
    }
    .followup-box {
        background-color: #fefce8;
        border: 1px solid #fef08a;
        border-left: 5px solid #eab308;
        padding: 18px;
        border-radius: 8px;
        margin: 1.2rem 0;
    }
    .score-badge {
        font-size: 1.1rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 6px;
        display: inline-block;
    }
    .badge-advanced { background: #dcfce7; color: #166534; }
    .badge-proficient { background: #dbeafe; color: #1e40af; }
    .badge-developing { background: #fef3c7; color: #92400e; }
    .stProgress > div > div > div > div {
        background-color: #2563eb;
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


def get_performance_badge(score: float) -> str:
    if score >= 4.2:
        return '<span class="score-badge badge-advanced">🌟 Advanced (4.2 - 5.0)</span>'
    elif score >= 3.2:
        return '<span class="score-badge badge-proficient">📈 Proficient (3.2 - 4.1)</span>'
    else:
        return '<span class="score-badge badge-developing">🌱 Developing (1.0 - 3.1)</span>'


# Sidebar setup
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/interview.png", width=64)
    st.title("InterviewIQ Studio")
    st.caption("Structured practice for high-stakes interviews")

    st.markdown("---")
    st.subheader("⚙️ Session Configuration")

    candidate_name = st.text_input("Candidate Name", value="Student Candidate", help="Used to personalize practice reports")
    target_role = st.selectbox(
        "Target Role",
        [r.value for r in TargetRole],
        index=0,
        help="Select the exact role you are applying to",
    )
    experience_level = st.selectbox(
        "Experience Level",
        [e.value for e in ExperienceLevel],
        index=0,
        help="Tailors scoring expectations and question nuance",
    )
    interview_type = st.selectbox(
        "Interview Type",
        [t.value for t in InterviewType],
        index=0,
        help="Select interview focus domain",
    )
    num_questions = st.slider(
        "Number of Questions",
        min_value=5,
        max_value=8,
        value=6,
        help="Recommended 5-8 questions for realistic interview stamina",
    )

    candidate_context = st.text_area(
        "Your Real Background / Projects (Optional)",
        placeholder="e.g. Built a Distributed Key-Value store in Go; Computer Networks capstone; React & Node.js e-commerce app...",
        help="Helps the coach anchor outlines to your genuine work without fabricating credentials.",
        height=90,
    )

    with st.expander("🤖 Evaluator Engine Settings"):
        eval_engine = st.radio(
            "Evaluation Engine",
            ["Intelligent Offline Diagnostic (No API Key Required)", "Live LLM (Gemini / OpenAI)"],
            index=0 if not st.session_state.api_key else 1,
        )
        api_key_input = st.text_input(
            "LLM API Key (Optional)",
            value=st.session_state.api_key,
            type="password",
            help="Gemini or OpenAI API key. Leave blank to use the offline rubric engine.",
        )
        if api_key_input != st.session_state.api_key:
            st.session_state.api_key = api_key_input

    st.markdown("---")
    if st.button("🚀 Start New Interview Session", type="primary", use_container_width=True):
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
        st.success(f"Session initialized with {len(questions)} balanced questions!")
        st.rerun()

    if st.session_state.session and not st.session_state.session.is_finished:
        if st.button("⏹️ End Current Session Early", use_container_width=True):
            st.session_state.session.is_finished = True
            st.session_state.session.completed_at = time.time()
            save_session(st.session_state.session)
            st.rerun()


# Top Header Banner
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="main-header">🎯 InterviewIQ Practice Studio</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Repeatable, structured mock interviews with transparent rubric feedback. Built for students & early-career job seekers.</div>',
        unsafe_allow_html=True,
    )
with col_h2:
    if st.session_state.session:
        s = st.session_state.session
        st.info(f"**Session:** `{s.session_id}`\n\n**Role:** {s.target_role.split('(')[0]}")

# Transparent Notices
st.markdown(
    f'<div class="disclaimer-banner"><strong>ℹ️ Transparent Rubric Notice:</strong> {RUBRIC_DISCLAIMER}</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div class="ethics-banner"><strong>🛡️ Ethical Coaching Guarantee:</strong> {ETHICAL_OUTLINE_GUIDELINE}</div>',
    unsafe_allow_html=True,
)

# Main Navigation Tabs
tab_studio, tab_bank, tab_analytics, tab_report, tab_rubric = st.tabs([
    "🎯 Mock Interview Studio",
    "📚 Question Bank & STAR Coach",
    "📊 Practice Analytics & History",
    "📑 Export Practice Report",
    "⚖️ Transparent Rubric & Guidelines",
])


# ==============================================================================
# TAB 1: MOCK INTERVIEW STUDIO
# ==============================================================================
with tab_studio:
    session: InterviewSession = st.session_state.session

    if session is None:
        st.markdown("""
        ### 👋 Welcome to InterviewIQ!
        No active interview session found. Configure your target role and click **'Start New Interview Session'** in the left sidebar to begin.

        #### What makes InterviewIQ different?
        - **One Question at a Time:** Realistic interview rhythm without overwhelming walls of text.
        - **Contextual Follow-Up Questions:** Probing deeper into your decisions, trade-offs, and metrics.
        - **Visible 4-Part Rubric:** Transparent scoring on *Relevance*, *Structure*, *Evidence*, and *Clarity*.
        - **Zero Fabrication:** Constructive advice that sharpens how you present your **real** projects and coursework without inventing fake qualifications.
        """)

        # Quick Start Cards
        col_c1, col_c2, col_c3 = st.columns(3)
        with col_c1:
            st.markdown("#### 💻 Technical Deep-Dive")
            st.write("Role-specific algorithms, system architecture, database optimization, and performance trade-offs.")
        with col_c2:
            st.markdown("#### 🧭 Behavioral (STAR)")
            st.write("Master Situation, Task, Action, and Result framing for conflict, leadership, and resilience.")
        with col_c3:
            st.markdown("#### 🏗️ Project Architecture")
            st.write("Defend your design choices, technical trade-offs, debugging stories, and retrospect lessons.")

    elif session.is_finished:
        st.success("🎉 **Interview Session Completed!** Review your executive scorecard below or export your report.")

        # Compute summary scores
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
                st.markdown(f"**Completed:** {len(valid_turns)} of {session.total_questions} questions answered with follow-ups.")

            # Turn-by-turn recap expanders
            st.markdown("### 📝 Turn-by-Turn Diagnostic Review")
            for i, turn in enumerate(session.turns):
                t_eval = turn.turn_evaluation or turn.initial_evaluation
                with st.expander(f"Question {i+1}: {turn.question.question_text[:70]}... (Score: {t_eval.overall_score if t_eval else 'N/A'}/5.0)"):
                    st.markdown(f"**Full Question:** {turn.question.question_text}")
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

                        st.markdown("#### 🚀 Actionable Improvements")
                        for imp in t_eval.actionable_improvements:
                            st.write(f"- {imp}")

                        st.markdown(t_eval.stronger_answer_outline)
        else:
            st.warning("Session ended before answers were submitted.")

        if st.button("🔄 Start Another Practice Session"):
            st.session_state.session = None
            st.rerun()

    else:
        # ACTIVE INTERVIEW IN PROGRESS
        curr_idx = session.current_turn_index
        turn = session.turns[curr_idx]
        q_item = turn.question

        # Progress bar
        progress_val = (curr_idx) / session.total_questions
        st.progress(progress_val)
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            st.caption(f"Question {curr_idx + 1} of {session.total_questions} | {session.target_role} ({session.experience_level})")
        with col_p2:
            cat_badge = "🧭 Behavioral" if q_item.category == QuestionCategory.BEHAVIORAL else "💻 Technical" if q_item.category == QuestionCategory.TECHNICAL else "🏗️ Project Architecture"
            st.markdown(f"**Domain:** `{cat_badge}`")

        # Question Presentation Card
        st.markdown(f"""
        <div class="question-card">
            <h3 style="margin-top:0; color:#1e3a8a;">Question {curr_idx + 1}</h3>
            <p style="font-size:1.18rem; font-weight:600; color:#0f172a; line-height:1.5;">{q_item.question_text}</p>
            <p style="font-size:0.9rem; color:#64748b; margin-bottom:0;"><strong>Key Focus:</strong> {q_item.competency_or_topic}</p>
        </div>
        """, unsafe_allow_html=True)

        # Scaffolding Hints Expander
        with st.expander("💡 Interviewer Expectations & Answer Framework Helpers"):
            st.markdown("**What Interviewers Look For:**")
            for h in q_item.rubric_hints:
                st.markdown(f"- {h}")

            if q_item.category == QuestionCategory.BEHAVIORAL:
                st.info("**STAR Framework Reminder:**\n- **S (Situation):** Set context & stakes (10-15%)\n- **T (Task):** Your specific role (10%)\n- **A (Action):** What YOU did, decided, and coded (60%)\n- **R (Result):** Observable impact & learnings (15-20%)")
            elif q_item.category == QuestionCategory.TECHNICAL:
                st.info("**Technical Answer Architecture:**\n1. Define concept concisely\n2. Explain internal data structure or protocol mechanics\n3. Discuss trade-offs (space vs time, write vs read bottlenecks)\n4. Provide a concrete example from your own work")
            else:
                st.info("**Project Deep-Dive Structure:**\n1. User problem & architecture\n2. Why this stack over alternatives\n3. Hardest technical decision YOU owned\n4. Bug troubleshooting & hindsight improvements")

        # STAGE A: PRIMARY ANSWER SUBMISSION
        if not session.in_followup and not turn.completed:
            st.markdown("#### ✍️ Type Your Response")
            user_input = st.text_area(
                "Your Answer:",
                value=turn.initial_answer,
                height=180,
                placeholder="Type your answer here in your own words. Use 'I' to highlight your genuine contributions...",
                key=f"ans_input_{curr_idx}",
            )

            word_count = len(user_input.strip().split()) if user_input.strip() else 0
            st.caption(f"Word count: {word_count} words | Aim for 60–250 words for a balanced answer.")

            col_sub1, col_sub2 = st.columns([1, 4])
            with col_sub1:
                if st.button("Submit Answer 💬", type="primary", use_container_width=True):
                    if not user_input.strip():
                        st.warning("Please type an answer before submitting.")
                    else:
                        turn.initial_answer = user_input.strip()

                        # Evaluate initial answer to generate contextual follow-up
                        with st.spinner("Analyzing answer and preparing contextual follow-up question..."):
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
                            # Use custom generated follow-up if available
                            if init_eval.suggested_followup_question:
                                turn.followup_question = init_eval.suggested_followup_question

                            session.in_followup = True
                            save_session(session)
                            st.rerun()

        # STAGE B: FOLLOW-UP QUESTION & TURN EVALUATION
        elif session.in_followup and not turn.completed:
            # Display candidate's initial answer in collapsible card
            with st.expander("📄 Review Your Initial Answer", expanded=False):
                st.write(turn.initial_answer)

            # Prominent Follow-up Question Callout
            st.markdown(f"""
            <div class="followup-box">
                <span style="font-size:0.85rem; font-weight:700; color:#854d0e; text-transform:uppercase; letter-spacing:0.05em;">Interviewer Follow-Up Question</span>
                <p style="font-size:1.15rem; font-weight:600; color:#713f12; margin-top:6px; margin-bottom:0;">
                    "{turn.followup_question or q_item.default_followup}"
                </p>
            </div>
            """, unsafe_allow_html=True)

            followup_input = st.text_area(
                "Your Follow-Up Response:",
                value=turn.followup_answer,
                height=140,
                placeholder="Elaborate on the specific trade-offs, edge cases, or metrics mentioned above...",
                key=f"followup_input_{curr_idx}",
            )
            f_word_count = len(followup_input.strip().split()) if followup_input.strip() else 0
            st.caption(f"Follow-up word count: {f_word_count} words")

            col_f1, col_f2, col_f3 = st.columns([2, 2, 3])
            with col_f1:
                if st.button("Submit Follow-Up & Score 🎯", type="primary", use_container_width=True):
                    turn.followup_answer = followup_input.strip()
                    with st.spinner("Scoring complete turn against 4-part rubric..."):
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
                    turn.followup_answer = "[Skipped by candidate]"
                    turn.turn_evaluation = turn.initial_evaluation
                    turn.completed = True
                    session.in_followup = False
                    save_session(session)
                    st.rerun()

        # STAGE C: COMPLETED TURN FEEDBACK CARD
        elif turn.completed and turn.turn_evaluation:
            t_eval = turn.turn_evaluation

            st.markdown("### 📊 Turn Diagnostic Feedback")
            col_sc, col_badge = st.columns([1, 2])
            with col_sc:
                st.metric("Turn Score", f"{t_eval.overall_score} / 5.0")
            with col_badge:
                st.markdown("**Performance Band:**")
                st.markdown(get_performance_badge(t_eval.overall_score), unsafe_allow_html=True)

            # Rubric Breakdown Grid
            st.markdown("#### Visible Rubric Breakdown")
            c_r1, c_r2, c_r3, c_r4 = st.columns(4)
            r_keys = ["relevance", "structure", "evidence", "clarity"]
            cols_list = [c_r1, c_r2, c_r3, c_r4]
            for idx, k in enumerate(r_keys):
                if k in t_eval.rubric_scores:
                    crit = t_eval.rubric_scores[k]
                    with cols_list[idx]:
                        st.metric(crit.display_name, f"{crit.score} / 5.0")
                        st.caption(crit.feedback)

            # Strengths & Growth Areas
            col_str, col_imp = st.columns(2)
            with col_str:
                st.markdown("#### 🌟 Key Strengths")
                for s in t_eval.key_strengths:
                    st.markdown(f"- {s}")
            with col_imp:
                st.markdown("#### 🚀 Actionable Growth Advice")
                for imp in t_eval.actionable_improvements:
                    st.markdown(f"- {imp}")

            # Stronger Answer Outline (Ethical)
            with st.expander("🧭 View Stronger Answer Outline (Authentic Blueprint)", expanded=True):
                st.markdown(t_eval.stronger_answer_outline)

            st.markdown("---")
            # Next button
            is_last = (curr_idx + 1) >= session.total_questions
            btn_label = "Finish Interview & View Final Report 🎉" if is_last else "Proceed to Next Question ➡️"
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
# TAB 2: QUESTION BANK & STAR COACH
# ==============================================================================
with tab_bank:
    st.header("📚 Comprehensive Question Bank & STAR Coach")
    st.markdown("Explore role-specific technical questions, curated behavioral prompts, and test your STAR responses.")

    bank_category = st.radio(
        "Select Category to Explore",
        ["Behavioral Competencies (STAR)", "Role-Specific Technical", "Project Architecture & Deep-Dive"],
        horizontal=True,
    )

    if bank_category == "Behavioral Competencies (STAR)":
        st.subheader("Behavioral Question Bank with STAR Scoring Guides")
        for q in BEHAVIORAL_QUESTIONS:
            with st.expander(f"📌 {q['competency']}: {q['question_text']}"):
                st.markdown(f"**Full Question:** {q['question_text']}")
                st.markdown(f"**Default Follow-Up Probe:** *\"{q['default_followup']}\"*")
                st.markdown("**What Interviewers Look For:**")
                for hint in q["rubric_hints"]:
                    st.markdown(f"- {hint}")

    elif bank_category == "Role-Specific Technical":
        st.subheader("Role-Specific Technical Quizzes")
        role_select = st.selectbox(
            "Filter by Role",
            list(TECHNICAL_QUESTIONS_BY_ROLE.keys()),
        )
        tech_list = TECHNICAL_QUESTIONS_BY_ROLE.get(role_select, [])
        for q in tech_list:
            with st.expander(f"⚙️ {q['topic']}: {q['question_text']}"):
                st.markdown(f"**Technical Prompt:** {q['question_text']}")
                st.markdown(f"**Technical Follow-Up:** *\"{q['default_followup']}\"*")
                st.markdown("**Core Technical Rubric Hints:**")
                for hint in q["rubric_hints"]:
                    st.markdown(f"- {hint}")

    else:
        st.subheader("Project-Explanation & Architecture Bank")
        for q in PROJECT_QUESTIONS:
            with st.expander(f"🏗️ {q['competency']}: {q['question_text']}"):
                st.markdown(f"**Architecture Prompt:** {q['question_text']}")
                st.markdown(f"**Follow-Up Challenge:** *\"{q['default_followup']}\"*")
                st.markdown("**Architectural Expectations:**")
                for hint in q["rubric_hints"]:
                    st.markdown(f"- {hint}")

    st.markdown("---")
    st.subheader("🧪 Interactive STAR Response Sandbox")
    st.caption("Practice drafting an answer to any question and receive instant diagnostic feedback.")

    sandbox_q_text = st.selectbox(
        "Select Practice Prompt:",
        [q["question_text"] for q in BEHAVIORAL_QUESTIONS] + [q["question_text"] for q in PROJECT_QUESTIONS],
    )
    sandbox_input = st.text_area(
        "Draft your STAR answer:",
        placeholder="Situation: In my software engineering course... Task: My responsibility was... Action: I implemented... Result: As a result, latency decreased...",
        height=140,
        key="sandbox_textarea",
    )
    if st.button("Evaluate STAR Response"):
        if not sandbox_input.strip():
            st.warning("Please type an answer to evaluate.")
        else:
            dummy_q = QuestionItem(
                id="sandbox_q",
                category=QuestionCategory.BEHAVIORAL,
                role="General",
                question_text=sandbox_q_text,
                competency_or_topic="STAR Practice",
            )
            with st.spinner("Evaluating against rubric..."):
                sb_eval = evaluate_heuristically(dummy_q, sandbox_input)
                st.metric("Rubric Score", f"{sb_eval.overall_score} / 5.0")
                st.markdown(get_performance_badge(sb_eval.overall_score), unsafe_allow_html=True)
                st.markdown("#### Strengths & Areas to Polish")
                for s in sb_eval.key_strengths:
                    st.write(f"✅ {s}")
                for imp in sb_eval.actionable_improvements:
                    st.write(f"💡 {imp}")


# ==============================================================================
# TAB 3: PRACTICE ANALYTICS & HISTORY
# ==============================================================================
with tab_analytics:
    st.header("📊 Student Practice Analytics & Local History")
    st.caption("Historical progress stored securely in your local SQLite database.")

    analytics = get_aggregate_analytics()

    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    with col_m1:
        st.metric("Total Sessions Recorded", analytics["total_sessions"])
    with col_m2:
        st.metric("Questions Answered", analytics["total_answers_submitted"])
    with col_m3:
        st.metric("Avg Session Score", f"{analytics['avg_session_score']} / 5.0")
    with col_m4:
        st.metric("Structure Average", f"{analytics['avg_structure']} / 5.0")

    st.markdown("---")

    # Historical Rubric Breakdown Bar Chart
    if analytics["total_sessions"] > 0:
        st.subheader("📈 Performance Breakdown Across Rubric Criteria")
        rubric_df = pd.DataFrame({
            "Criterion": ["Relevance", "Structure", "Evidence", "Clarity"],
            "Average Score (1-5)": [
                analytics["avg_relevance"],
                analytics["avg_structure"],
                analytics["avg_evidence"],
                analytics["avg_clarity"],
            ]
        })
        st.bar_chart(rubric_df.set_index("Criterion"))

    # Past Sessions Table
    st.subheader("📜 Recorded Practice Sessions")
    past_sessions = list_sessions(limit=30)
    if not past_sessions:
        st.info("No saved practice sessions found yet. Start an interview session to build your history!")
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

        st.markdown("#### 🔍 Load Session Transcript")
        select_sess_id = st.selectbox("Select Session ID to inspect:", [s["session_id"] for s in past_sessions])
        if st.button("Load Past Session"):
            sess_data = get_session(select_sess_id)
            if sess_data:
                st.json(sess_data)


# ==============================================================================
# TAB 4: EXPORT PRACTICE REPORT
# ==============================================================================
with tab_report:
    st.header("📑 Export Practice Report")
    st.caption("Generate clean Markdown, HTML (Printable to PDF), and JSON practice summaries.")

    current_sess = st.session_state.session
    if not current_sess:
        st.info("Start or complete an interview session to export your personalized report.")
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
        st.subheader("Preview Report")
        st.markdown(md_report)


# ==============================================================================
# TAB 5: RUBRIC & ETHICS TRANSPARENCY
# ==============================================================================
with tab_rubric:
    st.header("⚖️ Transparent Rubric & Ethical Guardrails")
    st.markdown("""
    InterviewIQ believes that artificial intelligence should empower students through **transparent criteria**
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
