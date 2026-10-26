"""Speech transcription for voice-first interview answers.

Uses a configured Gemini or Groq API key. Audio is sent to that selected provider
for transcription; no local speech model or shared API key is bundled.
"""
import base64
import io
from typing import Optional

import requests
from requests.exceptions import RequestException


def transcribe_audio(audio_bytes: bytes, mime_type: str, provider: str, api_key: Optional[str], model_name: Optional[str] = None) -> str:
    if not audio_bytes:
        raise ValueError("Record an answer before submitting.")
    if not api_key or provider not in {"gemini", "groq"}:
        raise ValueError("Voice transcription requires a configured Gemini or Groq API key.")
    mime_type = mime_type or "audio/wav"

    if provider == "groq":
        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {api_key}"},
                files={"file": ("answer.webm", io.BytesIO(audio_bytes), mime_type)},
                data={"model": "whisper-large-v3-turbo", "response_format": "json"},
                timeout=90,
            )
        except RequestException as exc:
            raise RuntimeError(
                "Could not reach Groq for speech transcription. Check your internet connection or use the typed-answer option."
            ) from exc
        if response.status_code != 200:
            raise RuntimeError(f"Speech transcription failed (Groq HTTP {response.status_code}). Check your key, quota, and audio format.")
        transcript = response.json().get("text", "").strip()
    else:
        model = model_name or "gemini-3.8-flash"
        payload = {
            "contents": [{
                "parts": [
                    {"text": "Transcribe the spoken audio accurately and verbatim. Return only the transcript, without commentary. If no intelligible speech is present, return an empty string."},
                    {"inline_data": {"mime_type": mime_type, "data": base64.b64encode(audio_bytes).decode("ascii")}},
                ]
            }],
            "generationConfig": {"temperature": 0},
        }
        try:
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json=payload,
                timeout=90,
            )
        except RequestException as exc:
            raise RuntimeError(
                "Could not reach Gemini for speech transcription. Check your internet connection or use the typed-answer option."
            ) from exc
        if response.status_code != 200:
            raise RuntimeError(f"Speech transcription failed (Gemini HTTP {response.status_code}). Check your key, model access, quota, and audio format.")
        parts = response.json().get("candidates", [{}])[0].get("content", {}).get("parts", [])
        transcript = " ".join(part.get("text", "") for part in parts if part.get("text")).strip()

    if not transcript:
        raise ValueError("No clear speech was detected. Please record your answer again.")
    return transcript
