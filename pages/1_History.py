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
st.caption("Review practice trends, inspect a saved session, or remove a session you no longer need.")

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
    import pandas as pd
    cat_df = pd.DataFrame([
        {"Category": category, "Average score": values["avg"], "Answers": values["count"]}
        for category, values in cat_breakdown.items()
    ])
    st.dataframe(
        cat_df,
        hide_index=True,
        use_container_width=True,
        column_config={
            "Average score": st.column_config.NumberColumn(format="%.1f / 5.0"),
            "Answers": st.column_config.NumberColumn(format="%d"),
        },
    )
else:
    st.info("No category data yet. Complete a practice round to see your strengths and growth areas.")

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
            summary_cols = st.columns(3)
            summary_cols[0].metric("Role", sess_data.get("target_role", "—"))
            summary_cols[1].metric("Experience", sess_data.get("experience_level", "—"))
            summary_cols[2].metric("Questions", sess_data.get("total_questions", 0))
            st.caption("Expand the raw session record only when you need debugging details.")
            with st.expander("Raw session data", expanded=False):
                st.json(sess_data)
        else:
            st.warning("Session data could not be loaded.")
        confirm_key = f"confirm_delete_{selected}"
        if st.button("Delete this session", key="del_btn", type="secondary"):
            st.session_state[confirm_key] = True
        if st.session_state.get(confirm_key, False):
            st.warning("This permanently deletes the selected session and its saved answers.")
            confirm_col, cancel_col = st.columns(2)
            with confirm_col:
                if st.button("Confirm delete", key=f"confirm_btn_{selected}", type="primary"):
                    if delete_session(selected):
                        st.session_state.pop(confirm_key, None)
                        st.success("Session deleted.")
                        st.rerun()
                    else:
                        st.error("Failed to delete session.")
            with cancel_col:
                if st.button("Cancel", key=f"cancel_btn_{selected}"):
                    st.session_state.pop(confirm_key, None)
                    st.rerun()
