"""InterviewIQ — candidate command centre."""
import time
import html
from datetime import date
import pandas as pd
import streamlit as st

st.set_page_config(page_title="InterviewIQ | Command Centre", page_icon="⚡", layout="wide")
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"]{font-family:'DM Sans',sans-serif}
.block-container{max-width:1360px;padding-top:1.4rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#0c1427}
[data-testid="stSidebar"] *{color:#e7edff}
.hero{position:relative;overflow:hidden;padding:34px 38px;border-radius:24px;background:radial-gradient(circle at 85% 10%,#536fe8 0,transparent 30%),linear-gradient(120deg,#101a35,#243f82 68%,#3159ba);color:#fff;margin:0 0 22px;box-shadow:0 18px 48px rgba(20,38,86,.2)}
.hero:after{content:"";position:absolute;width:240px;height:240px;border:1px solid rgba(255,255,255,.15);border-radius:50%;right:7%;top:-130px;box-shadow:0 0 0 28px rgba(255,255,255,.035),0 0 0 58px rgba(255,255,255,.025)}
.eyebrow{font-size:.72rem;font-weight:800;letter-spacing:.16em;color:#b9ceff;text-transform:uppercase}
.hero h1{font-size:clamp(2rem,3vw,2.7rem);letter-spacing:-.055em;line-height:1.08;margin:.5rem 0;color:white}
.hero p{max-width:720px;color:#dbe5ff;font-size:1rem;margin:0}
.panel{border:1px solid #e5eaf3;border-radius:18px;padding:20px 22px;background:linear-gradient(145deg,#fff,#f8faff);height:100%;box-shadow:0 6px 22px rgba(16,24,40,.035)}
.panel-kicker{font-size:.72rem;letter-spacing:.1em;text-transform:uppercase;font-weight:800;color:#64748b}
.panel h3{font-size:1.12rem;color:#172033;margin:.45rem 0}
.panel p{font-size:.88rem;color:#64748b;line-height:1.55}
[data-testid="stMetric"]{border:1px solid #e5eaf3;border-radius:16px;padding:15px 17px;background:linear-gradient(145deg,#fff,#f7f9ff);box-shadow:0 5px 18px rgba(16,24,40,.035)}
div.stButton>button{border-radius:11px;font-weight:700;min-height:2.7rem}
div[data-testid="stExpander"]{border:1px solid #e5eaf3;border-radius:14px}
hr{border-color:#e9edf5}
</style>
""", unsafe_allow_html=True)

candidate_id = st.session_state.get("authenticated_candidate_id") or st.session_state.get("authenticated_email")
if not candidate_id:
    st.warning("Sign in from the main InterviewIQ page to load your personal dashboard.")
    st.page_link("app.py", label="Open sign in", icon="🔐")
    st.stop()

data = st.session_state.get("browser_data", {"profiles": {}, "sessions": {}})
profile = data.get("profiles", {}).get(candidate_id, {})
rows = data.get("sessions", {}).get(candidate_id, [])
completed = [r for r in rows if r.get("is_finished")]
scores = [float(r["overall_session_score"]) for r in completed if r.get("overall_session_score") is not None]
avg = sum(scores) / len(scores) if scores else 0
best = max(scores) if scores else 0
name = profile.get("name") or st.session_state.get("sb_candidate_name") or "Candidate"
today = date.today()

st.markdown(f'<div class="hero"><div class="eyebrow">INTERVIEWIQ · DAILY COMMAND CENTRE</div><h1>Good to see you, {html.escape(str(name))}.</h1><p>Your interview preparation, performance signals and technology briefing — together in one workspace.</p></div>', unsafe_allow_html=True)

m = st.columns(4)
m[0].metric("Practice sessions", len(rows))
m[1].metric("Completed rounds", len(completed))
m[2].metric("Average score", f"{avg:.1f} / 5" if scores else "—")
m[3].metric("Personal best", f"{best:.1f} / 5" if scores else "—")

left, right = st.columns([1.55, 1], gap="large")
with left:
    st.subheader("Performance trajectory")
    scored = []
    for r in sorted(rows, key=lambda x: float(x.get("created_at", 0) or 0)):
        score = r.get("overall_session_score")
        if score is not None:
            stamp = float(r.get("completed_at") or r.get("created_at") or 0)
            scored.append({"Date": time.strftime("%d %b", time.localtime(stamp)) if stamp else "Practice", "Score": float(score)})
    if scored:
        st.line_chart(pd.DataFrame(scored).set_index("Date"), y="Score", y_min=0, y_max=5, color="#5275e8")
    else:
        st.info("Your score graph will appear after your first completed mock interview.")
with right:
    st.subheader("Your next milestone")
    target = 4.0
    progress = min(avg / target, 1.0) if scores else 0
    st.progress(progress, text=f"{avg:.1f} / {target:.1f} target score" if scores else "Complete a first interview to set your baseline")
    st.markdown("**Focus for your next session**")
    if scores:
        st.caption("Review the lowest-scoring rubric criteria in History & Performance, then practise one targeted answer.")
    else:
        st.caption("Start with a 5-question interview. Your first result becomes the baseline for future improvement.")
    st.page_link("pages/1_History.py", label="Open performance analytics", icon="📊")

st.divider()
st.subheader("Your preparation workspace")
cards = [
    ("01 · PRACTICE", "Mock interview", "Role-specific questions, follow-ups and structured feedback.", "app.py", "Start an interview", "🎯"),
    ("02 · DAILY BRIEFING", "Interview & tech updates", "Question of the day, current developer news and official release notes.", "pages/3_Daily_Briefing.py", "Explore today's briefing", "⚡"),
    ("03 · PERFORMANCE", "History & analytics", "Score progression, rubric strengths and category-wise performance.", "pages/1_History.py", "View your progress", "📈"),
    ("04 · UNDER THE HOOD", "System architecture", "Understand APIs, JSON payloads, evaluation and model tokens.", "pages/2_System_Architecture.py", "Explore the architecture", "🧭"),
]
for start in range(0, len(cards), 2):
    cols = st.columns(2, gap="large")
    for col, card in zip(cols, cards[start:start+2]):
        kicker, title, desc, path, action, icon = card
        with col:
            st.markdown(f'<div class="panel"><div class="panel-kicker">{kicker}</div><h3>{icon} &nbsp;{title}</h3><p>{desc}</p></div>', unsafe_allow_html=True)
            st.page_link(path, label=action, icon="↗")

st.divider()
st.subheader("Recent interview activity")
if not rows:
    st.info("No interview sessions yet. Start a mock interview to populate your activity and analytics.")
else:
    for row in sorted(rows, key=lambda x: float(x.get("created_at", 0) or 0), reverse=True)[:5]:
        stamp = float(row.get("created_at", 0) or 0)
        created = time.strftime("%d %b %Y · %H:%M", time.localtime(stamp)) if stamp else "Date unavailable"
        score = row.get("overall_session_score")
        status = "Completed" if row.get("is_finished") else "In progress"
        a, b, c = st.columns([3, 2, 1])
        a.markdown(f"**{row.get('target_role', 'Interview practice')}**")
        a.caption(created)
        b.caption(f"{status} · {row.get('interview_type', 'General')} · {len(row.get('turns', []) or [])} questions")
        c.metric("Score", f"{float(score):.1f}/5" if score is not None else "—")

st.caption("Candidate profiles and history are currently stored in this browser's local storage. They are not cloud-synchronised across devices.")
