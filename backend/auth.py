"""Passwordless email OTP authentication for InterviewIQ.

This module deliberately has no user database. Verified identity is scoped to the
current Streamlit session; user profile and practice data are stored in browser
localStorage by the browser-store component.
"""
import hashlib
import os
import smtplib
from email.message import EmailMessage


def normalize_email(email: str) -> str:
    return (email or "").strip().lower()


def otp_digest(email: str, code: str, secret: str) -> str:
    payload = f"{normalize_email(email)}:{code}:{secret}".encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def send_email_otp(email: str, code: str) -> None:
    """Send a one-time sign-in code; fail closed when SMTP is not configured."""
    host = os.getenv("SMTP_HOST", "").strip()
    username = os.getenv("SMTP_USER", "").strip()
    password = os.getenv("SMTP_PASSWORD", "")
    sender = os.getenv("SMTP_FROM", username).strip()
    port = int(os.getenv("SMTP_PORT", "587"))
    if not all((host, username, password, sender)):
        raise RuntimeError(
            "Email OTP is not configured. Set SMTP_HOST, SMTP_PORT, SMTP_USER, "
            "SMTP_PASSWORD, and SMTP_FROM in your deployment secrets."
        )
    message = EmailMessage()
    message["Subject"] = "Your InterviewIQ sign-in code"
    message["From"] = sender
    message["To"] = normalize_email(email)
    message.set_content(
        f"Your InterviewIQ verification code is {code}. It expires in 5 minutes. "
        "If you did not request this code, you can ignore this email."
    )
    with smtplib.SMTP(host, port, timeout=15) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(username, password)
        server.send_message(message)
