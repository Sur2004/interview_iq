"""Unit tests for speech transcription failure and success paths."""
from types import SimpleNamespace

import pytest
import requests

from backend import speech


def response(status_code=200, payload=None, text=""):
    return SimpleNamespace(
        status_code=status_code,
        _payload=payload or {},
        text=text,
        json=lambda: payload or {},
    )


def test_empty_audio_is_rejected():
    with pytest.raises(ValueError, match="Record an answer"):
        speech.transcribe_audio(b"", "audio/wav", "groq", "key")


def test_unsupported_or_unconfigured_provider_is_rejected():
    with pytest.raises(ValueError, match="requires a configured"):
        speech.transcribe_audio(b"audio", "audio/wav", "heuristic", None)


def test_groq_transcription_success(monkeypatch):
    monkeypatch.setattr(speech.requests, "post", lambda *a, **k: response(payload={"text": "A clear answer"}))
    assert speech.transcribe_audio(b"audio", "audio/webm", "groq", "test-key") == "A clear answer"


def test_groq_http_error_is_actionable(monkeypatch):
    monkeypatch.setattr(speech.requests, "post", lambda *a, **k: response(status_code=429))
    with pytest.raises(RuntimeError, match="Groq HTTP 429"):
        speech.transcribe_audio(b"audio", "audio/webm", "groq", "test-key")


def test_groq_network_failure_suggests_text_fallback(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.ConnectionError("offline")
    monkeypatch.setattr(speech.requests, "post", fail)
    with pytest.raises(RuntimeError, match="typed-answer option"):
        speech.transcribe_audio(b"audio", "audio/webm", "groq", "test-key")


def test_gemini_transcription_success(monkeypatch):
    payload = {"candidates": [{"content": {"parts": [{"text": "A Gemini transcript"}]}}]}
    monkeypatch.setattr(speech.requests, "post", lambda *a, **k: response(payload=payload))
    assert speech.transcribe_audio(b"audio", "audio/webm", "gemini", "test-key", "test-model") == "A Gemini transcript"


def test_gemini_http_error_is_actionable(monkeypatch):
    monkeypatch.setattr(speech.requests, "post", lambda *a, **k: response(status_code=403))
    with pytest.raises(RuntimeError, match="Gemini HTTP 403"):
        speech.transcribe_audio(b"audio", "audio/webm", "gemini", "test-key", "test-model")


def test_gemini_network_failure_suggests_text_fallback(monkeypatch):
    def fail(*args, **kwargs):
        raise requests.Timeout("timed out")
    monkeypatch.setattr(speech.requests, "post", fail)
    with pytest.raises(RuntimeError, match="typed-answer option"):
        speech.transcribe_audio(b"audio", "audio/webm", "gemini", "test-key", "test-model")


def test_empty_transcript_is_rejected(monkeypatch):
    monkeypatch.setattr(speech.requests, "post", lambda *a, **k: response(payload={"text": "  "}))
    with pytest.raises(ValueError, match="No clear speech"):
        speech.transcribe_audio(b"audio", "audio/webm", "groq", "test-key")
