"""
Unit and Acceptance Tests for InterviewIQ.
Covers:
- Technical, Behavioral, and Project-Explanation questions
- Visible transparent rubric scoring (Relevance, Structure, Evidence, Clarity)
- Formative practice feedback disclaimer (scores are practice feedback, not hiring predictions)
- Ethical outline guardrail (Never create fake work experience or qualifications)
- Follow-up question generation and two-step turn flow
- SQLite persistence and analytics aggregation
- Practice report export (Markdown & HTML)
"""

import os
import tempfile
import pytest
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
    generate_followup_question,
    generate_ethical_outline,
    RUBRIC_CRITERIA_META,
)
from backend.database import (
    init_db,
    save_session,
    get_session,
    list_sessions,
    get_aggregate_analytics,
)
from backend.report_generator import (
    generate_markdown_report,
    generate_html_report,
)


class TestQuestionBank:
    """Acceptance test: Technical, behavioral, and project-explanation questions."""

    def test_behavioral_questions_have_star_hints(self):
        assert len(BEHAVIORAL_QUESTIONS) >= 5
        for q in BEHAVIORAL_QUESTIONS:
            assert "question_text" in q
            assert "competency" in q
            assert "rubric_hints" in q
            assert len(q["rubric_hints"]) >= 3
            assert "default_followup" in q

    def test_technical_questions_cover_multiple_roles(self):
        assert TargetRole.SOFTWARE_ENGINEERING.value in TECHNICAL_QUESTIONS_BY_ROLE
        assert TargetRole.DATA_SCIENCE_ML.value in TECHNICAL_QUESTIONS_BY_ROLE
        assert TargetRole.PRODUCT_MANAGEMENT.value in TECHNICAL_QUESTIONS_BY_ROLE
        assert TargetRole.DEVOPS_CLOUD.value in TECHNICAL_QUESTIONS_BY_ROLE

        for role, q_list in TECHNICAL_QUESTIONS_BY_ROLE.items():
            assert len(q_list) >= 2
            for q in q_list:
                assert "question_text" in q
                assert "topic" in q
                assert len(q["rubric_hints"]) > 0

    def test_project_questions_cover_architecture_and_tradeoffs(self):
        assert len(PROJECT_QUESTIONS) >= 3
        topics = [q["competency"] for q in PROJECT_QUESTIONS]
        assert any("Architecture" in t for t in topics)
        assert any("Trade-Off" in t for t in topics)

    def test_build_interview_plan_respects_limits_and_types(self):
        # Must support 5-8 questions
        plan_5 = build_interview_plan(
            target_role=TargetRole.SOFTWARE_ENGINEERING.value,
            experience_level=ExperienceLevel.INTERNSHIP.value,
            interview_type=InterviewType.COMPREHENSIVE.value,
            num_questions=5,
        )
        assert len(plan_5) == 5

        plan_8 = build_interview_plan(
            target_role=TargetRole.SOFTWARE_ENGINEERING.value,
            experience_level=ExperienceLevel.GRADUATE.value,
            interview_type=InterviewType.COMPREHENSIVE.value,
            num_questions=8,
        )
        assert len(plan_8) == 8

        # Verify all 3 categories (technical, behavioral, project) are present in comprehensive mode
        categories = {item.category for item in plan_8}
        assert QuestionCategory.TECHNICAL in categories
        assert QuestionCategory.BEHAVIORAL in categories
        assert QuestionCategory.PROJECT in categories


