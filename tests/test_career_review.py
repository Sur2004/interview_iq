"""Tests for bounded resume/repository intake and offline review fallback."""
import pytest

from backend.career_review import (
    _offline_review,
    parse_github_repo_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://github.com/Sur2004/interview_iq",
        "https://www.github.com/openai/openai",
        "https://github.com/owner/repo/tree/main/src",
        "https://github.com/owner/repo.git",
    ],
)
def test_parse_github_repo_url_accepts_github_repository_paths(url):
    owner, repo = parse_github_repo_url(url)
    assert owner
    assert repo


@pytest.mark.parametrize(
    "url",
    [
        "http://github.com/owner/repo",
        "https://example.com/owner/repo",
        "https://github.com/",
        "https://github.com/settings/profile",
        "https://github.com.evil.example/owner/repo",
    ],
)
def test_parse_github_repo_url_rejects_unsafe_or_invalid_urls(url):
    with pytest.raises(ValueError):
        parse_github_repo_url(url)


def test_offline_review_is_explicit_and_does_not_claim_llm_analysis():
    result = _offline_review(
        "Built a Flask project and improved response time by 25%.",
        {
            "name": "owner/project",
            "file_count": 2,
            "files": [
                {"path": "README.md", "content": "Project setup and tests with pytest."},
                {"path": "requirements.txt", "content": "requests"},
            ],
        },
        "Software Engineering",
    )
    assert result["provider"] == "Offline checklist (no LLM API key)"
    assert "not a semantic AI review" in result["summary"]
    assert result["priority_actions"]
    assert result["disclaimer"]
