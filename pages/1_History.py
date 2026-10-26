"""Browser-local History & Performance dashboard for InterviewIQ."""
import time
import pandas as pd
import streamlit as st

st.set_page_config(page_title="InterviewIQ — History & Performance", page_icon="⚡", layout="wide")
st.title("History & Performance")
email = st.session_state.get("authenticated_email")
if not email:
    st.warning("Sign in from the main InterviewIQ page to view your personal history.")
    st.page_link("app.py", label="Go to sign in")
    st.stop()

data = st.session_state.get("browser_data", {"profiles": {}, "sessions": {}})
rows = data.get("sessions", {}).get(email, [])
rows = sorted(rows, key=lambda row: float(row.get("created_at", 0) or 0))
if not rows:
    st.info("No practice history yet. Complete a mock interview to see your graphs here.")
    st.page_link("app.py", label="Start practicing")
    st.stop()

trend, rubric_rows, category_rows = [], [], []
for row in rows:
    stamp = float(row.get("completed_at") or row.get("created_at") or time.time())
    score = row.get("overall_session_score")
    if score is not None:
        trend.append({
            "Practice": time.strftime("%d %b %y", time.localtime(stamp)) + " · " + str(row.get("session_id", ""))[:6],
            "Score": float(score),
        })
    for turn in row.get("turns", []) or []:
        evaluation = turn.get("turn_evaluation") or turn.get("initial_evaluation") or {}
        for key, item in (evaluation.get("rubric_scores") or {}).items():
            try:
                rubric_rows.append({"Criterion": key.title(), "Score": float(item.get("score", 0))})
            except (TypeError, ValueError):
                continue
        category = (turn.get("question") or {}).get("category", "other").title()
        if evaluation.get("overall_score") is not None:
            category_rows.append({"Category": category, "Score": float(evaluation["overall_score"])})

if trend:
    st.subheader("Score progression")
    st.line_chart(pd.DataFrame(trend).set_index("Practice"), y="Score", y_label="Score / 5", use_container_width=True)
if rubric_rows:
    st.subheader("Rubric performance")
    rubric = pd.DataFrame(rubric_rows).groupby("Criterion", as_index=False)["Score"].mean().sort_values("Score")
    st.bar_chart(rubric.set_index("Criterion"), y="Score", y_label="Average score / 5", use_container_width=True)
if category_rows:
    st.subheader("Performance by interview category")
    categories = pd.DataFrame(category_rows).groupby("Category", as_index=False)["Score"].mean().sort_values("Score")
    st.bar_chart(categories.set_index("Category"), y="Score", y_label="Average score / 5", use_container_width=True)

st.subheader("Past sessions")
for row in reversed(rows):
    stamp = float(row.get("created_at") or 0)
    created = time.strftime("%d %b %Y, %H:%M", time.localtime(stamp)) if stamp else "Date unavailable"
    score = row.get("overall_session_score")
    status = "Completed" if row.get("is_finished") else "In progress"
    st.markdown(
        f"**{created} · {row.get('target_role', 'Practice')}** — "
        f"{float(score):.1f} / 5" if score is not None else
        f"**{created} · {row.get('target_role', 'Practice')}** — Not scored"
    )
    st.caption(f"{status} · {row.get('interview_type', '')} · {len(row.get('turns', []) or [])} questions · Session {str(row.get('session_id', ''))[:8]}")

st.warning(
    "This is browser-only storage, not a cloud backup. History is specific to this browser profile and device, "
    "does not sync across devices, and may be permanently lost when browser data is cleared. Download your reports "
    "regularly if you need a durable copy. Do not rely on localStorage for confidential information."
)
