"""
Evaluation & Feedback Engine for InterviewIQ.
Scores responses against a visible 4-part rubric (Relevance, Structure, Evidence, Clarity).
Generates constructive improvement advice and stronger answer outlines WITHOUT fabricating credentials.
Supports both live LLM APIs (Gemini / OpenAI compatible) and an intelligent offline diagnostic evaluator.
"""

import os
import re
import json
import logging
from typing import Dict, List, Optional, Tuple
from .models import (
    RubricScore,
    EvaluationResult,
    QuestionItem,
    QuestionCategory,
    RUBRIC_DISCLAIMER,
    ETHICAL_OUTLINE_GUIDELINE,
)

logger = logging.getLogger(__name__)


# Standard Rubric Definitions with transparent scoring anchors
RUBRIC_CRITERIA_META = {
    "relevance": {
        "display_name": "Relevance & Directness",
        "description": "How directly and completely the response addresses the interview question and follow-up prompt without evasion.",
        "anchors": {
            1: "Off-topic or evades the question asked.",
            2: "Partially touches the subject but wanders into unrelated tangents.",
            3: "Addresses the main core of the prompt with moderate directness.",
            4: "Directly and thoroughly answers all parts of the question.",
            5: "Exceptionally targeted; directly hits both primary prompt and underlying sub-intent.",
        },
    },
    "structure": {
        "display_name": "Structure & Framework",
        "description": "Logical flow and structural methodology (e.g. STAR method for behavioral, problem-solution-tradeoff for technical).",
        "anchors": {
            1: "Disorganized stream-of-consciousness; hard to follow.",
            2: "Loose sequence with missing critical milestones (e.g. skips Situation or Action).",
            3: "Follows a recognizable progression with basic transitions.",
            4: "Well-structured (clear beginning, action steps, and outcomes).",
            5: "Masterful narrative structure; seamless pacing and logical signposting.",
        },
    },
    "evidence": {
        "display_name": "Evidence & Personal Ownership",
        "description": "Concrete technical details, personal contributions ('I' vs generic 'we'), and verifiable outcomes.",
        "anchors": {
            1: "Purely abstract generalities with zero concrete examples or ownership.",
            2: "High-level description of group work without showing personal role.",
            3: "Describes personal actions with some technical or situational specifics.",
            4: "Strong specific examples, technical decisions, and tangible results.",
            5: "Compelling concrete evidence; demonstrates deep personal agency and measurable impact.",
        },
    },
    "clarity": {
        "display_name": "Clarity & Communication",
        "description": "Professional tone, conciseness, articulate terminology, and absence of excessive filler.",
        "anchors": {
            1: "Extremely fragmented, repetitive, or confusing phrasing.",
            2: "Noticeable filler, awkward wording, or excessive jargon without substance.",
            3: "Clear and understandable with minor wordiness.",
            4: "Crisp, confident, articulate, and professionally phrased.",
            5: "Exemplary executive clarity; concise, precise, and compelling.",
        },
    },
}


def _detect_star_elements(text: str) -> Dict[str, bool]:
    """Detects presence of STAR structural markers in candidate answers."""
    lower = text.lower()

    # Situation markers
    situation_found = bool(re.search(
        r"\b(when i was|during|at the time|in my|in a project|in college|in class|coursework|hackathon|working on|faced with|the problem was)\b",
        lower,
        re.IGNORECASE,
    ))

    # Task markers
    task_found = bool(re.search(
        r"\b(my role|my task|responsible for|needed to|had to|goal was|objective was|assigned to|aimed to)\b",
        lower,
        re.IGNORECASE,
    ))

    # Action markers
    action_found = bool(re.search(
        r"\b(i decided|i implemented|i built|i designed|i refactored|i spoke with|i investigated|i wrote|i chose|i optimized|i analyzed|i tested|i presented|i evaluated)\b",
        lower,
        re.IGNORECASE,
    ))

    # Result markers
    result_found = bool(re.search(
        r"\b(as a result|ultimately|in the end|outcome|achieved|reduced|improved|learned|delivered|shipped|finished|prevented)\b",
        lower,
        re.IGNORECASE,
    ))

    return {
        "situation": situation_found,
        "task": task_found,
        "action": action_found,
        "result": result_found,
    }


