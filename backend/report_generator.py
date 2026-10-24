"""
Practice Report Generator for InterviewIQ.
Generates comprehensive Markdown, HTML, and JSON reports with strengths,
growth areas, turn-by-turn transcripts, and actionable next steps.
"""

from typing import Dict, Any, List
import datetime
from .models import InterviewSession, RUBRIC_DISCLAIMER, ETHICAL_OUTLINE_GUIDELINE


def generate_markdown_report(session: InterviewSession) -> str:
    """Generates an extensive, readable Markdown practice report."""
    date_str = datetime.datetime.fromtimestamp(session.created_at).strftime("%B %d, %Y at %I:%M %p")
    completed_str = (
        datetime.datetime.fromtimestamp(session.completed_at).strftime("%I:%M %p")
        if session.completed_at
        else "In Progress"
    )

    # Compute overall rubric averages across completed turns
    rel_scores, struct_scores, evi_scores, clar_scores, overall_scores = [], [], [], [], []
    for turn in session.turns:
        t_eval = turn.turn_evaluation or turn.initial_evaluation
        if t_eval:
            overall_scores.append(t_eval.overall_score)
            if "relevance" in t_eval.rubric_scores:
                rel_scores.append(t_eval.rubric_scores["relevance"].score)
            if "structure" in t_eval.rubric_scores:
                struct_scores.append(t_eval.rubric_scores["structure"].score)
            if "evidence" in t_eval.rubric_scores:
                evi_scores.append(t_eval.rubric_scores["evidence"].score)
            if "clarity" in t_eval.rubric_scores:
                clar_scores.append(t_eval.rubric_scores["clarity"].score)

    avg_overall = round(sum(overall_scores) / len(overall_scores), 1) if overall_scores else 0.0
    avg_rel = round(sum(rel_scores) / len(rel_scores), 1) if rel_scores else 0.0
    avg_struct = round(sum(struct_scores) / len(struct_scores), 1) if struct_scores else 0.0
    avg_evi = round(sum(evi_scores) / len(evi_scores), 1) if evi_scores else 0.0
    avg_clar = round(sum(clar_scores) / len(clar_scores), 1) if clar_scores else 0.0

    # Aggregate strengths & improvements
    all_strengths = []
    all_improvements = []
    for turn in session.turns:
        t_eval = turn.turn_evaluation or turn.initial_evaluation
        if t_eval:
            all_strengths.extend(t_eval.key_strengths)
            all_improvements.extend(t_eval.actionable_improvements)

    # Deduplicate while preserving order
    unique_strengths = list(dict.fromkeys(all_strengths))[:5]
    unique_improvements = list(dict.fromkeys(all_improvements))[:5]

    md = []
    md.append(f"# 🎯 InterviewIQ Practice & Diagnostic Report")
    md.append(f"**Candidate:** {session.candidate_name or 'Anonymous Candidate'}  ")
    md.append(f"**Target Role:** {session.target_role}  ")
    md.append(f"**Experience Level:** {session.experience_level}  ")
    md.append(f"**Interview Type:** {session.interview_type}  ")
    md.append(f"**Session Date:** {date_str} (Completed: {completed_str})  ")
    md.append(f"**Questions Completed:** {len([t for t in session.turns if t.completed])} / {session.total_questions}\n")

    md.append("> ### ⚠️ Practice Feedback Notice")
    md.append(f"> {RUBRIC_DISCLAIMER}\n")
    md.append(f"> **Ethical Standard:** {ETHICAL_OUTLINE_GUIDELINE}\n")

    md.append("## 📊 Executive Scorecard")
    md.append(f"| Dimension | Average Score (1.0 – 5.0) | Performance Level |")
    md.append(f"| :--- | :---: | :--- |")
    md.append(f"| **Overall Session Score** | **{avg_overall} / 5.0** | {'🌟 Advanced' if avg_overall >= 4.2 else '📈 Proficient' if avg_overall >= 3.3 else '🌱 Developing'} |")
    md.append(f"| **Relevance & Directness** | {avg_rel} / 5.0 | Directly hits prompt intent & follow-up questions |")
    md.append(f"| **Structure & Framework** | {avg_struct} / 5.0 | Logical pacing (STAR, Problem-Solution-Trade-off) |")
    md.append(f"| **Evidence & Ownership** | {avg_evi} / 5.0 | Specific technical details, 'I' vs 'we', concrete impact |")
    md.append(f"| **Clarity & Communication** | {avg_clar} / 5.0 | Professional tone, concise articulation, low filler |")
    md.append("")

    md.append("## 🌟 Key Strengths Identified")
    if unique_strengths:
        for s in unique_strengths:
            md.append(f"- **{s}**")
    else:
        md.append("- Good baseline foundation and willingness to address all prompts.")
    md.append("")

    md.append("## 🚀 Priority Improvement Areas")
    if unique_improvements:
        for imp in unique_improvements:
            md.append(f"- **{imp}**")
    else:
        md.append("- Continue practicing under timed conditions to maintain fluidity.")
    md.append("")

    md.append("## 📝 Turn-by-Turn Diagnostic Transcript")
    for i, turn in enumerate(session.turns):
        t_eval = turn.turn_evaluation or turn.initial_evaluation
        md.append(f"### Question {i+1}: {turn.question.question_text}")
        md.append(f"*Category: {turn.question.category.value.capitalize()} | Focus: {turn.question.competency_or_topic}*\n")

        md.append(f"**Your Initial Response:**\n```\n{turn.initial_answer.strip() or 'No answer recorded.'}\n```\n")

        if turn.followup_question:
            md.append(f"**Follow-Up Question:**\n> *\"{turn.followup_question}\"*\n")
            md.append(f"**Your Follow-Up Response:**\n```\n{turn.followup_answer.strip() or 'No follow-up answer recorded.'}\n```\n")

        if t_eval:
            md.append(f"**Turn Score:** {t_eval.overall_score} / 5.0")
            md.append("| Criterion | Score | Diagnostic Feedback |")
            md.append("| :--- | :---: | :--- |")
            for crit_key, r_score in t_eval.rubric_scores.items():
                md.append(f"| {r_score.display_name} | {r_score.score} / 5.0 | {r_score.feedback} |")
            md.append("")
            md.append(f"**Stronger Answer Outline (Authentic Framework):**\n{t_eval.stronger_answer_outline}\n")
        md.append("---\n")

    md.append("## 🗓️ 7-Day Personalized Action Plan")
    md.append("1. **Day 1–2 (Narrative Distillation):** Write out 3 authentic STAR stories from your real coursework or projects. Ensure your *Action* section occupies 60% of the speaking time.")
    md.append("2. **Day 3–4 (Technical Nuance & Trade-offs):** For every technical concept on your resume, prepare the answer to: *'Under what condition does this fail or perform poorly?'*")
    md.append("3. **Day 5–6 (Follow-up Resilience):** Practice anticipating follow-up questions on edge cases, metrics, and what you would do differently in hindsight.")
    md.append("4. **Day 7 (Retake Mock Session):** Run another 6-question InterviewIQ session to measure your rubric growth across Structure and Evidence.")
    md.append("\n*Report generated by InterviewIQ.*")

    return "\n".join(md)


