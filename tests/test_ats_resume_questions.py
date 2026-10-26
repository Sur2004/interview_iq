"""Tests for transparent ATS checklist scoring and resume-based interview prompts."""
from backend.career_review import calculate_ats_score, generate_resume_based_questions


def test_ats_score_has_explained_100_point_breakdown():
    resume = """
    Jane Example
    jane@example.com | +1 555 555 1212

    PROFESSIONAL SUMMARY
    Software engineering graduate focused on backend systems.

    SKILLS
    Python, Java, SQL, data structures, algorithms, Git, testing, API development.

    EDUCATION
    Bachelor of Technology in Computer Science.

    PROJECTS
    Developed a Flask API and tested endpoints. Built a dashboard for 1,200 records,
    improving report generation time by 25%.
    """
    result = calculate_ats_score(resume, "Software Engineering")
    assert 0 <= result["score"] <= 100
    assert sum(item["max_score"] for item in result["breakdown"]) == 100
    assert result["matched_keywords"]
    assert result["suggestions"]
    assert "not an employer ATS score" in result["method"]


def test_ats_score_handles_empty_resume_without_fabricating_score():
    result = calculate_ats_score("", "Data Analyst")
    assert result["score"] is None
    assert result["breakdown"] == []
    assert result["suggestions"]


def test_resume_questions_reference_resume_claims_and_include_followups():
    resume = """
    SKILLS
    Python, SQL, Power BI and pandas

    PROJECTS
    Developed a sales forecasting model using Python and pandas.
    Improved prediction accuracy by 18% after feature engineering.
    """
    questions = generate_resume_based_questions(resume, "Data Analyst")
    assert 1 <= len(questions) <= 8
    assert any("Developed a sales forecasting model" in question for question in questions)
    assert any("18%" in question for question in questions)
    assert any("Data Analyst" in question for question in questions)
