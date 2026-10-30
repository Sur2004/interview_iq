"""Unit tests for speech transcription and provider connectivity."""
from unittest.mock import Mock, patch
import pytest
from backend.healthcheck import check_llm_connection
from backend.speech import transcribe_audio

def test_gemini_connection_reports_success_without_exposing_key():
    response = Mock(status_code=200)
    response.json.return_value = {"candidates": [{"content": {"parts": [{"text": "OK"}]}}]}
    with patch("backend.healthcheck.requests.post", return_value=response) as post:
        result = check_llm_connection("gemini", "test-secret", "gemini-3.8-flash")
    assert "connection successful" in result.lower()
    assert "test-secret" not in result
    assert post.call_args.kwargs["headers"]["x-goog-api-key"] == "test-secret"

def test_invalid_api_key_is_reported():
    response = Mock(status_code=401)
    with patch("backend.healthcheck.requests.post", return_value=response):
        with pytest.raises(RuntimeError, match="rejected the API key"):
            check_llm_connection("groq", "bad-key", "openai/gpt-oss-120b")

def test_openai_audio_is_sent_to_transcription_endpoint_and_returned_as_text():
    response = Mock(status_code=200)
    response.json.return_value = {"text": "I would use a database index to improve query performance."}
    with patch("backend.speech.requests.post", return_value=response) as post:
        transcript = transcribe_audio(b"fake-audio", "audio/wav", "openai", "test-secret")
    assert transcript.startswith("I would use a database index")
    assert post.call_args.args[0] == "https://api.openai.com/v1/audio/transcriptions"
    assert post.call_args.kwargs["data"]["model"] == "whisper-1"
    assert post.call_args.kwargs["files"]["file"][0] == "answer.wav"

def test_groq_audio_transcription_returns_text():
    response = Mock(status_code=200)
    response.json.return_value = {"text": "I would inspect the service logs and metrics first."}
    with patch("backend.speech.requests.post", return_value=response):
        transcript = transcribe_audio(b"fake-audio", "audio/webm", "groq", "test-secret")
    assert transcript.startswith("I would inspect the service logs")
