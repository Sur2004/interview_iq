# 1_History.py – Session History & Performance Dashboard
"""
Streamlit multipage file that displays a table of past interview sessions
and aggregate analytics (overall scores, per‑category breakdowns).
It leverages the SQLite helpers in ``backend/database.py``.
"""

import streamlit as st
from backend.database import list_sessions, get_aggregate_analytics, delete_session, get_session
from datetime import datetime

st.set_page_config(page_title="InterviewIQ – History & Performance", layout="wide")

st.title("📚 Interview History & Performance")

# ---------------------------------------------------------------------------
# Theme selector (mirrors the main app)
# ---------------------------------------------------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
theme = st.selectbox("UI Theme", ["Light", "Night (Dark)"], index=0)
st.session_state.theme = theme
if theme == "Night (Dark)":
    st.markdown(
        """
        <style>
            body, .stApp {background-color:#0f172a;color:#f8fafc;}
            .stSelectbox div[data-baseweb="select"] {background:#1e293b;}
        </style>
        """,
        unsafe_allow_html=True,
    )

# ---------------------------------------------------------------------------
# Load and display aggregate analytics
# ---------------------------------------------------------------------------
analytics = get_aggregate_analytics()
col1, col2, col3 = st.columns(3)
col1.metric("Total Sessions", analytics.get("total_sessions", 0))
col2.metric("Answers Submitted", analytics.get("total_answers_submitted", 0))
col3.metric("Avg Session Score", analytics.get("avg_session_score", 0.0))

st.subheader("🧩 Category‑wise Average Scores")
cat_breakdown = analytics.get("category_breakdown", {})
if cat_breakdown:
    cat_df = {
        "Category": list(cat_breakdown.keys()),
        "Avg Score": [v["avg"] for v in cat_breakdown.values()],
        "Answers": [v["count"] for v in cat_breakdown.values()],
    }
    st.table(cat_df)
else:
    st.info("No category data yet – run a few interview rounds first.")

# ---------------------------------------------------------------------------
# Session table with actions
# ---------------------------------------------------------------------------
st.subheader("🗂️ Past Sessions")
sessions = list_sessions(limit=100)
if not sessions:
    st.info("No sessions recorded. Finish a practice round to populate history.")
else:
    # Convert timestamps to readable format
    for s in sessions:
        s["created_at"] = datetime.fromtimestamp(s["created_at"]).strftime("%Y-%m-%d %H:%M")
        if s["completed_at"]:
            s["completed_at"] = datetime.fromtimestamp(s["completed_at"]).strftime("%Y-%m-%d %H:%M")
        else:
            s["completed_at"] = "‑"
        s["overall_score"] = f"{s.get('overall_score') or 'N/A'} / 5.0"
        s["is_finished"] = "✅" if s["is_finished"] else "⏳"

    # Show as a DataFrame for sorting / filtering
    import pandas as pd
    df = pd.DataFrame(sessions)
    df = df[["session_id", "candidate_name", "target_role", "experience_level", "interview_type",
             "total_questions", "overall_score", "is_finished", "created_at", "completed_at"]]
    st.dataframe(df, hide_index=True, use_container_width=True)

    # Action buttons per row – Streamlit does not support per‑row buttons directly, so we use a selectbox.
    selected = st.selectbox(
        "Select a session to view details / delete",
        options=["‑"] + [s["session_id"] for s in sessions],
        format_func=lambda x: "‑" if x == "‑" else f"{x[:8]} – {next(s for s in sessions if s['session_id']==x)['candidate_name']}",
    )
    if selected != "‑":
        sess_data = get_session(selected)
        if sess_data:
            st.subheader(f"🔎 Session {selected[:8]} Details")
            st.json(sess_data)
        else:
            st.warning("Session data could not be loaded.")
        if st.button("Delete this session", key="del_btn"):
            if delete_session(selected):
                st.success("Session deleted. Refresh to see updated list.")
                st.experimental_rerun()
            else:
                st.error("Failed to delete session.")
