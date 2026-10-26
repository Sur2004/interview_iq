"""Browser-only session serialization and chart-ready analytics."""
from __future__ import annotations

from typing import Any, Dict, List
from .models import (
    InterviewSession, InterviewTurn, QuestionItem, QuestionCategory,
    EvaluationResult, RubricScore,
)


def _evaluation_from_dict(data: dict | None):
    if not data:
        return None
    scores = {
        key: RubricScore(
            criterion=value.get("criterion", key),
            display_name=value.get("display_name", key.title()),
            score=float(value.get("score", 0)),
            feedback=value.get("feedback", ""),
            strengths=value.get("strengths", []) or [],
            areas_for_growth=value.get("areas_for_growth", []) or [],
        )
        for key, value in (data.get("rubric_scores") or {}).items()
    }
    return EvaluationResult(
        overall_score=float(data.get("overall_score", 0)),
        rubric_scores=scores,
        key_strengths=data.get("key_strengths", []) or [],
        actionable_improvements=data.get("actionable_improvements", []) or [],
        stronger_answer_outline=data.get("stronger_answer_outline", ""),
        suggested_followup_question=data.get("suggested_followup_question"),
        technical_breakdown=data.get("technical_breakdown"),
        architecture_diagram_mermaid=data.get("architecture_diagram_mermaid"),
        disclaimer=data.get("disclaimer", ""),
        ethical_note=data.get("ethical_note", ""),
    )


def session_from_dict(data: dict) -> InterviewSession:
    turns = []
    for item in data.get("turns", []) or []:
        qdata = item.get("question") or {}
        category_value = qdata.get("category", "technical")
        try:
            category = QuestionCategory(category_value)
        except ValueError:
            category = QuestionCategory.TECHNICAL
        question = QuestionItem(
            id=qdata.get("id", f"browser-q-{item.get('question_index', 0)}"),
            category=category,
            role=qdata.get("role", data.get("target_role", "")),
            question_text=qdata.get("question_text", ""),
            competency_or_topic=qdata.get("competency_or_topic", ""),
            rubric_hints=qdata.get("rubric_hints", []) or [],
            default_followup=qdata.get("default_followup", ""),
        )
        turns.append(InterviewTurn(
            question_index=int(item.get("question_index", len(turns))),
            question=question,
            initial_answer=item.get("initial_answer", ""),
            initial_evaluation=_evaluation_from_dict(item.get("initial_evaluation")),
            followup_question=item.get("followup_question", ""),
            followup_answer=item.get("followup_answer", ""),
            turn_evaluation=_evaluation_from_dict(item.get("turn_evaluation")),
            completed=bool(item.get("completed", False)),
            timestamp=float(item.get("timestamp", 0) or 0),
            answer_revisions=item.get("answer_revisions", []) or [],
        ))
    return InterviewSession(
        session_id=str(data.get("session_id", "")),
        candidate_name=data.get("candidate_name", "Candidate"),
        target_role=data.get("target_role", ""),
        experience_level=data.get("experience_level", ""),
        interview_type=data.get("interview_type", ""),
        total_questions=int(data.get("total_questions", len(turns))),
        candidate_context=data.get("candidate_context", ""),
        turns=turns,
        current_turn_index=int(data.get("current_turn_index", 0)),
        in_followup=bool(data.get("in_followup", False)),
        is_finished=bool(data.get("is_finished", False)),
        created_at=float(data.get("created_at", 0) or 0),
        completed_at=data.get("completed_at"),
        overall_session_score=data.get("overall_session_score"),
    )


def session_summaries(data: dict, email: str) -> List[Dict[str, Any]]:
    rows = data.get("sessions", {}).get(email, [])
    return sorted(rows, key=lambda row: float(row.get("created_at", 0) or 0))


def analytics_from_sessions(rows: list[dict]) -> dict:
    scored_sessions = [r for r in rows if r.get("overall_session_score") is not None]
    scores = [float(r["overall_session_score"]) for r in scored_sessions]
    turns = [t for r in rows for t in (r.get("turns", []) or [])]
    scored_turns = [t for t in turns if (t.get("turn_evaluation") or t.get("initial_evaluation"))]
    criterion_values = {key: [] for key in ("relevance", "structure", "evidence", "clarity")}
    category_values: dict[str, list[float]] = {}
    for turn in scored_turns:
        evaluation = turn.get("turn_evaluation") or turn.get("initial_evaluation") or {}
        rubric = evaluation.get("rubric_scores") or {}
        for key in criterion_values:
            if key in rubric:
                try:
                    criterion_values[key].append(float(rubric[key].get("score", 0)))
                except (TypeError, ValueError):
                    pass
        q = turn.get("question") or {}
        category = q.get("category", "unknown")
        try:
            category_values.setdefault(category, []).append(float(evaluation.get("overall_score", 0)))
        except (TypeError, ValueError):
            pass
    return {
        "total_sessions": len(rows),
        "total_answers_submitted": len([t for t in turns if t.get("initial_answer")]),
        "avg_session_score": round(sum(scores) / len(scores), 2) if scores else 0,
        "avg_relevance": round(sum(criterion_values["relevance"]) / len(criterion_values["relevance"]), 2) if criterion_values["relevance"] else 0,
        "avg_structure": round(sum(criterion_values["structure"]) / len(criterion_values["structure"]), 2) if criterion_values["structure"] else 0,
        "avg_evidence": round(sum(criterion_values["evidence"]) / len(criterion_values["evidence"]), 2) if criterion_values["evidence"] else 0,
        "avg_clarity": round(sum(criterion_values["clarity"]) / len(criterion_values["clarity"]), 2) if criterion_values["clarity"] else 0,
        "category_breakdown": {
            key: {"avg": round(sum(values) / len(values), 2), "count": len(values)}
            for key, values in category_values.items() if values
        },
    }