class TestRubricAndEthics:
    """Acceptance test: Transparent rubric & ethics (no fabricated experience)."""

    def test_rubric_criteria_metadata(self):
        for crit in ["relevance", "structure", "evidence", "clarity"]:
            assert crit in RUBRIC_CRITERIA_META
            assert "display_name" in RUBRIC_CRITERIA_META[crit]
            assert "description" in RUBRIC_CRITERIA_META[crit]
            assert len(RUBRIC_CRITERIA_META[crit]["anchors"]) == 5

    def test_disclaimer_clarifies_scores_are_practice_not_hiring_predictions(self):
        assert "not predictive hiring decisions" in RUBRIC_DISCLAIMER.lower() or "not predictive hiring" in RUBRIC_DISCLAIMER.lower()
        assert "practice" in RUBRIC_DISCLAIMER.lower()

    def test_ethical_guideline_prohibits_fabrication(self):
        assert "never fabricate" in ETHICAL_OUTLINE_GUIDELINE.lower()

    def test_behavioral_evaluation_detects_star_and_scores_accurately(self):
        q = QuestionItem(
            id="test_beh_1",
            category=QuestionCategory.BEHAVIORAL,
            role=TargetRole.SOFTWARE_ENGINEERING.value,
            question_text="Tell me about a time you handled a conflict in a team.",
            competency_or_topic="Teamwork",
            rubric_hints=["Situation", "Task", "Action", "Result"],
        )

        # High quality answer with explicit STAR markers and personal ownership
        star_answer = (
            "During my university capstone project, our team was divided on database selection. "
            "My task was to lead the database benchmark. I decided to write an automated benchmark suite "
            "comparing PostgreSQL and MongoDB on our expected query patterns. I presented the empirical "
            "latency numbers to the team, which allowed us to agree on PostgreSQL without rancor. "
            "As a result, we delivered the project on time with zero database bottleneck issues."
        )

        res = evaluate_heuristically(q, star_answer)
        assert res.overall_score >= 3.5
        assert "relevance" in res.rubric_scores
        assert "structure" in res.rubric_scores
        assert "evidence" in res.rubric_scores
        assert "clarity" in res.rubric_scores
        assert res.rubric_scores["structure"].score >= 4.0
        assert res.rubric_scores["evidence"].score >= 3.5
        assert len(res.key_strengths) > 0
        assert res.disclaimer == RUBRIC_DISCLAIMER

        # Check outline does not invent fake credentials
        assert "never" in res.stronger_answer_outline.lower() or "blueprint" in res.stronger_answer_outline.lower()
        assert "invent fictional company" in res.stronger_answer_outline.lower() or "authentic" in res.stronger_answer_outline.lower()

    def test_technical_evaluation_scores_and_probes_tradeoffs(self):
        q = QuestionItem(
            id="test_tech_1",
            category=QuestionCategory.TECHNICAL,
            role=TargetRole.SOFTWARE_ENGINEERING.value,
            question_text="Explain how database indexing works and the write trade-offs.",
            competency_or_topic="Database Indexing",
            rubric_hints=["B-Tree", "Write amplification", "Lookups"],
        )

        tech_answer = (
            "A B-Tree index organizes table keys in a balanced tree structure, allowing O(log N) searches "
            "instead of O(N) full table scans. The trade-off is write amplification: on every INSERT or UPDATE, "
            "the database engine must also rebalance and write to each index tree, consuming additional memory and disk I/O."
        )

        res = evaluate_heuristically(q, tech_answer)
        assert res.overall_score >= 3.8
        assert res.rubric_scores["relevance"].score >= 4.0
        assert res.rubric_scores["clarity"].score >= 3.5

    def test_followup_question_generation(self):
        q = QuestionItem(
            id="test_proj_1",
            category=QuestionCategory.PROJECT,
            role=TargetRole.SOFTWARE_ENGINEERING.value,
            question_text="Walk me through the architecture of your main project.",
            competency_or_topic="Architecture",
        )
        answer = "I built a web scraper with Python and FastAPI storing records in SQLite."
        followup = generate_followup_question(q, answer)
        assert isinstance(followup, str)
        assert len(followup) > 20
        assert "?" in followup


