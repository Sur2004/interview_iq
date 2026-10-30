"""Small, safe live connectivity checks for configured LLM providers."""
from typing import Optional
import requests

def check_llm_connection(provider: str, api_key: Optional[str], model_name: Optional[str] = None) -> str:
    """Make a minimal authenticated request; never log or return the secret."""
    provider = (provider or "").strip().lower()
    if provider == "heuristic":
        return "Offline diagnostic engine is active; it does not require an API key."
    if provider not in {"gemini", "groq", "openai"}:
        raise ValueError("Unsupported AI provider.")
    if not api_key:
        raise ValueError(f"No API key is configured for {provider.upper()}.")
    try:
        if provider == "gemini":
            model = model_name or "gemini-3.8-flash"
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
                json={"contents": [{"parts": [{"text": "Reply with exactly: OK"}]}], "generationConfig": {"temperature": 0, "maxOutputTokens": 8}},
                timeout=20,
            )
            if response.status_code == 200 and response.json()["candidates"][0]["content"]["parts"][0]["text"].strip():
                return f"Gemini API connection successful ({model})."
        else:
            model = model_name or ("openai/gpt-oss-120b" if provider == "groq" else "gpt-4o-mini")
            base = "https://api.groq.com/openai/v1" if provider == "groq" else "https://api.openai.com/v1"
            response = requests.post(
                f"{base}/chat/completions",
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                json={"model": model, "messages": [{"role": "user", "content": "Reply with exactly: OK"}], "temperature": 0, "max_tokens": 8},
                timeout=20,
            )
            if response.status_code == 200 and response.json()["choices"][0]["message"]["content"].strip():
                return f"{provider.upper()} API connection successful ({model})."
    except requests.RequestException as exc:
        raise RuntimeError(f"Could not reach {provider.upper()}: check network connectivity.") from exc
    except (KeyError, IndexError, TypeError, ValueError):
        raise RuntimeError(f"{provider.upper()} responded, but the response format was unexpected.")
    if response.status_code in {401, 403}:
        raise RuntimeError(f"{provider.upper()} rejected the API key (HTTP {response.status_code}). Check the key and project permissions.")
    if response.status_code == 429:
        raise RuntimeError(f"{provider.upper()} rate limit or quota was reached (HTTP 429). Check usage and quota.")
    raise RuntimeError(f"{provider.upper()} API test failed (HTTP {response.status_code}). Check model access and provider settings.")