def _detect_technical_elements(text: str) -> Dict[str, bool]:
    """Detects technical depth indicators (tradeoffs, complexity, architecture)."""
    lower = text.lower()
    has_tradeoff = bool(re.search(r"\b(trade-off|tradeoff|versus|vs|instead of|alternative|compromise|drawback|benefit|pro and con|amplification)\b", lower, re.IGNORECASE))
    has_metrics = bool(re.search(r"\b(\d+[%mskbgbx]?|latency|throughput|o\(|big-o|complexity|seconds|milliseconds|qps|queries|memory|cpu|disk|i/o)\b", lower, re.IGNORECASE))
    has_technical_terms = bool(re.search(r"\b(api|database|index|query|cache|concurrency|thread|async|pipeline|algorithm|schema|b-tree|microservice|docker|test|debug|log|metric)\b", lower, re.IGNORECASE))
    has_first_person = bool(re.search(r"\b(i |my |me )\b", lower, re.IGNORECASE))

    return {
        "tradeoff": has_tradeoff,
        "metrics": has_metrics,
        "terms": has_technical_terms,
        "first_person": has_first_person,
    }


def evaluate_heuristically(
    question: QuestionItem,
    candidate_answer: str,
    followup_answer: Optional[str] = None,
    candidate_context: str = "",
) -> EvaluationResult:
    """
    Intelligent offline rubric evaluation when no external LLM API is configured.
    Provides rigorous, predictable, and transparent practice diagnostics.
    """
    combined_answer = candidate_answer
    if followup_answer:
        combined_answer += "\n" + followup_answer

    word_count = len(combined_answer.strip().split())
    lower = combined_answer.lower()

    # Category-specific heuristics
    is_behavioral = question.category == QuestionCategory.BEHAVIORAL
    is_tech = question.category == QuestionCategory.TECHNICAL
    is_project = question.category == QuestionCategory.PROJECT

    star = _detect_star_elements(combined_answer)
    tech = _detect_technical_elements(combined_answer)

    # 1. Relevance Score Calculation (1.0 to 5.0)
    prompt_words = [w.lower() for w in re.findall(r"\b[A-Za-z]{4,}\b", question.question_text)]
    overlap = sum(1 for w in prompt_words if w in lower)
    if word_count < 20:
        relevance_score = 1.5
        rel_feedback = "Answer is too brief to address the prompt's core question."
    elif word_count < 40 and overlap < 2:
        relevance_score = 2.5
        rel_feedback = "Partially answers the question, but leaves key aspects unaddressed."
    else:
        if overlap >= 2 or (tech["tradeoff"] and tech["terms"]):
            relevance_score = 4.5 if (followup_answer and len(followup_answer.split()) > 20) else 4.0
            rel_feedback = "Directly addresses the prompt and maintains focus throughout."
        else:
            relevance_score = 3.2
            rel_feedback = "Addresses the general topic, but could align more tightly with the prompt's specific challenge."

    # 2. Structure Score Calculation (1.0 to 5.0)
    if is_behavioral:
        star_count = sum(1 for v in star.values() if v)
        if star_count == 4:
            structure_score = 4.8
            struct_feedback = "Excellent STAR progression (Situation, Task, Action, Result clearly marked)."
        elif star_count == 3:
            structure_score = 3.8
            missing = [k.capitalize() for k, v in star.items() if not v]
            struct_feedback = f"Solid narrative flow, but could strengthen the {', '.join(missing)} section."
        elif star_count >= 1:
            structure_score = 2.7
            struct_feedback = "Loose chronological narrative; adopt an explicit STAR structure to keep your story crisp."
        else:
            structure_score = 1.8
            struct_feedback = "Lacks structured sequencing; difficult for an interviewer to track the timeline."
    else:
        # Technical / Project structure
        has_intro = bool(re.search(r"^(in general|first|to begin|when dealing with|the main concept|a |an )", lower))
        has_contrast = tech["tradeoff"]
        has_conclusion = bool(re.search(r"(therefore|in summary|overall|as a result|ultimately|trade-off|tradeoff)", lower))
        points = sum([has_intro, has_contrast, has_conclusion, word_count > 40])
        structure_score = min(5.0, 2.5 + (points * 0.65))
        if structure_score >= 4.0 or tech["tradeoff"]:
            structure_score = max(4.0, structure_score)
            struct_feedback = "Logical technical flow: definition, mechanics, trade-offs, and practical application."
        else:
            struct_feedback = "Consider organizing technical answers: High-level summary -> How it works -> Trade-offs -> Practical example."

    # 3. Evidence & Ownership Score Calculation (1.0 to 5.0)
    has_i = tech["first_person"]
    has_metrics = tech["metrics"]

    if is_tech:
        evidence_score = 2.5
        if tech["terms"]:
            evidence_score += 1.0
        if tech["tradeoff"]:
            evidence_score += 0.8
        if tech["metrics"]:
            evidence_score += 0.7
        evidence_score = max(1.0, min(5.0, evidence_score))
        if evidence_score >= 4.0:
            evi_feedback = "Strong technical evidence: specific data structures, computational trade-offs, and mechanical depth."
        elif evidence_score >= 3.0:
            evi_feedback = "Good technical basis, but provide deeper mechanical depth or complexity analysis."
        else:
            evi_feedback = "Needs concrete technical specifics, mechanisms, and trade-off comparisons."
    else:
        evidence_score = 2.0
        if has_i:
            evidence_score += 1.0
        if has_metrics:
            evidence_score += 0.8
        if word_count > 90:
            evidence_score += 0.6
        if tech["terms"] or tech["tradeoff"]:
            evidence_score += 0.6
        evidence_score = max(1.0, min(5.0, evidence_score))

        if evidence_score >= 4.0:
            evi_feedback = "Strong personal ownership ('I') backed by concrete specifics and observable outcomes."
        elif evidence_score >= 3.0:
            evi_feedback = "Good foundation, but replace generic statements with your exact individual contributions."
        else:
            evi_feedback = "Needs concrete examples. Avoid speaking in hypotheticals; anchor your answer to a real project or lab."

    # 4. Clarity Score Calculation (1.0 to 5.0)
    filler_words = len(re.findall(r"\b(um|uh|like|sort of|kind of|basically|you know|stuff|things)\b", lower))
    clarity_score = 4.0
    if filler_words > 4:
        clarity_score -= 1.0
    if word_count < 30:
        clarity_score -= 1.0
    elif word_count > 250:
        clarity_score -= 0.5  # slightly rambling
    clarity_score = max(1.0, min(5.0, clarity_score))
    if clarity_score >= 4.0:
        clar_feedback = "Clear, articulate, and well-paced communication."
    else:
        clar_feedback = "Work on conciseness and replace filler words with precise technical vocabulary."

    # Overall calculation
    overall_score = round(
        (relevance_score * 0.3) +
        (structure_score * 0.25) +
        (evidence_score * 0.25) +
        (clarity_score * 0.2),
        1
    )

    # Key strengths & improvements
    strengths = []
    improvements = []

    if relevance_score >= 3.8:
        strengths.append("Directly targeted the core question without unnecessary filler.")
    if structure_score >= 3.8:
        strengths.append("Followed a clear, logical progression that was easy for the interviewer to follow.")
    if tech["first_person"]:
        strengths.append("Maintained clear personal agency using first-person ownership ('I' rather than generic 'we').")
    if tech["tradeoff"] or tech["terms"]:
        strengths.append("Demonstrated technical nuance by discussing trade-offs and domain concepts.")
    if not strengths:
        strengths.append("Clear willingness to address the question and communicate your approach.")

    if structure_score < 3.5:
        if is_behavioral:
            improvements.append("Use the STAR framework explicitly: devote 20% to Situation/Task, 60% to your Actions, and 20% to Results.")
        else:
            improvements.append("Structure technical responses: 1) Core definition, 2) Internal mechanics, 3) Real-world trade-offs.")
    if not tech["metrics"] and (is_behavioral or is_project):
        improvements.append("Add measurable evidence or observable signals (e.g. latency reduced, test coverage added, team time saved).")
    if not tech["first_person"]:
        improvements.append("Avoid saying 'we did' or passive voice; interviewers want to know YOUR exact individual actions.")
    if word_count < 60:
        improvements.append("Expand on your technical decision-making: explain WHY you picked your approach over alternatives.")
    if not improvements:
        improvements.append("To elevate this to an exceptional response, discuss an unexpected edge case or what you would do differently in hindsight.")

    # Generate constructive outline WITHOUT fabricating credentials
    outline = generate_ethical_outline(question, candidate_context)

    # Generate dynamic follow-up question if none has been asked yet
    followup_q = None
    if not followup_answer:
        followup_q = generate_followup_question(question, candidate_answer)

    rubric_scores = {
        "relevance": RubricScore("relevance", RUBRIC_CRITERIA_META["relevance"]["display_name"], round(relevance_score, 1), rel_feedback),
        "structure": RubricScore("structure", RUBRIC_CRITERIA_META["structure"]["display_name"], round(structure_score, 1), struct_feedback),
        "evidence": RubricScore("evidence", RUBRIC_CRITERIA_META["evidence"]["display_name"], round(evidence_score, 1), evi_feedback),
        "clarity": RubricScore("clarity", RUBRIC_CRITERIA_META["clarity"]["display_name"], round(clarity_score, 1), clar_feedback),
    }

    return EvaluationResult(
        overall_score=overall_score,
        rubric_scores=rubric_scores,
        key_strengths=strengths,
        actionable_improvements=improvements,
        stronger_answer_outline=outline,
        suggested_followup_question=followup_q,
    )


