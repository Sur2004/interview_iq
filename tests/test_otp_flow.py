"""OTP delivery and UI regression tests.

The SMTP test uses a fake server: it verifies message construction and the TLS/login/send
sequence without sending real email. UI tests patch delivery and use a deterministic OTP.
"""
import smtplib
from pathlib import Path

from streamlit.testing.v1 import AppTest

import backend.auth as auth_module


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


class FakeSMTP:
    instances = []

    def __init__(self, host, port, timeout=0):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.did_starttls = False
        self.login_args = None
        self.message = None
        self.__class__.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def ehlo(self):
        return None

    def starttls(self):
        self.did_starttls = True

    def login(self, username, password):
        self.login_args = (username, password)

    def send_message(self, message):
        self.message = message


def _offline_auth_app():
    app = AppTest.from_file(str(APP_PATH), default_timeout=30)
    app.session_state["sb_provider"] = "Built-In Offline Engine"
    return app


def _send_code(app, email="student@example.com"):
    app.run()
    email_box = next(item for item in app.text_input if item.label == "Email address")
    email_box.set_value(email)
    send_button = next(item for item in app.button if item.label == "Send verification code")
    send_button.click().run()
    assert not app.exception
    assert any("Verification code sent" in item.value for item in app.success)
    return app


def test_send_email_otp_uses_tls_and_sends_code(monkeypatch):
    values = {
        "SMTP_HOST": "smtp.example.com",
        "SMTP_PORT": "587",
        "SMTP_USER": "smtp-user",
        "SMTP_PASSWORD": "smtp-password",
        "SMTP_FROM": "InterviewIQ <noreply@example.com>",
    }
    monkeypatch.setattr(auth_module, "get_setting", lambda key, default=None: values.get(key, default))
    monkeypatch.setattr(smtplib, "SMTP", FakeSMTP)
    FakeSMTP.instances.clear()

    auth_module.send_email_otp("  Student@Example.com ", "012345")

    smtp = FakeSMTP.instances[-1]
    assert (smtp.host, smtp.port, smtp.timeout) == ("smtp.example.com", 587, 15)
    assert smtp.did_starttls
    assert smtp.login_args == ("smtp-user", "smtp-password")
    assert smtp.message["To"] == "student@example.com"
    assert smtp.message["From"] == "InterviewIQ <noreply@example.com>"
    assert "012345" in smtp.message.get_content()
    assert "5 minutes" in smtp.message.get_content()


def test_app_opens_in_guest_mode_without_sign_in():
    app = _offline_auth_app()
    app.run()

    assert not app.exception
    labels = [item.label for item in app.text_input]
    button_labels = [item.label for item in app.button]
    assert "Email address" not in labels
    assert "6-digit verification code" not in labels
    assert "Send verification code" not in button_labels
    assert "Verify and continue" not in button_labels
    assert app.session_state.get("authenticated_email") is None
