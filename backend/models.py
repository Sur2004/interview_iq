"""
Core data models and type definitions for InterviewIQ.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Optional
import time

RUBRIC_DISCLAIMER = (
    "Practice Feedback Notice: Scores and feedback are formative practice indicators "
    "designed to highlight communication structure, technical depth, and answer organization. "
    "They are NOT predictive hiring decisions, ATS filters, or employment guarantees. "
    "Use these insights to refine your authentic voice and genuine experiences."
)

ETHICAL_OUTLINE_GUIDELINE = (
    "Ethical Practice Rule: Feedback and stronger outlines provide structural scaffolding "
    "and strategic framing prompts. They NEVER fabricate fictional company names, "
    "unearned technical credentials, or false project metrics."
)


class ExperienceLevel(str, Enum):
    INTERNSHIP = "Undergraduate Internship"
    GRADUATE = "Graduate / Entry-Level (0-1 yrs)"
    JUNIOR = "Associate / Junior (1-2 yrs)"
    SWITCHER = "Career Transition / Switcher"


class InterviewType(str, Enum):
    COMPREHENSIVE = "Comprehensive Mixed (Behavioral + Tech + Project)"
    BEHAVIORAL = "Behavioral Focus (STAR Framework)"
    TECHNICAL = "Role-Specific Technical Deep-Dive"
    PROJECT_EXPLANATION = "Project Architecture & Trade-Offs"


class TargetRole(str, Enum):
    SOFTWARE_ENGINEERING = "Software Engineering (Full Stack / Backend)"
    FRONTEND_ENGINEERING = "Frontend & Web Engineering"
    DATA_SCIENCE_ML = "Data Science & Machine Learning"
    AI_LLM_ENGINEERING = "AI & LLM Application Engineering"
    CYBERSECURITY = "Cybersecurity & Information Security"
    PRODUCT_MANAGEMENT = "Product Management"
    DEVOPS_CLOUD = "DevOps & Cloud Engineering"
    CUSTOM = "Custom Target Role"


class QuestionCategory(str, Enum):
    BEHAVIORAL = "behavioral"
    TECHNICAL = "technical"
    PROJECT = "project"


@dataclass
class RubricScore:
    criterion: str  # "relevance", "structure", "evidence", "clarity"
    display_name: str
    score: float  # 1.0 to 5.0
    feedback: str
    strengths: List[str] = field(default_factory=list)
    areas_for_growth: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvaluationResult:
    overall_score: float  # 1.0 to 5.0
    rubric_scores: Dict[str, RubricScore] = field(default_factory=dict)
    key_strengths: List[str] = field(default_factory=list)
    actionable_improvements: List[str] = field(default_factory=list)
    stronger_answer_outline: str = ""
    suggested_followup_question: Optional[str] = None
    technical_breakdown: Optional[Dict[str, Any]] = None
    architecture_diagram_mermaid: Optional[str] = None
    disclaimer: str = RUBRIC_DISCLAIMER
    ethical_note: str = ETHICAL_OUTLINE_GUIDELINE

    def to_dict(self) -> dict:
        return {
            "overall_score": round(self.overall_score, 1),
            "rubric_scores": {k: v.to_dict() for k, v in self.rubric_scores.items()},
            "key_strengths": self.key_strengths,
            "actionable_improvements": self.actionable_improvements,
            "stronger_answer_outline": self.stronger_answer_outline,
            "suggested_followup_question": self.suggested_followup_question,
            "technical_breakdown": self.technical_breakdown,
            "architecture_diagram_mermaid": self.architecture_diagram_mermaid,
            "disclaimer": self.disclaimer,
            "ethical_note": self.ethical_note,
        }


@dataclass
class QuestionItem:
    id: str
    category: QuestionCategory
    role: str
    question_text: str
    competency_or_topic: str
    rubric_hints: List[str] = field(default_factory=list)
    default_followup: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["category"] = self.category.value
        return data


@dataclass
class InterviewTurn:
    question_index: int
    question: QuestionItem
    initial_answer: str = ""
    initial_evaluation: Optional[EvaluationResult] = None
    followup_question: str = ""
    followup_answer: str = ""
    turn_evaluation: Optional[EvaluationResult] = None
    completed: bool = False
    timestamp: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "question_index": self.question_index,
            "question": self.question.to_dict(),
            "initial_answer": self.initial_answer,
            "initial_evaluation": (
                self.initial_evaluation.to_dict() if self.initial_evaluation else None
            ),
            "followup_question": self.followup_question,
            "followup_answer": self.followup_answer,
            "turn_evaluation": (
                self.turn_evaluation.to_dict() if self.turn_evaluation else None
            ),
            "completed": self.completed,
            "timestamp": self.timestamp,
        }


@dataclass
class InterviewSession:
    session_id: str
    candidate_name: str
    target_role: str
    experience_level: str
    interview_type: str
    total_questions: int
    candidate_context: str = ""  # Real coursework/projects entered by student
    turns: List[InterviewTurn] = field(default_factory=list)
    current_turn_index: int = 0
    in_followup: bool = False
    is_finished: bool = False
    created_at: float = field(default_factory=time.time)
    completed_at: Optional[float] = None
    overall_session_score: Optional[float] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "candidate_name": self.candidate_name,
            "target_role": self.target_role,
            "experience_level": self.experience_level,
            "interview_type": self.interview_type,
            "total_questions": self.total_questions,
            "candidate_context": self.candidate_context,
            "turns": [turn.to_dict() for turn in self.turns],
            "current_turn_index": self.current_turn_index,
            "in_followup": self.in_followup,
            "is_finished": self.is_finished,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "overall_session_score": self.overall_session_score,
        }
