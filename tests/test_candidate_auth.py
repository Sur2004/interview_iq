"""Tests for candidate ID and PIN helpers."""
import pytest

from backend.candidate_auth import (
    generate_candidate_id,
    hash_pin,
    validate_candidate_id,
    verify_pin,
)


def test_candidate_id_is_valid_and_unique_against_existing_profiles():
    existing = {"IQ-AAAAAAAA": {"name": "Existing"}}
    first = generate_candidate_id(existing)
    assert validate_candidate_id(first)
    assert first not in existing
    existing[first] = {}
    second = generate_candidate_id(existing)
    assert validate_candidate_id(second)
    assert second != first


@pytest.mark.parametrize("pin", ["", "123", "1234567", "12a456", " 12345"])
def test_hash_pin_rejects_invalid_pin(pin):
    with pytest.raises(ValueError):
        hash_pin(pin)


def test_pin_hash_is_salted_and_verifies_only_correct_pin():
    salt, digest = hash_pin("042817")
    other_salt, other_digest = hash_pin("042817")
    assert salt != other_salt
    assert digest != other_digest
    assert verify_pin("042817", salt, digest)
    assert not verify_pin("042818", salt, digest)
    assert not verify_pin("bad", salt, digest)


def test_candidate_id_validation_is_case_insensitive_and_strict():
    assert validate_candidate_id("iq-a1b2c3d4")
    assert not validate_candidate_id("IQ-123")
    assert not validate_candidate_id("IQ-ABCDEFGH!")


def test_session_history_is_namespaced_by_candidate_id():
    from backend.browser_store import session_summaries

    browser_data = {
        "sessions": {
            "IQ-AAAAAAAA": [{"session_id": "session-a", "created_at": 1}],
            "IQ-BBBBBBBB": [{"session_id": "session-b", "created_at": 2}],
        }
    }
    assert [row["session_id"] for row in session_summaries(browser_data, "IQ-AAAAAAAA")] == ["session-a"]
    assert [row["session_id"] for row in session_summaries(browser_data, "IQ-BBBBBBBB")] == ["session-b"]
    assert session_summaries(browser_data, "IQ-CCCCCCCC") == []


def test_gibberish_answer_is_rejected_before_scoring():
    from backend.evaluator import validate_answer_relevance
    from backend.models import QuestionCategory, QuestionItem

    question = QuestionItem(
        id="q-test",
        category=QuestionCategory.TECHNICAL,
        role="Software Engineering",
        question_text="Explain how a hash map works and its time complexity.",
        competency_or_topic="hash map complexity",
    )
    with pytest.raises(ValueError, match="gibberish|random text"):
        validate_answer_relevance(question, "Hheiskkdjdhd this is random keyboard mash text.")


def test_meaningful_technical_answer_passes_gibberish_gate():
    from backend.evaluator import validate_answer_relevance
    from backend.models import QuestionCategory, QuestionItem

    question = QuestionItem(
        id="q-test",
        category=QuestionCategory.TECHNICAL,
        role="Software Engineering",
        question_text="Explain how a hash map works and its time complexity.",
        competency_or_topic="hash map complexity",
    )
    validate_answer_relevance(
        question,
        "A hash map stores key value pairs and uses a hash function to find the bucket. "
        "Collisions can be handled with chaining, and average lookup time is constant.",
    )


def test_legitimate_synchronization_answer_is_not_mistaken_for_gibberish():
    from backend.evaluator import validate_answer_relevance
    from backend.models import QuestionCategory, QuestionItem

    question = QuestionItem(
        id="q-sync",
        category=QuestionCategory.TECHNICAL,
        role="Software Engineering",
        question_text="Explain synchronization in concurrent programming.",
        competency_or_topic="synchronization threads shared memory",
    )
    validate_answer_relevance(
        question,
        "Synchronization prevents race conditions when multiple threads access shared memory. "
        "A lock can protect critical sections and make updates predictable.",
    )


def test_short_repeated_character_spam_is_detected():
    from backend.evaluator import _suspicious_gibberish_tokens

    assert _suspicious_gibberish_tokens(["aaaaaaa"])
