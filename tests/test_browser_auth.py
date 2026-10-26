"""Regression tests for browser-local persistence and OTP helpers."""
import pytest

from backend.auth import normalize_email, otp_digest, send_email_otp
from backend.browser_store import analytics_from_sessions, session_from_dict
from backend.models import InterviewSession, InterviewTurn, QuestionItem, QuestionCategory, TargetRole
from backend.evaluator import evaluate_heuristically


def test_email_normalization_and_otp_digest_are_stable():
    assert normalize_email("  TEST@Example.com ") == "test@example.com"
    assert otp_digest("TEST@example.com", "123456", "secret") == otp_digest(" test@example.com ", "123456", "secret")
    assert otp_digest("test@example.com", "123456", "secret") != otp_digest("test@example.com", "654321", "secret")


def test_otp_fails_closed_without_smtp_configuration(monkeypatch):
    for key in ("SMTP_HOST", "SMTP_USER", "SMTP_PASSWORD", "SMTP_FROM"):
        monkeypatch.delenv(key, raising=False)
    with pytest.raises(RuntimeError, match="Email OTP is not configured"):
        send_email_otp("student@example.com", "123456")


def test_browser_session_round_trip_and_chart_analytics():
    question = QuestionItem(
        id="browser-q1",
        category=QuestionCategory.TECHNICAL,
        role=TargetRole.SOFTWARE_ENGINEERING.value,
        question_text="Explain a hash map.",
        competency_or_topic="Data structures",
    )
    turn = InterviewTurn(
        question_index=0,
        question=question,
        initial_answer="A hash map stores key-value pairs.",
        followup_answer="It resolves collisions with chaining.",
        completed=True,
    )
    turn.turn_evaluation = evaluate_heuristically(question, turn.initial_answer, turn.followup_answer)
    session = InterviewSession(
        session_id="browser-session-1",
        candidate_name="Test Candidate",
        target_role=TargetRole.SOFTWARE_ENGINEERING.value,
        experience_level="Undergraduate Internship",
        interview_type="Comprehensive Mixed",
        total_questions=1,
        turns=[turn],
        is_finished=True,
        overall_session_score=turn.turn_evaluation.overall_score,
    )

    restored = session_from_dict(session.to_dict())
    assert restored.session_id == session.session_id
    assert restored.turns[0].question.question_text == "Explain a hash map."
    assert restored.turns[0].turn_evaluation is not None
    assert restored.turns[0].turn_evaluation.rubric_scores["relevance"].score >= 1

    analytics = analytics_from_sessions([session.to_dict()])
    assert analytics["total_sessions"] == 1
    assert analytics["total_answers_submitted"] == 1
    assert analytics["avg_session_score"] == session.overall_session_score
    assert analytics["category_breakdown"]["technical"]["count"] == 1


def test_browser_analytics_handles_empty_data():
    analytics = analytics_from_sessions([])
    assert analytics["total_sessions"] == 0
    assert analytics["avg_session_score"] == 0
    assert analytics["category_breakdown"] == {}