def generate_followup_question(question: QuestionItem, candidate_answer: str) -> str:
    """
    Synthesizes an intelligent, contextual follow-up question based on what was said or omitted.
    """
    lower = candidate_answer.lower()

    if question.category == QuestionCategory.BEHAVIORAL:
        if "learned" not in lower and "hindsight" not in lower:
            return "Looking back at that experience today, what is the single biggest lesson you took away, and how has it influenced your current workflow?"
        elif "disagree" in lower or "conflict" in lower:
            return "If one of the stakeholders had pushed back hard on your compromise, what data or proof-of-concept would you have presented to convince them?"
        else:
            return "What was the most difficult personal trade-off you had to make in that situation, and how did you measure whether the final result was a success?"

    elif question.category == QuestionCategory.TECHNICAL:
        if "bottleneck" not in lower and "scale" not in lower:
            return "If your system suddenly experienced a 50x spike in concurrent read and write operations, where is the first point of failure and how would you mitigate it?"
        elif "trade-off" not in lower and "drawback" not in lower:
            return "Every technical decision has a downside. What is the biggest drawback or limitation of the approach you just described?"
        else:
            return "How would you design the telemetry, metrics, and alerting to detect if this component degraded or failed silently in production?"

    else:  # Project explanation
        if "test" not in lower and "bug" not in lower:
            return "Walk me through how you validated and tested that component before deploying it. What unexpected edge case did you discover?"
        else:
            return "If you had an additional month and full technical autonomy, what architectural refactor or performance upgrade would you prioritize next?"


