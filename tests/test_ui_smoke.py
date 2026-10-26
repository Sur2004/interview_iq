"""Streamlit UI smoke tests for common user journeys.

These tests use the offline provider and do not make external API calls.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def build_offline_app() -> AppTest:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30)
    app.session_state["sb_provider"] = "Built-In Offline Engine"
    return app


def test_main_app_renders_without_streamlit_exceptions():
    app = build_offline_app().run()

    assert not app.exception
    assert any("InterviewIQ" in item.value for item in app.markdown)
    assert any("Start Interview Round" in item.label for item in app.button)


def test_user_can_change_role_and_start_an_offline_round():
    app = build_offline_app().run()

    role_selector = next(item for item in app.selectbox if "Target Role" in item.label)
    role_selector.select("Data Science & Machine Learning").run()

    assert not app.exception

    start_button = next(item for item in app.button if "Start Interview Round" in item.label)
    start_button.click().run()

    assert not app.exception
    session = app.session_state["session"]
    assert session is not None
    assert session.target_role == "Data Science & Machine Learning"
    assert len(session.turns) == session.total_questions
    assert 5 <= session.total_questions <= 8


def test_provider_panel_explains_offline_mode():
    app = build_offline_app().run()

    assert not app.exception
    assert any(
        "Offline diagnostic mode is selected" in item.value
        for item in app.info
    )
