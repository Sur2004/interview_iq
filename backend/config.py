"""
Configuration and Secret Management for InterviewIQ.
Supports both local (.env / .streamlit/secrets.toml) and deployed (Streamlit Community Cloud st.secrets)
environments with zero code changes.
"""

import os
from typing import Optional, Dict, Any
import streamlit as st

# Load local .env if available
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """
    Retrieves a configuration value or secret.
    Order of precedence:
    1. Streamlit Community Cloud secrets (`st.secrets[key]`)
    2. Operating system environment variable (`os.environ[key]`, loaded from .env)
    3. Default fallback value
    """
    # Check Streamlit secrets first (works in deployed cloud and local secrets.toml)
    try:
        if hasattr(st, "secrets") and key in st.secrets:
            val = str(st.secrets[key]).strip()
            if val and not val.startswith("replace_with_"):
                return val
    except Exception:
        pass

    # Fallback to os.environ (loaded from .env via python-dotenv)
    env_val = os.environ.get(key)
    if env_val is not None:
        val = env_val.strip()
        if val and not val.startswith("replace_with_"):
            return val

    return default


def get_llm_config() -> Dict[str, Optional[str]]:
    """Returns current active LLM configuration and detects active provider."""
    explicit_provider = get_setting("LLM_PROVIDER")
    groq_key = get_setting("GROQ_API_KEY")
    gemini_key = get_setting("GEMINI_API_KEY")
    openai_key = get_setting("OPENAI_API_KEY")
    model_name = get_setting("MODEL_NAME")

    if explicit_provider:
        provider = explicit_provider.lower()
    elif groq_key:
        provider = "groq"
    elif gemini_key:
        provider = "gemini"
    elif openai_key:
        provider = "openai"
    else:
        provider = "heuristic"

    # Default model names per provider
    if provider == "groq" and model_name == "llama-3.3-70b-versatile":
        # Groq retired Llama 3.3 70B on 2026-08-16; migrate stale deployment secrets.
        model_name = "openai/gpt-oss-120b"
    elif provider == "groq" and not model_name:
        model_name = "openai/gpt-oss-120b"
    elif provider == "gemini" and not model_name:
        model_name = "gemini-3.8-flash"
    elif provider == "openai" and not model_name:
        model_name = "gpt-4o-mini"
    elif provider == "heuristic" and not model_name:
        model_name = "built-in-diagnostic-engine"

    return {
        "provider": provider,
        "groq_api_key": groq_key,
        "gemini_api_key": gemini_key,
        "openai_api_key": openai_key,
        "model_name": model_name,
    }


def validate_secrets() -> Dict[str, Any]:
    """Validates secrets and returns helpful startup status information without printing raw secrets."""
    config = get_llm_config()
    provider = config["provider"]

    if provider == "groq" and not config["groq_api_key"]:
        return {
            "status": "warning",
            "message": "GROQ_API_KEY is not configured or using placeholder. Running in Built-In Diagnostic Mode.",
            "provider": "heuristic",
        }
    elif provider == "gemini" and not config["gemini_api_key"]:
        return {
            "status": "warning",
            "message": "GEMINI_API_KEY is not configured. Running in Built-In Diagnostic Mode.",
            "provider": "heuristic",
        }
    elif provider == "openai" and not config["openai_api_key"]:
        return {
            "status": "warning",
            "message": "OPENAI_API_KEY is not configured. Running in Built-In Diagnostic Mode.",
            "provider": "heuristic",
        }

    return {
        "status": "ready",
        "message": f"AI Engine active using hosted provider: {provider.upper()} ({config['model_name']})",
        "provider": provider,
    }
