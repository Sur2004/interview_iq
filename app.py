"""InterviewIQ — lightweight, reliable demo build.

This entry point intentionally uses only Streamlit's built-in widgets and Python's
standard library. It avoids optional AI/network calls, browser components, and
large imports so every section opens quickly for a project demonstration.
The previous full app is preserved as app_full.py.
"""
import streamlit as st
from datetime import datetime

st.set_page_config(
    page_title="InterviewIQ | Demo",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
:root { color-scheme: light; }
.block-container { max-width: 1100px; padding-top: 1.6rem; padding-bottom: 2.5rem; }
[data-testid="stSidebar"] { border-right: 1px solid #e5e7eb; }
.hero { padding: 1.5rem 1.7rem; border: 1px solid #e5e7eb; border-radius: 16px;
        background: linear-gradient(135deg,#f8fbff,#ffffff); margin-bottom: 1.2rem; }
.hero h1 { margin: 0 0 .35rem 0; color: #172033; }
.hero p { color: #667085; margin: 0; }
.small-note { color: #667085; font-size: .9rem; }
div[data-testid="stMetric"] { border: 1px solid #e5e7eb; border-radius: 12px; padding: 12px; }
</style>
""", unsafe_allow_html=True)

SECTIONS = [
    "Home",
    "Mock Interview",
    "Resume Review",
    "Projects",
    "Question Bank",
    "System Design",
    "STAR Story Builder",
    "Spot the Flaw",
    "Progress",
    "Reports",
    "About",
]

with st.sidebar:
    st.title("🎯 InterviewIQ")
    st.caption("Simple project demo")
    section = st.radio("Navigate", SECTIONS, index=0, key="demo_section")
    st.divider()
    st.caption("Demo mode · No API key or sign-in required")
    st.caption("Use the navigation above to open each section.")

st.markdown("""
<div class="hero">
  <h1>InterviewIQ</h1>
  <p>Practice interviews, explore project feedback, and prepare clear, confident answers.</p>
</div>
""", unsafe_allow_html=True)

def section_title(title, description):
    st.header(title)
    st.write(description)

if section == "Home":
    section_title("Welcome", "A lightweight, click-through demonstration of the InterviewIQ project.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Practice modes", "3")
    c2.metric("Learning sections", "4")
    c3.metric("Setup required", "None")
    st.subheader("What you can explore")
    cards = [
        ("Mock Interview", "Answer a sample question and receive simple practice feedback."),
        ("Resume Review", "See a sample resume checklist and areas to improve."),
        ("Projects", "Review example project summaries and talking points."),
        ("Question Bank", "Browse common technical and behavioral questions."),
        ("System Design", "Follow a basic system-design discussion structure."),
        ("Reports", "View a sample report summary for demonstration."),
    ]
    cols = st.columns(2)
    for i, (title, desc) in enumerate(cards):
        with cols[i % 2]:
            with st.container(border=True):
                st.subheader(title)
                st.write(desc)
    st.info("This demo prioritizes reliable navigation and fast loading. AI/API integrations are intentionally not required.")

elif section == "Mock Interview":
    section_title("Mock Interview", "Try a sample interview flow. Feedback is a basic demonstration, not an AI or hiring assessment.")
    role = st.selectbox("Target role", ["Software Engineer", "Data Analyst", "Machine Learning Intern", "Cybersecurity Intern"])
    question = st.selectbox("Sample question", [
        "Tell me about yourself.",
        "Explain a project you built and your contribution.",
        "How would you debug a slow application?",
        "Describe a difficult problem and how you solved it.",
    ])
    answer = st.text_area("Your answer", placeholder="Type your answer here…", height=180, key="demo_answer")
    if st.button("Review my answer", type="primary"):
        if len(answer.strip()) < 20:
            st.warning("Add a little more detail. Try explaining the context, your action, and the result.")
        else:
            st.success("Sample review completed.")
            st.write(f"**Role:** {role}")
            st.write(f"**Question:** {question}")
            st.write(f"**Answer length:** {len(answer.split())} words")
            st.markdown("**Practice tips**")
            st.write("- Start with a direct answer.")
            st.write("- Include a specific example and explain your personal contribution.")
            st.write("- Finish with the result or what you learned.")
            st.caption("Feedback is rule-based demo guidance; it does not call an external AI service.")

elif section == "Resume Review":
    section_title("Resume Review", "Use this quick checklist to demonstrate the resume-review section.")
    st.write("A strong resume should be easy to scan and supported by clear evidence.")
    checks = [
        "Contact details and professional links are correct",
        "Summary is concise and tailored to the target role",
        "Projects explain the problem, approach, tools, and outcome",
        "Skills listed can be explained in an interview",
        "Dates, formatting, spelling, and links are consistent",
    ]
    completed = 0
    for item in checks:
        if st.checkbox(item, key="resume_" + item[:12]):
            completed += 1
    st.progress(completed / len(checks))
    st.caption(f"{completed} of {len(checks)} checklist items reviewed.")
    st.info("For this presentation build, resume review is a checklist demo. File parsing and external ATS services are not enabled.")

elif section == "Projects":
    section_title("Projects", "Sample project cards for explaining technical work during an interview.")
    projects = [
        ("InterviewIQ", "Interview practice platform", "Python, Streamlit", "Guided practice questions, structured answer tips, and section-based navigation."),
        ("Smart Grid Monitoring", "Energy monitoring demo", "Flask, SQLite, Chart.js", "Simulated grid readings, outage indicators, and simple monitoring dashboards."),
        ("Carnatic Raga Identification", "Music classification prototype", "Python, librosa, scikit-learn", "Audio feature extraction and a baseline model for raga classification."),
    ]
    for name, subtitle, stack, summary in projects:
        with st.container(border=True):
            st.subheader(name)
            st.caption(subtitle + " · " + stack)
            st.write(summary)
            st.markdown("**Explain in an interview:** problem → your role → approach → result → next improvement.")

elif section == "Question Bank":
    section_title("Question Bank", "Browse a small set of common questions.")
    bank = {
        "Python": ["What is the difference between a list and a tuple?", "What are decorators?", "How do exceptions work?"],
        "SQL and Data": ["Explain INNER JOIN vs LEFT JOIN.", "What is normalization?", "How would you handle missing values?"],
        "Machine Learning": ["What is overfitting?", "Why use train/test split?", "Explain precision and recall."],
        "Behavioral": ["Tell me about a challenge you faced.", "Describe a time you worked in a team.", "What would you improve in a past project?"],
    }
    topic = st.selectbox("Choose topic", list(bank.keys()))
    for i, q in enumerate(bank[topic], 1):
        with st.expander(f"{i}. {q}"):
            st.write("Build your answer with a clear explanation, one example, and the trade-offs or result.")

elif section == "System Design":
    section_title("System Design", "A simple structure for explaining a design clearly.")
    steps = [
        ("1. Clarify requirements", "Identify users, core features, constraints, and success criteria."),
        ("2. Estimate scale", "Discuss request volume, data size, latency, and availability."),
        ("3. Sketch components", "Show client, API, business logic, database, cache, and background jobs as needed."),
        ("4. Explain data flow", "Walk through one typical request end to end."),
        ("5. Discuss trade-offs", "Cover bottlenecks, failure handling, security, monitoring, and future scaling."),
    ]
    for title, detail in steps:
        st.markdown(f"**{title}**")
        st.write(detail)

elif section == "STAR Story Builder":
    section_title("STAR Story Builder", "Draft a behavioral interview answer using Situation, Task, Action, and Result.")
    situation = st.text_area("Situation", placeholder="What was happening?")
    task = st.text_area("Task", placeholder="What were you responsible for?")
    action = st.text_area("Action", placeholder="What did you personally do?")
    result = st.text_area("Result", placeholder="What changed or what did you learn?")
    if st.button("Build STAR answer"):
        if not any([situation.strip(), task.strip(), action.strip(), result.strip()]):
            st.warning("Add at least one detail to build your draft.")
        else:
            st.subheader("Your STAR draft")
            st.markdown(f"**Situation:** {situation or 'Add details.'}\n\n**Task:** {task or 'Add details.'}\n\n**Action:** {action or 'Add details.'}\n\n**Result:** {result or 'Add details.'}")

elif section == "Spot the Flaw":
    section_title("Spot the Flaw", "Choose the stronger interview statement.")
    choice = st.radio("Which answer is more convincing?", [
        "I helped improve the project a lot.",
        "I implemented input validation, added tests for edge cases, and documented the changes.",
    ])
    if st.button("Check answer"):
        if choice.startswith("I implemented"):
            st.success("Correct. It describes specific actions and evidence.")
        else:
            st.info("Try to describe what you personally did and provide concrete evidence.")

elif section == "Progress":
    section_title("Progress", "A small local demo tracker. These values are only for this running app session.")
    if "demo_practice_count" not in st.session_state:
        st.session_state.demo_practice_count = 0
    st.metric("Practice reviews completed", st.session_state.demo_practice_count)
    if st.button("Add a demo practice session"):
        st.session_state.demo_practice_count += 1
        st.rerun()
    st.caption("This lightweight demo does not store personal data in a server database.")

elif section == "Reports":
    section_title("Reports", "Example summary for demonstrating the report section.")
    st.write("**Sample practice report**")
    st.write("- Focus: clarity, structure, evidence, and relevance")
    st.write("- Suggested next step: practise one technical and one behavioral question")
    st.write("- Reminder: practice feedback is educational and is not a hiring prediction")
    report = "# InterviewIQ Demo Report\n\n- Focus: clarity, structure, evidence, relevance\n- Next step: practise one technical and one behavioral question\n"
    st.download_button("Download sample report (.md)", report, file_name="interviewiq_demo_report.md", mime="text/markdown")

else:
    section_title("About InterviewIQ", "InterviewIQ is a student project concept for guided interview practice.")
    st.markdown("""
**Project goals**
- Help candidates practise technical and behavioral interview answers.
- Encourage structured explanations grounded in real experience.
- Offer a simple interface that is easy to navigate during a live demonstration.

**Demo technology:** Python and Streamlit.

**Current demo scope:** navigation, sample interactions, static learning content, and a downloadable sample report. Live AI evaluation, authentication, camera monitoring, and cloud history are intentionally disabled in this lightweight build.
""")

st.divider()
st.caption(f"InterviewIQ demo · {datetime.now().strftime('%d %b %Y')} · Built for demonstration and navigation reliability")