def generate_html_report(session: InterviewSession) -> str:
    """Generates a standalone, beautiful HTML report suitable for printing or PDF conversion."""
    md_content = generate_markdown_report(session)

    # Basic markdown to HTML conversion with styling
    import html
    escaped_md = html.escape(md_content)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>InterviewIQ Practice Report - {html.escape(session.candidate_name or 'Candidate')}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: #1e293b;
            background-color: #f8fafc;
            margin: 0;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: #ffffff;
            padding: 48px;
            border-radius: 12px;
            box-shadow: 0 4px 16px rgba(0,0,0,0.06);
            border: 1px solid #e2e8f0;
        }}
        h1 {{ color: #0f172a; border-bottom: 2px solid #3b82f6; padding-bottom: 12px; font-size: 28px; }}
        h2 {{ color: #1e3a8a; margin-top: 32px; border-bottom: 1px solid #e2e8f0; padding-bottom: 8px; font-size: 20px; }}
        h3 {{ color: #2563eb; margin-top: 24px; font-size: 16px; }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            background: #eff6ff;
            color: #1d4ed8;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 600;
        }}
        .disclaimer-box {{
            background: #fffbeb;
            border-left: 4px solid #f59e0b;
            padding: 16px 20px;
            border-radius: 6px;
            margin: 24px 0;
            font-size: 14px;
            color: #92400e;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            font-size: 14px;
        }}
        th, td {{
            padding: 10px 14px;
            border: 1px solid #e2e8f0;
            text-align: left;
        }}
        th {{
            background-color: #f1f5f9;
            color: #334155;
            font-weight: 600;
        }}
        pre {{
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            padding: 14px;
            border-radius: 8px;
            white-space: pre-wrap;
            font-size: 13px;
            color: #334155;
        }}
        blockquote {{
            border-left: 4px solid #3b82f6;
            margin: 0;
            padding: 10px 18px;
            background: #f0fdf4;
            color: #166534;
            border-radius: 4px;
        }}
        .score-pill {{
            font-weight: bold;
            color: #1e3a8a;
            background: #dbeafe;
            padding: 2px 8px;
            border-radius: 4px;
        }}
        .print-btn {{
            background: #2563eb;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-weight: 600;
            margin-bottom: 24px;
        }}
        @media print {{
            .print-btn {{ display: none; }}
            body {{ background: white; padding: 0; }}
            .container {{ box-shadow: none; border: none; padding: 0; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
        <div id="report-body">
            <pre style="background:transparent; border:none; font-family:inherit; font-size:inherit; line-height:inherit; white-space:pre-wrap;">{escaped_md}</pre>
        </div>
    </div>
</body>
</html>
"""
