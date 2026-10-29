"""Streamlit UI smoke tests for common user journeys.

These tests use the offline provider and do not make external API calls.
"""
from pathlib import Path

from streamlit.testing.v1 import AppTest


APP_PATH = Path(__file__).resolve().parents[1] / "app.py"


def build_offline_app(section: str = "mock_interview") -> AppTest:
    app = AppTest.from_file(str(APP_PATH), default_timeout=30)
    app.session_state["sb_provider"] = "Built-In Offline Engine"
    app.session_state["workspace_navigation"] = section
    app.session_state["authenticated_email"] = "offline-test@example.com"
    app.session_state["authenticated_candidate_id"] = "offline-test@example.com"
    app.session_state["browser_data"] = {
        "profiles": {"offline-test@example.com": {"name": "Offline Test"}},
        "sessions": {"offline-test@example.com": []},
    }
    app.session_state["browser_data_loaded"] = True
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
    type_selector.select("HR & Behavioral (STAR Framework)").run()

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
    assert session.interview_type == "HR & Behavioral (STAR Framework)"
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

    submit = next(item for item in app.button if "Transcribe & Submit Answer" in item.label)
    submit.click().run()

    assert not app.exception
    assert any("typed-answer option above" in item.value.lower() for item in app.warning)
    assert app.session_state["session"].current_turn_index == initial_index
    assert not app.session_state["session"].turns[initial_index].initial_answer


def test_interview_round_requires_audio_instead_of_typed_answers():
    app = start_one_question_offline_app()

    assert not app.exception
    assert any("Record your answer" in item.label for item in app.audio_input)
    assert any(item.label == "Or type your answer" for item in app.text_area)
    assert any("Submit Typed Answer" in item.label for item in app.button)
    assert any("Transcribe & Submit Answer" in item.label for item in app.button)


def test_followup_round_uses_audio_input_and_allows_skip():
    app = start_one_question_offline_app()
    session = app.session_state["session"]
    turn = session.turns[session.current_turn_index]
    turn.initial_answer = "A hash map stores key-value pairs and offers average constant-time lookup."
    from backend.evaluator import evaluate_heuristically
    turn.initial_evaluation = evaluate_heuristically(turn.question, turn.initial_answer)
    session.in_followup = True
    app.session_state["session"] = session
    app.run()

    assert not app.exception
    assert any("Record your follow-up answer" in item.label for item in app.audio_input)
    assert any(item.label == "Or type your follow-up answer" for item in app.text_area)
    assert any("Submit Typed Follow-Up & Score Turn" in item.label for item in app.button)
    skip = next(item for item in app.button if "Skip Follow-Up" in item.label)
    skip.click().run()
    assert not app.exception
    assert app.session_state["session"].turns[0].completed


def test_blank_custom_challenge_topic_is_rejected():
    app = build_offline_app("technical_challenge").run()

    topic = next(item for item in app.text_input if item.label == "Topic or technology")
    topic.set_value("")
    generate = next(item for item in app.button if item.label == "Generate challenge")
    generate.click().run()

    assert not app.exception
    assert any("enter a topic" in item.value.lower() for item in app.warning)
    assert "current_dyn_q" not in app.session_state


def test_custom_challenge_topic_generates_offline_question():
    app = build_offline_app("technical_challenge").run()

    topic = next(item for item in app.text_input if item.label == "Topic or technology")
    topic.set_value("SQL indexing and query plans")
    generate = next(item for item in app.button if item.label == "Generate challenge")
    generate.click().run()

    assert not app.exception
    assert "current_dyn_q" in app.session_state
    question = app.session_state["current_dyn_q"]
    assert question.question_text.strip()
    assert question.competency_or_topic



def test_typed_primary_answer_is_evaluated_offline():
    app = start_one_question_offline_app()
    answer = next(item for item in app.text_area if item.label == "Or type your answer")
    answer.set_value("A hash map stores key-value pairs and usually supports average constant-time lookup.")
    submit = next(item for item in app.button if item.label == "Submit Typed Answer")
    submit.click().run()

    assert not app.exception
    session = app.session_state["session"]
    assert session.in_followup
    assert session.turns[session.current_turn_index].initial_answer.startswith("A hash map")


def test_typed_followup_answer_is_evaluated_offline():
    app = start_one_question_offline_app()
    session = app.session_state["session"]
    turn = session.turns[session.current_turn_index]
    turn.initial_answer = "A hash map stores key-value pairs and usually supports average constant-time lookup."
    from backend.evaluator import evaluate_heuristically
    turn.initial_evaluation = evaluate_heuristically(turn.question, turn.initial_answer)
    session.in_followup = True
    app.session_state["session"] = session
    app.run()

    answer = next(item for item in app.text_area if item.label == "Or type your follow-up answer")
    answer.set_value("I would handle collisions with chaining and measure load factor.")
    submit = next(item for item in app.button if item.label == "Submit Typed Follow-Up & Score Turn")
    submit.click().run()

    assert not app.exception
    session = app.session_state["session"]
    assert session.turns[0].completed
    assert session.turns[0].followup_answer.startswith("I would handle collisions")


def test_all_sidebar_sections_open_without_exceptions():
    """Regression test: every navigation destination must render its workspace."""
    expected = {
        "technical_challenge": "Build and Practice a Technical Challenge",
        "question_bank": "Comprehensive Interview Question Bank",
        "system_design": "System Design & Engineering Playbooks",
        "star_builder": "Interactive STAR Story Builder",
        "spot_the_flaw": "Spot the Interview Flaw",
        "progress": "Practice history & performance",
        "export_report": "Export Practice Report",
        "rubric_guide": "Transparent Rubric & Ethical Guardrails",
        "resume_review": "Resume & Project Review",
    }

    for section, heading in expected.items():
        app = build_offline_app(section).run()
        assert not app.exception, f"Section {section!r} raised: {app.exception}"
        rendered_text = "\n".join(
            [item.value for item in app.markdown]
            + [item.value for item in app.header]
            + [item.value for item in app.subheader]
        )
        assert heading in rendered_text, f"Section {section!r} did not render its heading"


def test_user_can_navigate_to_resume_and_project_review():
    app = build_offline_app().run()
    navigation = next(item for item in app.selectbox if item.label == "Open a section")
    navigation.select("resume_review").run()

    assert not app.exception
    assert app.session_state["workspace_navigation"] == "resume_review"
    assert any(item.value == "Resume & Project Review" for item in app.header)