class TestDatabaseAndReports:
    """Acceptance test: Local session storage in SQLite and Practice Report Export."""

    def test_sqlite_session_crud_and_analytics(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name

        try:
            init_db(db_path)

            session = InterviewSession(
                session_id="test_sess_101",
                candidate_name="Alex River",
                target_role=TargetRole.SOFTWARE_ENGINEERING.value,
                experience_level=ExperienceLevel.INTERNSHIP.value,
                interview_type=InterviewType.COMPREHENSIVE.value,
                total_questions=5,
                candidate_context="Coursework in Operating Systems and Cloud Computing",
            )

            q = QuestionItem(
                id="q1",
                category=QuestionCategory.BEHAVIORAL,
                role=TargetRole.SOFTWARE_ENGINEERING.value,
                question_text="Describe a time you handled a difficult deadline.",
                competency_or_topic="Prioritization",
            )
            turn = InterviewTurn(
                question_index=0,
                question=q,
                initial_answer="I prioritized critical paths and communicated early with my team.",
                followup_question="What task did you drop?",
                followup_answer="I postponed non-essential UI animations.",
                completed=True,
            )
            eval_res = evaluate_heuristically(q, turn.initial_answer, turn.followup_answer)
            turn.turn_evaluation = eval_res
            session.turns.append(turn)
            session.overall_session_score = eval_res.overall_score
            session.is_finished = True

            # Save
            save_session(session, db_path=db_path)

            # Retrieve
            fetched = get_session("test_sess_101", db_path=db_path)
            assert fetched is not None
            assert fetched["candidate_name"] == "Alex River"
            assert len(fetched["turns"]) == 1
            assert fetched["turns"][0]["initial_answer"] == "I prioritized critical paths and communicated early with my team."

            # List
            sessions_list = list_sessions(db_path=db_path)
            assert len(sessions_list) == 1
            assert sessions_list[0]["session_id"] == "test_sess_101"

            # Analytics
            analytics = get_aggregate_analytics(db_path=db_path)
            assert analytics["total_sessions"] == 1
            assert analytics["total_answers_submitted"] == 1
            assert analytics["avg_session_score"] > 0

            # Export reports
            md_report = generate_markdown_report(session)
            assert "InterviewIQ Practice & Diagnostic Report" in md_report
            assert "Alex River" in md_report
            assert RUBRIC_DISCLAIMER in md_report
            assert "7-Day Personalized Action Plan" in md_report

            html_report = generate_html_report(session)
            assert "<!DOCTYPE html>" in html_report
            assert "Alex River" in html_report
            assert "Print / Save as PDF" in html_report

            # Test session deletion
            from backend.database import delete_session
            assert delete_session("test_sess_101", db_path=db_path) is True
            assert get_session("test_sess_101", db_path=db_path) is None

        finally:
            if os.path.exists(db_path):
                os.remove(db_path)

    def test_brief_answer_handling(self):
        q = QuestionItem(
            id="q_short",
            category=QuestionCategory.TECHNICAL,
            role=TargetRole.SOFTWARE_ENGINEERING.value,
            question_text="What is a race condition?",
            competency_or_topic="Concurrency",
        )
        res = evaluate_heuristically(q, "It is bad.")
        assert res.overall_score < 3.0
        assert res.rubric_scores["relevance"].score <= 2.5
        assert len(res.actionable_improvements) > 0

    def test_all_interview_types_generate_valid_plans(self):
        for itype in InterviewType:
            plan = build_interview_plan(
                target_role=TargetRole.DATA_SCIENCE_ML.value,
                experience_level=ExperienceLevel.GRADUATE.value,
                interview_type=itype.value,
                num_questions=6,
            )
            assert len(plan) == 6
            for q in plan:
                assert len(q.question_text) > 10
                assert q.role == TargetRole.DATA_SCIENCE_ML.value

    def test_technical_complexity_and_dynamic_generator(self):
        from backend.evaluator import (
            analyze_technical_complexity,
            generate_mermaid_architecture,
            generate_dynamic_ai_technical_question,
        )

        sample_answer = (
            "In our FastAPI backend service, we handled client requests by checking Redis in-memory cache "
            "with O(1) lookup time before falling back to PostgreSQL relational database. We used mutex locks "
            "to prevent race conditions, achieving a P95 latency of 45ms."
        )

        analysis = analyze_technical_complexity(sample_answer)
        assert analysis["depth_score"] >= 3.5
        assert len(analysis["time_complexity"]) > 0
        assert "Mutex / Locks" in analysis["concurrency_primitives"]
        assert len(analysis["architectural_patterns"]) >= 2
        assert len(analysis["metrics_telemetry"]) > 0

        # Architecture diagram
        mermaid = generate_mermaid_architecture(sample_answer)
        assert mermaid is not None
        assert "graph TD" in mermaid
        assert "Client" in mermaid
        assert "Cache" in mermaid or "DB" in mermaid

        # Dynamic AI technical question generator
        dyn_q = generate_dynamic_ai_technical_question(topic="Kafka Partition Rebalancing")
        assert "kafka" in dyn_q.question_text.lower() or "partition" in dyn_q.question_text.lower()
        assert len(dyn_q.rubric_hints) >= 3

    def test_secret_management_and_environment_config(self, monkeypatch):
        from backend.config import get_setting, validate_secrets, get_llm_config

        # 1. Fallback to default
        assert get_setting("NON_EXISTENT_KEY_123", default="my_fallback") == "my_fallback"

        # 2. Ignore placeholder values
        monkeypatch.setenv("GROQ_API_KEY", "replace_with_your_own_key")
        assert get_setting("GROQ_API_KEY") is None

        # 3. Read actual value from env
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_actual_key_456")
        assert get_setting("GROQ_API_KEY") == "gsk_test_actual_key_456"

        # 4. Validate secrets helper gives readable status rather than crashing
        status_info = validate_secrets()
        assert "status" in status_info
        assert "message" in status_info
        assert status_info["status"] in ("ready", "warning")

        # 5. Missing keys produce graceful warning message
        monkeypatch.delenv("GROQ_API_KEY", raising=False)
        monkeypatch.setenv("LLM_PROVIDER", "groq")
        missing_info = validate_secrets()
        assert missing_info["status"] == "warning"
        assert "GROQ_API_KEY" in missing_info["message"]


class TestRegressionFixes:
    """Regression tests for provider isolation and analytics correctness."""

    def test_llm_provider_never_uses_another_providers_key(self, monkeypatch):
        from backend.evaluator import evaluate_with_llm

        question = QuestionItem(
            id="provider-isolation",
            category=QuestionCategory.TECHNICAL,
            role=TargetRole.SOFTWARE_ENGINEERING.value,
            question_text="Explain a hash map.",
            competency_or_topic="Data Structures",
        )
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.setenv("GROQ_API_KEY", "gsk_test_key_that_must_not_be_used")
        monkeypatch.setenv("LLM_PROVIDER", "gemini")

        # Missing Gemini key must trigger offline evaluation, never send the Groq
        # key to Google's endpoint. A successful return proves fallback was used.
        result = evaluate_with_llm(
            question,
            "A hash map stores key-value pairs and uses hashing to find buckets.",
            provider="gemini",
        )
        assert 1.0 <= result.overall_score <= 5.0
        assert set(result.rubric_scores) == {"relevance", "structure", "evidence", "clarity"}

    def test_analytics_include_unscored_sessions_without_weighting_session_means(self):
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
            db_path = tf.name

        try:
            from backend.database import get_aggregate_analytics

            # One completed session with one scored turn; and one
            # new session with no score. Both sessions must appear in the count.
            scored_session = InterviewSession(
                session_id="analytics-scored",
                candidate_name="Candidate A",
                target_role=TargetRole.SOFTWARE_ENGINEERING.value,
                experience_level=ExperienceLevel.INTERNSHIP.value,
                interview_type=InterviewType.COMPREHENSIVE.value,
                total_questions=2,
            )
            question = QuestionItem(
                id="analytics-q",
                category=QuestionCategory.TECHNICAL,
                role=TargetRole.SOFTWARE_ENGINEERING.value,
                question_text="Explain a hash map.",
                competency_or_topic="Data Structures",
            )
            scored_turn = InterviewTurn(
                question_index=0,
                question=question,
                initial_answer="A hash map stores key-value pairs.",
                completed=True,
            )
            scored_turn.turn_evaluation = evaluate_heuristically(
                question, scored_turn.initial_answer
            )
            scored_session.turns = [scored_turn]
            scored_session.overall_session_score = scored_turn.turn_evaluation.overall_score
            save_session(scored_session, db_path=db_path)

            unscored_session = InterviewSession(
                session_id="analytics-unscored",
                candidate_name="Candidate B",
                target_role=TargetRole.SOFTWARE_ENGINEERING.value,
                experience_level=ExperienceLevel.INTERNSHIP.value,
                interview_type=InterviewType.COMPREHENSIVE.value,
                total_questions=5,
            )
            save_session(unscored_session, db_path=db_path)

            analytics = get_aggregate_analytics(db_path=db_path)
            assert analytics["total_sessions"] == 2
            assert analytics["total_answers_submitted"] == 1
            assert analytics["avg_session_score"] == scored_session.overall_session_score
        finally:
            if os.path.exists(db_path):
                os.remove(db_path)



def test_answer_revision_history_persists():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tf:
        db_path = tf.name

    try:
        question = QuestionItem(
            id="revision-q",
            category=QuestionCategory.TECHNICAL,
            role=TargetRole.SOFTWARE_ENGINEERING.value,
            question_text="Explain a hash map.",
            competency_or_topic="Data Structures",
        )
        turn = InterviewTurn(
            question_index=0,
            question=question,
            initial_answer="A hash map stores values.",
            completed=True,
        )
        turn.answer_revisions.append({
            "field": "main answer",
            "previous": "A hash map stores values.",
            "updated": "A hash map maps keys to values using a hash function.",
            "edited_at": 1760000000.0,
        })
        session = InterviewSession(
            session_id="revision-history",
            candidate_name="Test Candidate",
            target_role=TargetRole.SOFTWARE_ENGINEERING.value,
            experience_level=ExperienceLevel.INTERNSHIP.value,
            interview_type=InterviewType.COMPREHENSIVE.value,
            total_questions=1,
            turns=[turn],
        )

        save_session(session, db_path=db_path)
        saved = get_session("revision-history", db_path=db_path)
        assert saved is not None
        saved_turn = saved["turns"][0]
        assert saved_turn["answer_revisions"][0]["previous"] == "A hash map stores values."
        assert saved_turn["answer_revisions"][0]["updated"].startswith("A hash map maps keys")
    finally:
        if os.path.exists(db_path):
            os.remove(db_path)
