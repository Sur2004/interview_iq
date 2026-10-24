"""
Script: rebuild_sidebar.py
Replaces lines 326..780 (0-indexed 326..780) in app.py with the clean sidebar + hero + tabs block.
"""

NEW_BLOCK = '''
# ==============================================================================
# SIDEBAR CONTROLS  (single clean block – no duplicates)
# ==============================================================================
with st.sidebar:
    st.markdown("""
    <div style="background:linear-gradient(135deg,#000,#03182e);border:1.5px solid #0ea5e9;
         border-radius:12px;padding:14px 16px;margin-bottom:12px;">
        <div style="font-size:1.35rem;font-weight:800;color:#fff;letter-spacing:-0.01em;">
            \\U0001f3af InterviewIQ Studio
        </div>
        <div style="font-size:0.82rem;color:#bae6fd;margin-top:4px;">
            Technical &amp; Behavioural Interview Practice Platform
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("\\u2699\\ufe0f Session Setup")

    candidate_name = st.text_input(
        "Your Name",
        value="Student Candidate",
        help="Personalises practice reports and rubric summaries.",
        key="sb_candidate_name",
    )

    target_role = st.selectbox(
        "\\U0001f3ad Target Role",
        [r.value for r in TargetRole],
        index=0,
        help="Sets technical depth, domain questions and rubric expectations.",
        key="sb_target_role",
    )

    experience_level = st.selectbox(
        "\\U0001f4c8 Experience Level",
        [e.value for e in ExperienceLevel],
        index=0,
        help="Tailors question difficulty and scoring criteria.",
        key="sb_experience_level",
    )

    interview_type = st.selectbox(
        "\\U0001f5c2\\ufe0f Interview Type",
        [t.value for t in InterviewType],
        index=0,
        help="Comprehensive Mix, Technical Deep-Dive, Behavioural, or Architecture.",
        key="sb_interview_type",
    )

    interviewer_persona = st.selectbox(
        "\\U0001f935 Interviewer Persona",
        [
            "Jordan — Principal Architect (Scale & Failure Modes)",
            "Alex — Staff Engineer (Algorithms & Clean Code)",
            "Taylor — VP Engineering (Vision & Culture Fit)",
        ],
        index=0,
        help="Shapes tone and technical rigour of follow-up questions.",
        key="sb_interviewer_persona",
    )
    st.session_state.interviewer_persona = interviewer_persona

    num_questions = st.slider(
        "\\U0001f522 Questions in Round",
        min_value=5,
        max_value=8,
        value=6,
        help="5-8 questions to simulate a 45-minute technical loop.",
        key="sb_num_questions",
    )

    candidate_context = st.text_area(
        "\\U0001f4dd Your Projects / Coursework (Optional)",
        placeholder=(
            "e.g. Distributed KV-Store in Go; Virtual Memory Manager in C; "
            "React & PostgreSQL e-commerce; PyTorch RAG pipeline..."
        ),
        help="Grounds AI feedback in your real background - no fabrication.",
        height=90,
        key="sb_candidate_context",
    )

    st.markdown("---")
    llm_conf = get_llm_config()
    secret_val = validate_secrets()

    with st.expander("\\U0001f511 LLM Provider & API Key", expanded=False):
        st.caption(f"Status: {secret_val[\'message\']}")
        provider_opts = [
            "Auto (via .env / Secrets)",
            "Groq Cloud — Llama 3.3 70B",
            "Google Gemini 1.5 Flash",
            "OpenAI GPT-4o Mini",
            "Built-In Offline Engine",
        ]
        chosen_provider = st.selectbox(
            "Provider",
            provider_opts,
            index=0,
            help="Keys live in .env locally or Streamlit Secrets on Cloud.",
            key="sb_provider",
        )
        manual_key = st.text_input(
            "API Key Override",
            value="",
            type="password",
            placeholder="Paste key to override...",
            help="Never committed or logged.",
            key="sb_manual_key",
        )
        if manual_key:
            st.session_state.api_key = manual_key

    st.markdown("---")
    if st.button("\\U0001f680 Start Interview Round", type="primary", use_container_width=True):
        questions = build_interview_plan(
            target_role=target_role,
            experience_level=experience_level,
            interview_type=interview_type,
            num_questions=num_questions,
        )
        turns = [
            InterviewTurn(
                question_index=i,
                question=q,
                followup_question=q.default_followup,
            )
            for i, q in enumerate(questions)
        ]
        new_sess = InterviewSession(
            session_id=str(uuid.uuid4())[:8],
            candidate_name=candidate_name.strip() or "Student Candidate",
            target_role=target_role,
            experience_level=experience_level,
            interview_type=interview_type,
            total_questions=len(questions),
            candidate_context=candidate_context.strip(),
            turns=turns,
            current_turn_index=0,
            in_followup=False,
            is_finished=False,
        )
        st.session_state.session = new_sess
        save_session(new_sess)
        st.success(f"\\u2705 Round started - {len(questions)} questions queued!")
        st.rerun()

    if st.session_state.session and not st.session_state.session.is_finished:
        st.markdown("---")
        if st.button("\\u23f9\\ufe0f End Session Early", use_container_width=True):
            st.session_state.session.is_finished = True
            st.session_state.session.completed_at = time.time()
            save_session(st.session_state.session)
            st.rerun()

    st.markdown("---")
    st.page_link("pages/1_History.py", label="\\U0001f4da History & Performance", icon="\\U0001f4ca")


# ==============================================================================
# HERO HEADER BANNER  (sky-blue / white / black)
# ==============================================================================
st.markdown("""
<div class="hero-banner-sky">
    <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:16px;">
        <div>
            <div class="hero-title">\\U0001f3af InterviewIQ — Practice. Diagnose. Improve.</div>
            <div class="hero-subtitle">
                Repeatable mock interview rounds with Big-O complexity telemetry,
                contextual follow-up probing &amp; a transparent 4-part rubric.
                Built for students targeting their first or next engineering role.
            </div>
        </div>
        <div style="text-align:right;white-space:nowrap;">
            <span class="ai-online-badge">\\u25cf LIVE</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Dynamic Role Selector Cards
roles_meta = [
    ("\\U0001f4bb", "Software Engineering", "#0ea5e9"),
    ("\\U0001f3a8", "Frontend / UI", "#6366f1"),
    ("\\U0001f4ca", "Data Science & ML", "#10b981"),
    ("\\U0001f916", "AI / LLM Engineering", "#f59e0b"),
    ("\\U0001f512", "Cybersecurity", "#ef4444"),
    ("\\U0001f680", "DevOps / Platform", "#8b5cf6"),
    ("\\U0001f4e6", "Product Management", "#ec4899"),
]
role_cols = st.columns(len(roles_meta))
for col, (icon, label, color) in zip(role_cols, roles_meta):
    with col:
        st.markdown(f"""
        <div style="background:#000;border:1.5px solid {color};border-radius:10px;
                    padding:10px 6px;text-align:center;
                    box-shadow:0 0 10px {color}44;margin-bottom:6px;">
            <div style="font-size:1.4rem;">{icon}</div>
            <div style="font-size:0.72rem;font-weight:700;color:{color};
                        margin-top:4px;line-height:1.2;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown(
    f\'<div class="notice-card-sky"><strong>\\u2139\\ufe0f Rubric Notice:</strong> {RUBRIC_DISCLAIMER}</div>\',
    unsafe_allow_html=True,
)
st.markdown(
    f\'<div class="ethics-card-sky"><strong>\\U0001f6e1\\ufe0f Anti-Fabrication:</strong> {ETHICAL_OUTLINE_GUIDELINE}</div>\',
    unsafe_allow_html=True,
)


# ==============================================================================
# MAIN NAVIGATION TABS
# ==============================================================================
tab_studio, tab_dynamic_ai, tab_flaw_game, tab_star_builder, tab_bank, tab_playbook, tab_analytics, tab_report, tab_rubric = st.tabs([
    "\\U0001f3af Mock Interview Studio",
    "\\u26a1 Technical Generator",
    "\\U0001f3ae Spot the Flaw",
    "\\U0001f6e0\\ufe0f STAR Builder",
    "\\U0001f4da Question Bank",
    "\\U0001f4d6 Design Playbooks",
    "\\U0001f4ca Practice Analytics",
    "\\U0001f4d1 Export Report",
    "\\u2696\\ufe0f Rubric Guide",
])
'''

with open('app.py', 'r') as f:
    lines = f.readlines()

# Keep everything before line 327 (index 326) and after line 780 (index 780)
before = lines[:326]   # lines 1..326
after  = lines[780:]   # lines 781..end

new_lines = before + [NEW_BLOCK] + after

with open('app.py', 'w') as f:
    f.writelines(new_lines)

print("Done. Total lines now:", len(new_lines))
