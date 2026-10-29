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
