"""Browser-local candidate identity helpers for InterviewIQ.

PINs are salted and PBKDF2-hashed before being written to localStorage.
This is convenience-level protection, not secure server-side authentication.
"""
from __future__ import annotations

import hashlib
import hmac
import secrets
import re
from typing import Mapping

_CANDIDATE_ID_RE = re.compile(r"^IQ-[A-F0-9]{8}$")
_PBKDF2_ROUNDS = 310_000


def generate_candidate_id(existing_profiles: Mapping[str, object]) -> str:
    """Return an unused, human-readable candidate ID."""
    for _ in range(100):
        candidate_id = f"IQ-{secrets.token_hex(4).upper()}"
        if candidate_id not in existing_profiles:
            return candidate_id
    raise RuntimeError("Could not allocate a unique candidate ID; please retry.")


def validate_candidate_id(candidate_id: str) -> bool:
    """Validate the public ID format."""
    return isinstance(candidate_id, str) and bool(_CANDIDATE_ID_RE.fullmatch(candidate_id.strip().upper()))


def hash_pin(pin: str, salt: str | None = None) -> tuple[str, str]:
    """Hash a PIN with a random salt using PBKDF2-HMAC-SHA256."""
    if not isinstance(pin, str) or not (pin.isdigit() and len(pin) == 6):
        raise ValueError("PIN must contain exactly 6 digits.")
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), bytes.fromhex(salt), _PBKDF2_ROUNDS).hex()
    return salt, digest


def verify_pin(pin: str, salt: str, expected_digest: str) -> bool:
    """Constant-time verification; malformed stored values fail closed."""
    if not isinstance(pin, str) or not (pin.isdigit() and len(pin) == 6):
        return False
    if not isinstance(salt, str) or not isinstance(expected_digest, str):
        return False
    try:
        _, actual = hash_pin(pin, salt)
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(actual, expected_digest)