def generate_ethical_outline(question: QuestionItem, candidate_context: str = "") -> str:
    """
    Produces a structural outline guiding the student on HOW to build an exemplary response
    using THEIR OWN authentic experiences. NEVER fabricates fake employers or false credentials.
    """
    context_note = ""
    if candidate_context.strip():
        context_note = f"\n> *Tip tailored to your background ({candidate_context[:80]}...): Anchor this outline to one of your real projects or coursework.*"

    if question.category == QuestionCategory.BEHAVIORAL:
        return (
            "### 🧭 Stronger Answer Structural Blueprint (STAR Method)\n"
            f"{context_note}\n\n"
            "1. **Situation (10–15%):**\n"
            "   - State the authentic context (e.g. *'In a group software engineering capstone project...'* or *'During a university hackathon...'*).\n"
            "   - Identify the deadline, team dynamics, and the high-stakes problem you were solving.\n\n"
            "2. **Task (10%):**\n"
            "   - Clarify your personal responsibility versus the team's shared mandate (*'My specific task was to build the data ingestion pipeline and ensure zero dropped events'*).\n\n"
            "3. **Action (55–60% - Heart of the Answer):**\n"
            "   - Walk through 2–3 concrete steps **YOU** took.\n"
            "   - Explain your decision-making and rationale (*'I evaluated Option A and Option B, choosing A because...'*).\n"
            "   - Describe how you communicated, resolved blockers, or handled disagreements.\n\n"
            "4. **Result & Takeaway (15–20%):**\n"
            "   - State the genuine outcome (e.g., project finished ahead of time, zero bugs in final demo, positive peer reviews).\n"
            "   - Highlight what this taught you that you now carry into your future engineering work.\n\n"
            "> *Ethical Note: Notice how this framework elevates your story without needing to invent fictional company names or inflated metrics.*"
        )
    elif question.category == QuestionCategory.TECHNICAL:
        return (
            "### ⚙️ Stronger Technical Answer Architecture\n"
            f"{context_note}\n\n"
            "1. **Executive Definition (1–2 sentences):**\n"
            "   - Define the core concept clearly without jargon fluff (*'At its core, X solves Y by doing Z'*).\n\n"
            "2. **Mechanism & How It Works Under the Hood:**\n"
            "   - Break down the underlying data structure, protocol, or algorithmic flow.\n"
            "   - Mention time/space complexity (e.g., *O(1)* lookups vs *O(log N)* traversals) where applicable.\n\n"
            "3. **Trade-offs & Edge Cases:**\n"
            "   - Explain when you would **NOT** use this pattern.\n"
            "   - Discuss write amplification, memory footprint, cache invalidation, or network overhead.\n\n"
            "4. **Concrete Real-World Scenario:**\n"
            "   - Ground it in a real tool or personal project (*'For example, when I designed a cached API in FastAPI...'*).\n"
        )
    else:  # Project explanation
        return (
            "### 🏗️ Stronger Project Deep-Dive Architecture\n"
            f"{context_note}\n\n"
            "1. **High-Level Context & User Problem:**\n"
            "   - What real problem did this project solve, and who were the users?\n\n"
            "2. **System Architecture & Stack Justification:**\n"
            "   - Outline the frontend, backend, persistence, and communication layers.\n"
            "   - Justify your stack choices based on constraints (e.g. rapid prototyping vs strict schema typing).\n\n"
            "3. **Your Core Technical Contribution:**\n"
            "   - Highlight the single most challenging module you designed and implemented yourself.\n\n"
            "4. **Failure Modes & Retrospective:**\n"
            "   - Discuss a tricky bug you resolved and how you would architect it differently with today's knowledge.\n"
        )


