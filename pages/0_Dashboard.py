"""InterviewIQ candidate dashboard."""
import time
import streamlit as st

st.set_page_config(page_title="InterviewIQ | Dashboard", page_icon="⚡", layout="wide")
st.markdown("""
<style>
.block-container{max-width:1220px;padding-top:2rem}
.hero{padding:32px;border-radius:22px;background:linear-gradient(125deg,#101a35,#243f82 68%,#4776d5);color:#fff;margin-bottom:22px;box-shadow:0 16px 40px rgba(20,38,86,.14)}
.hero h1{font-size:2.4rem;letter-spacing:-.05em;margin:0}
.hero p{color:#dbe5ff;font-size:1rem;margin:.55rem 0 0}
.eyebrow{font-size:.74rem;font-weight:800;letter-spacing:.13em;color:#b9ceff}
.tile{border:1px solid #e4e9f2;border-radius:17px;padding:20px;background:linear-gradient(145deg,#fff,#f7f9ff);min-height:150px;box-shadow:0 5px 18px rgba(16,24,40,.035)}
.tile h3{font-size:1.05rem;margin:.2rem 0 .45rem;color:#172033}
.tile p{color:#667085;font-size:.9rem;line-height:1.5}
.big{font-size:1.9rem;font-weight:800;letter-spacing:-.04em;color:#172033}
[data-testid="stMetric"]{border:1px solid #e4e9f2;border-radius:14px;padding:15px;background:#fff}
</style>
""",unsafe_allow_html=True)
st.markdown('<div class="hero"><div class="eyebrow">YOUR INTERVIEW WORKSPACE</div><h1>Prepare with purpose.</h1><p>Practice, review your progress, and understand exactly how InterviewIQ evaluates your answers.</p></div>',unsafe_allow_html=True)

candidate_id=st.session_state.get("authenticated_candidate_id") or st.session_state.get("authenticated_email")
if not candidate_id or candidate_id=="local_guest":
    st.warning("Sign in or create a Candidate ID from the main InterviewIQ page to load your personal dashboard.")
    st.page_link("app.py",label="Open InterviewIQ sign in",icon="🔐")
    st.stop()

data=st.session_state.get("browser_data",{"profiles":{},"sessions":{}})
profile=data.get("profiles",{}).get(candidate_id,{})
rows=data.get("sessions",{}).get(candidate_id,[])
completed=[x for x in rows if x.get("is_finished")]
scores=[float(x["overall_session_score"]) for x in completed if x.get("overall_session_score") is not None]
avg=round(sum(scores)/len(scores),1) if scores else 0
best=max(scores) if scores else 0
name=profile.get("name","Candidate")
st.markdown("### Welcome back, "+name)
m1,m2,m3,m4=st.columns(4)
m1.metric("Practice sessions",len(rows))
m2.metric("Completed rounds",len(completed))
m3.metric("Average score",f"{avg:.1f} / 5" if scores else "—")
m4.metric("Personal best",f"{best:.1f} / 5" if scores else "—")

st.markdown("### Your workspace")
cols=st.columns(2)
tiles=[
("🎯","Mock interview","Run a realistic interview with role-specific questions, follow-ups and structured feedback.","app.py"),
("📈","History & performance","Review score trends, rubric strengths and completed sessions.","pages/1_History.py"),
("🧭","System architecture","Explore the end-to-end workflow, JSON payloads, API formats and model tokens.","pages/2_System_Architecture.py"),
("📄","Resume & project review","Review your resume and project materials with structured feedback.","app.py"),
]
for i,(icon,title,desc,path) in enumerate(tiles):
    with cols[i%2]:
        st.markdown(f'<div class="tile"><div style="font-size:1.5rem">{icon}</div><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
        st.page_link(path,label="Open "+title,icon="↗")

st.markdown("### Recent activity")
if not rows:
    st.info("No interview sessions yet. Start your first mock interview to build your progress history.")
else:
    for row in sorted(rows,key=lambda x:float(x.get("created_at",0) or 0),reverse=True)[:5]:
        stamp=float(row.get("created_at",0) or 0)
        date=time.strftime("%d %b %Y",time.localtime(stamp)) if stamp else "Date unavailable"
        score=row.get("overall_session_score")
        status="Completed" if row.get("is_finished") else "In progress"
        left,right=st.columns([4,1])
        left.markdown(f"**{date} · {row.get('target_role','Practice')}**")
        left.caption(f"{status} · {row.get('interview_type','')} · {len(row.get('turns',[]) or [])} questions")
        right.metric("Score",f"{float(score):.1f}/5" if score is not None else "—")

st.caption("Your candidate profile and interview history currently live in this browser's localStorage. They do not automatically sync to another device.")
