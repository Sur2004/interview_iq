"""Focused interview tracks remain compatible with the shared scoring pipeline."""
import pytest

from backend.models import InterviewType, TargetRole
from backend.question_bank import build_interview_plan


@pytest.mark.parametrize(
    "track",
    [
        InterviewType.BEHAVIORAL.value,
        InterviewType.MANAGERIAL.value,
        InterviewType.SITUATIONAL.value,
        InterviewType.COMMUNICATION.value,
    ],
)
def test_focused_interview_tracks_generate_valid_question_plans(track):
    questions = build_interview_plan(
        target_role=TargetRole.SOFTWARE_ENGINEERING.value,
        experience_level="Graduate / Entry-Level (0-1 yrs)",
        interview_type=track,
        num_questions=6,
    )
    assert len(questions) == 6
    assert all(q.question_text.strip() for q in questions)
    assert all(q.default_followup.strip() for q in questions)
    assert len({q.id for q in questions}) == len(questions)