def evaluate_with_llm(
    question: QuestionItem,
    candidate_answer: str,
    followup_answer: Optional[str] = None,
    candidate_context: str = "",
    api_key: Optional[str] = None,
    provider: str = "gemini",
) -> EvaluationResult:
    """
    Evaluates responses using an LLM API (Google Gemini or OpenAI).
    Falls back gracefully to the heuristic evaluator if the API call fails or no key is provided.
    """
    api_key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.info("No LLM API key provided; using intelligent heuristic evaluation engine.")
        return evaluate_heuristically(question, candidate_answer, followup_answer, candidate_context)

    # If key is available, attempt live LLM evaluation with strict ethical prompt
    system_prompt = (
        "You are an expert interview coach for students and early-career job applicants. "
        "Your role is to provide rigorous, constructive, and actionable feedback based strictly "
        "on a 4-part visible rubric: Relevance, Structure, Evidence, and Clarity (scores 1.0 to 5.0). "
        "CRITICAL ETHICAL CONSTRAINT: You must NEVER invent fake companies, unearned credentials, "
        "or false work experience. Your improvement outlines must provide structural templates "
        "guiding the candidate on how to frame their OWN authentic experiences, coursework, or projects. "
        "Scores are practice indicators for skill development, not hiring predictions. "
        "Return your evaluation STRICTLY as valid JSON matching the required schema."
    )

    user_prompt = f"""
QUESTION CATEGORY: {question.category.value}
QUESTION TOPIC: {question.competency_or_topic}
TARGET ROLE: {question.role}
INTERVIEW QUESTION: {question.question_text}
CANDIDATE'S PRIMARY ANSWER:
{candidate_answer}

FOLLOW-UP QUESTION (IF ANY): {question.default_followup}
CANDIDATE'S FOLLOW-UP ANSWER (IF ANY): {followup_answer or "N/A"}

CANDIDATE AUTHENTIC CONTEXT (PROJECTS/STUDIES): {candidate_context or "None provided"}

Evaluate the candidate's responses on the 4 criteria (each from 1.0 to 5.0):
1. relevance (score, feedback)
2. structure (score, feedback)
3. evidence (score, feedback)
4. clarity (score, feedback)

Also provide:
- overall_score (1.0 to 5.0)
- key_strengths (list of 2-3 specific positive observations)
- actionable_improvements (list of 2-3 concrete ways to elevate the response)
- stronger_answer_outline (markdown structural outline guiding them on framing their real work)
- suggested_followup_question (probing follow-up question if not yet answered)

Format output as pure JSON:
{{
  "overall_score": 3.8,
  "rubric_scores": {{
    "relevance": {{"score": 4.0, "feedback": "..."}},
    "structure": {{"score": 3.5, "feedback": "..."}},
    "evidence": {{"score": 3.5, "feedback": "..."}},
    "clarity": {{"score": 4.2, "feedback": "..."}}
  }},
  "key_strengths": ["...", "..."],
  "actionable_improvements": ["...", "..."],
  "stronger_answer_outline": "...",
  "suggested_followup_question": "..."
}}
"""

    try:
        import requests

        if provider.lower() == "gemini" or "AIza" in (api_key or ""):
            # Call Google Gemini API (v1beta)
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            payload = {
                "contents": [
                    {"parts": [{"text": f"{system_prompt}\n\n{user_prompt}"}]}
                ],
                "generationConfig": {
                    "temperature": 0.2,
                    "responseMimeType": "application/json"
                }
            }
            resp = requests.post(url, json=payload, timeout=12)
            if resp.status_code == 200:
                raw_text = resp.json()["candidates"][0]["content"]["parts"][0]["text"]
                data = json.loads(raw_text)
                return _parse_llm_json(data, question)
            else:
                logger.warning(f"Gemini API returned status {resp.status_code}; falling back to heuristic.")
        else:
            # OpenAI compatible endpoint
            url = "https://api.openai.com/v1/chat/completions"
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.2,
                "response_format": {"type": "json_object"}
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                raw_text = resp.json()["choices"][0]["message"]["content"]
                data = json.loads(raw_text)
                return _parse_llm_json(data, question)
            else:
                logger.warning(f"OpenAI API returned status {resp.status_code}; falling back to heuristic.")

    except Exception as e:
        logger.warning(f"LLM evaluation failed ({e}); falling back to heuristic evaluation.")

    return evaluate_heuristically(question, candidate_answer, followup_answer, candidate_context)


def _parse_llm_json(data: dict, question: QuestionItem) -> EvaluationResult:
    """Helper to safely build EvaluationResult from LLM JSON response."""
    rubric_scores = {}
    for crit in ["relevance", "structure", "evidence", "clarity"]:
        raw_crit = data.get("rubric_scores", {}).get(crit, {})
        score = float(raw_crit.get("score", 3.0))
        feedback = raw_crit.get("feedback", "Solid response.")
        disp_name = RUBRIC_CRITERIA_META[crit]["display_name"]
        rubric_scores[crit] = RubricScore(
            criterion=crit,
            display_name=disp_name,
            score=min(5.0, max(1.0, score)),
            feedback=feedback,
        )

    return EvaluationResult(
        overall_score=min(5.0, max(1.0, float(data.get("overall_score", 3.5)))),
        rubric_scores=rubric_scores,
        key_strengths=data.get("key_strengths", ["Addressed the question directly."]),
        actionable_improvements=data.get("actionable_improvements", ["Deepen evidence and personal ownership."]),
        stronger_answer_outline=data.get("stronger_answer_outline", generate_ethical_outline(question)),
        suggested_followup_question=data.get("suggested_followup_question"),
    )
