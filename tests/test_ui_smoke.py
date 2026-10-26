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
    role_selector.select("Cybersecurity & Information Security").run()

    experience_selector = next(item for item in app.selectbox if "Experience Level" in item.label)
    experience_selector.select("Graduate / Entry-Level (0-1 yrs)").run()

    type_selector = next(item for item in app.selectbox if "Interview Type" in item.label)
    type_selector.select("Behavioral Focus (STAR Framework)").run()

    question_slider = next(item for item in app.slider if "Questions in Round" in item.label)
    question_slider.set_value(8).run()

    assert not app.exception

    start_button = next(item for item in app.button if "Start Interview Round" in item.label)
    start_button.click().run()

    assert not app.exception
    session = app.session_state["session"]
    assert session is not None
    assert session.target_role == "Cybersecurity & Information Security"
    assert session.experience_level == "Graduate / Entry-Level (0-1 yrs)"
    assert session.interview_type == "Behavioral Focus (STAR Framework)"
    assert len(session.turns) == session.total_questions == 8


def test_provider_panel_explains_offline_mode():
    app = build_offline_app().run()

    assert not app.exception
    assert any(
        "Offline diagnostic mode is selected" in item.value
        for item in app.info
    )



def start_one_question_offline_app():
    """Start a deterministic offline round and return its rendered AppTest."""
    app = build_offline_app().run()
    slider = next(item for item in app.slider if "Questions in Round" in item.label)
    slider.set_value(5).run()
    start = next(item for item in app.button if "Start Interview Round" in item.label)
    start.click().run()
    assert not app.exception
    return app


def test_empty_answer_is_rejected_without_advancing_the_turn():
    app = start_one_question_offline_app()
    session = app.session_state["session"]
    initial_index = session.current_turn_index

    submit = next(item for item in app.button if "Submit Answer" in item.label)
    submit.click().run()

    assert not app.exception
    assert any("type your response" in item.value.lower() for item in app.warning)
    assert app.session_state["session"].current_turn_index == initial_index
    assert not app.session_state["session"].turns[initial_index].initial_answer


def test_valid_answer_can_be_scored_and_followup_skipped():
    app = start_one_question_offline_app()

    answer = next(item for item in app.text_area if item.label == "Your Answer:")
    answer.set_value(
        "A hash map stores key-value pairs using a hash function. Average lookup is O(1), "
        "while collisions can use chaining or open addressing. The trade-off is memory use "
        "versus lookup speed, and resizing can be costly."
    ).run()

    submit = next(item for item in app.button if "Submit Answer" in item.label)
    submit.click().run()

    assert not app.exception
    session = app.session_state["session"]
    assert session.in_followup
    assert session.turns[session.current_turn_index].initial_evaluation is not None

    skip = next(item for item in app.button if "Skip Follow-Up" in item.label)
    skip.click().run()

    assert not app.exception
    session = app.session_state["session"]
    assert session.turns[0].completed
    assert session.turns[0].turn_evaluation is not None
    assert session.current_turn_index == 0

    # Completion is intentionally separate from navigation to the next question.
    next_question = next(item for item in app.button if "Next Question" in item.label)
    next_question.click().run()

    assert not app.exception
    assert app.session_state["session"].current_turn_index == 1
