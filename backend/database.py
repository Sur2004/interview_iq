"""
SQLite persistence module for InterviewIQ.
Stores sessions, turn-by-turn answers, rubric scores, and historical analytics locally.
"""

import sqlite3
import json
import os
import time
from typing import List, Dict, Optional, Any
from .models import InterviewSession, InterviewTurn, QuestionItem, QuestionCategory, EvaluationResult, RubricScore

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "interview_iq.db")


def get_connection(db_path: str = DEFAULT_DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str = DEFAULT_DB_PATH) -> None:
    """Initialize database schema with indexes for performance."""
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS sessions (
                    session_id TEXT PRIMARY KEY,
                    candidate_name TEXT,
                    target_role TEXT,
                    experience_level TEXT,
                    interview_type TEXT,
                    total_questions INTEGER,
                    candidate_context TEXT,
                    overall_score REAL,
                    is_finished INTEGER DEFAULT 0,
                    created_at REAL,
                    completed_at REAL,
                    session_json TEXT
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS turns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    question_index INTEGER,
                    category TEXT,
                    question_text TEXT,
                    initial_answer TEXT,
                    followup_question TEXT,
                    followup_answer TEXT,
                    relevance_score REAL,
                    structure_score REAL,
                    evidence_score REAL,
                    clarity_score REAL,
                    overall_score REAL,
                    turn_json TEXT,
                    timestamp REAL,
                    FOREIGN KEY(session_id) REFERENCES sessions(session_id) ON DELETE CASCADE
                )
            """)

            conn.execute("CREATE INDEX IF NOT EXISTS idx_sessions_created ON sessions(created_at DESC)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_turns_session ON turns(session_id)")
    finally:
        conn.close()


def save_session(session: InterviewSession, db_path: str = DEFAULT_DB_PATH) -> None:
    """Inserts or updates an interview session and its turns in SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        with conn:
            session_json = json.dumps(session.to_dict())
            conn.execute("""
                INSERT INTO sessions (
                    session_id, candidate_name, target_role, experience_level,
                    interview_type, total_questions, candidate_context,
                    overall_score, is_finished, created_at, completed_at, session_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    overall_score = excluded.overall_score,
                    is_finished = excluded.is_finished,
                    completed_at = excluded.completed_at,
                    session_json = excluded.session_json
            """, (
                session.session_id,
                session.candidate_name,
                session.target_role,
                session.experience_level,
                session.interview_type,
                session.total_questions,
                session.candidate_context,
                session.overall_session_score,
                1 if session.is_finished else 0,
                session.created_at,
                session.completed_at,
                session_json,
            ))

            # Delete prior turns for this session and re-insert current snapshot
            conn.execute("DELETE FROM turns WHERE session_id = ?", (session.session_id,))

            for turn in session.turns:
                turn_eval = turn.turn_evaluation or turn.initial_evaluation
                rel_score = turn_eval.rubric_scores.get("relevance").score if turn_eval and "relevance" in turn_eval.rubric_scores else None
                struct_score = turn_eval.rubric_scores.get("structure").score if turn_eval and "structure" in turn_eval.rubric_scores else None
                evi_score = turn_eval.rubric_scores.get("evidence").score if turn_eval and "evidence" in turn_eval.rubric_scores else None
                clar_score = turn_eval.rubric_scores.get("clarity").score if turn_eval and "clarity" in turn_eval.rubric_scores else None
                overall = turn_eval.overall_score if turn_eval else None

                conn.execute("""
                    INSERT INTO turns (
                        session_id, question_index, category, question_text,
                        initial_answer, followup_question, followup_answer,
                        relevance_score, structure_score, evidence_score, clarity_score,
                        overall_score, turn_json, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    session.session_id,
                    turn.question_index,
                    turn.question.category.value,
                    turn.question.question_text,
                    turn.initial_answer,
                    turn.followup_question,
                    turn.followup_answer,
                    rel_score,
                    struct_score,
                    evi_score,
                    clar_score,
                    overall,
                    json.dumps(turn.to_dict()),
                    turn.timestamp,
                ))
    finally:
        conn.close()


def list_sessions(db_path: str = DEFAULT_DB_PATH, limit: int = 50) -> List[Dict[str, Any]]:
    """Returns a summary list of past sessions."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("""
            SELECT session_id, candidate_name, target_role, experience_level,
                   interview_type, total_questions, overall_score, is_finished,
                   created_at, completed_at
            FROM sessions
            ORDER BY created_at DESC
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_session(session_id: str, db_path: str = DEFAULT_DB_PATH) -> Optional[Dict[str, Any]]:
    """Fetches full session details and turns from SQLite."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT session_json FROM sessions WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if not row or not row["session_json"]:
            return None
        return json.loads(row["session_json"])
    finally:
        conn.close()


def delete_session(session_id: str, db_path: str = DEFAULT_DB_PATH) -> bool:
    """Deletes a session and its associated turns."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        with conn:
            conn.execute("DELETE FROM turns WHERE session_id = ?", (session_id,))
            cursor = conn.execute("DELETE FROM sessions WHERE session_id = ?", (session_id,))
            return cursor.rowcount > 0
    finally:
        conn.close()


def get_aggregate_analytics(db_path: str = DEFAULT_DB_PATH) -> Dict[str, Any]:
    """Computes overall student practice metrics across all recorded sessions."""
    init_db(db_path)
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("""
            SELECT
                COUNT(DISTINCT s.session_id) as total_sessions,
                COUNT(t.id) as total_answers_submitted,
                (SELECT AVG(overall_score) FROM sessions WHERE overall_score IS NOT NULL) as avg_session_score,
                AVG(t.relevance_score) as avg_relevance,
                AVG(t.structure_score) as avg_structure,
                AVG(t.evidence_score) as avg_evidence,
                AVG(t.clarity_score) as avg_clarity
            FROM sessions s
            LEFT JOIN turns t ON s.session_id = t.session_id
        """)
        row = cursor.fetchone()

        # Category performance
        cat_cursor = conn.execute("""
            SELECT category, AVG(overall_score) as avg_score, COUNT(*) as count
            FROM turns
            WHERE overall_score IS NOT NULL
            GROUP BY category
        """)
        cat_rows = cat_cursor.fetchall()
        category_breakdown = {r["category"]: {"avg": round(r["avg_score"] or 0, 2), "count": r["count"]} for r in cat_rows}

        return {
            "total_sessions": row["total_sessions"] or 0,
            "total_answers_submitted": row["total_answers_submitted"] or 0,
            "avg_session_score": round(row["avg_session_score"] or 0, 2),
            "avg_relevance": round(row["avg_relevance"] or 0, 2),
            "avg_structure": round(row["avg_structure"] or 0, 2),
            "avg_evidence": round(row["avg_evidence"] or 0, 2),
            "avg_clarity": round(row["avg_clarity"] or 0, 2),
            "category_breakdown": category_breakdown,
        }
    finally:
        conn.close()
