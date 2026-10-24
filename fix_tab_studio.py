"""
fix_tab_studio.py – Inserts the complete tab_studio body into app.py
between the end of the welcome screen (line 607) and the start of TAB 2 (line 608).
"""

STUDIO_BODY = '''
    elif session.is_finished:
        st.success("\\U0001f389 **Interview Round Completed!** Full diagnostic transcript compiled below.")

        valid_turns = [t for t in session.turns if t.turn_evaluation]
        if valid_turns:
            avg_score = round(sum(t.turn_evaluation.overall_score for t in valid_turns) / len(valid_turns), 1)
            session.overall_session_score = avg_score
            save_session(session)

            col_sc1, col_sc2, col_sc3 = st.columns([1, 1, 2])
            with col_sc1:
                st.metric("Overall Practice Score", f"{avg_score} / 5.0")
            with col_sc2:
                st.markdown("**Performance Mastery:**")
                st.markdown(get_performance_badge(avg_score), unsafe_allow_html=True)
            with col_sc3:
                st.markdown(f"**Round Overview:** Completed {len(valid_turns)} of {session.total_questions} questions for **{session.target_role}**.")

            st.markdown("### \\U0001f4dd Turn-by-Turn Diagnostic Review")
            for i, turn in enumerate(session.turns):
                t_eval = turn.turn_evaluation or turn.initial_evaluation
                score_str = f"{t_eval.overall_score}/5.0" if t_eval else "N/A"
                with st.expander(f"Question {i+1}: {turn.question.question_text[:75]}... (Score: {score_str})"):
                    st.markdown(f"**Question:** {turn.question.question_text}")
                    st.markdown(f"**Your Initial Answer:**\\n```\\n{turn.initial_answer}\\n```")
                    if turn.followup_question:
                        st.markdown(f"**Follow-Up Question:**\\n> *\\"{turn.followup_question}\\"*")
                        st.markdown(f"**Your Follow-Up Answer:**\\n```\\n{turn.followup_answer or 'N/A'}\\n```")
                    if t_eval:
                        if t_eval.technical_breakdown:
                            tb = t_eval.technical_breakdown
                            st.markdown("#### \\U0001f52c Technical Depth Telemetry")
                            col_t1, col_t2, col_t3 = st.columns(3)
                            with col_t1:
                                st.write("**Time Complexity:**", ", ".join(tb.get("time_complexity", [])) or "None explicit")
                            with col_t2:
                                st.write("**Concurrency:**", ", ".join(tb.get("concurrency_primitives", [])) or "None explicit")
                            with col_t3:
                                st.write("**Patterns:**", ", ".join(tb.get("architectural_patterns", [])) or "None explicit")
                        if t_eval.architecture_diagram_mermaid:
                            st.markdown("#### \\U0001f5fa\\ufe0f Architecture Diagram")
                            render_mermaid(t_eval.architecture_diagram_mermaid, height=240)
                        st.markdown("#### \\u2696\\ufe0f Rubric Breakdown")
                        cols_r = st.columns(4)
                        for idx, (k, r_crit) in enumerate(t_eval.rubric_scores.items()):
                            with cols_r[idx]:
                                st.metric(r_crit.display_name, f"{r_crit.score} / 5.0")
                                st.caption(r_crit.feedback)
                        st.markdown(t_eval.stronger_answer_outline)
        else:
            st.warning("Session completed without submitted responses.")

        if st.button("\\U0001f504 Start Fresh Practice Round"):
            st.session_state.session = None
            st.rerun()

    else:
        # ACTIVE INTERVIEW ROUND IN PROGRESS
        curr_idx = session.current_turn_index
        turn = session.turns[curr_idx]
        q_item = turn.question

        progress_val = curr_idx / session.total_questions
        st.progress(progress_val)
        col_p1, col_p2 = st.columns([3, 1])
        with col_p1:
            st.caption(f"Question {curr_idx + 1} of {session.total_questions} | {session.target_role} \\u2022 {session.experience_level}")
        with col_p2:
            st.markdown(f"<span class=\'tech-tag\'>{q_item.category.value.upper()}</span>", unsafe_allow_html=True)

        st.markdown(f"""
        <div class="animated-question-card">
            <span style="font-size:0.8rem; font-weight:700; text-transform:uppercase; color:#0284c7; letter-spacing:0.05em;">
                \\u26a1 Question {curr_idx + 1} \\u2022 Focus: {q_item.competency_or_topic}
            </span>
            <p style="font-size:1.26rem; font-weight:700; color:#000000; margin-top:8px; line-height:1.5;">
                {q_item.question_text}
            </p>
        </div>
        """, unsafe_allow_html=True)

        with st.expander("\\U0001f4a1 Technical Expectations & Evaluation Hints", expanded=False):
            st.markdown("**What Interviewers Look For:**")
            for h in q_item.rubric_hints:
                st.markdown(f"- {h}")
            if q_item.category == QuestionCategory.BEHAVIORAL:
                st.info("**STAR Framework:**\\n- **S:** Situation (15%)\\n- **T:** Task (10%)\\n- **A:** Action YOU took (60%)\\n- **R:** Result + metrics (15%)")
            elif q_item.category == QuestionCategory.TECHNICAL:
                st.info("**Technical Flow:**\\n1. Core definition\\n2. Internal mechanics & complexity\\n3. Real-world trade-offs\\n4. Concrete example from your codebase")
            else:
                st.info("**Project Flow:**\\n1. Problem & topology\\n2. Stack choices vs alternatives\\n3. Hardest bug YOU solved\\n4. Hindsight redesign")

        if not session.in_followup and not turn.completed:
            st.markdown("#### \\u270d\\ufe0f Type Your Response")
            user_input = st.text_area(
                "Your Answer:",
                value=turn.initial_answer,
                height=180,
                placeholder="State your answer clearly. Explain technical choices, complexity trade-offs, and use \'I\' to highlight your individual contribution...",
                key=f"ans_input_{curr_idx}",
            )
            word_count = len(user_input.strip().split()) if user_input.strip() else 0
            pacing_chip = get_word_pacing_chip(word_count)
            st.markdown(f"**Word Count:** `{word_count} words` {pacing_chip}", unsafe_allow_html=True)

            with st.expander("\\U0001f4bb Include Code Snippet (Optional)"):
                code_input = st.text_area(
                    "Code / Pseudocode:",
                    height=110,
                    placeholder="def solve(stream):\\n    cache = {}\\n    ...",
                    key=f"code_snippet_{curr_idx}",
                )

            col_sub1, col_sub2 = st.columns([1, 4])
            with col_sub1:
                if st.button("Submit Answer \\U0001f4ac", type="primary", use_container_width=True):
                    if not user_input.strip():
                        st.warning("Please type your response before submitting.")
                    else:
                        full_content = user_input.strip()
                        if code_input.strip():
                            full_content += f"\\n\\n[Code]:\\n```\\n{code_input.strip()}\\n```"
                        turn.initial_answer = full_content
                        with st.spinner("Analysing your answer and generating follow-up..."):
                            init_eval = evaluate_with_llm(
                                q_item,
                                turn.initial_answer,
                                candidate_context=session.candidate_context,
                                api_key=st.session_state.api_key or None,
                            )
                            turn.initial_evaluation = init_eval
                            if init_eval.suggested_followup_question:
                                turn.followup_question = init_eval.suggested_followup_question
                            session.in_followup = True
                            save_session(session)
                            st.rerun()

        elif session.in_followup and not turn.completed:
            with st.expander("\\U0001f4c4 Review Your Initial Response", expanded=False):
                st.markdown(turn.initial_answer)

            persona_name = st.session_state.interviewer_persona.split("\\u2014")[0].strip()
            st.markdown(f"""
            <div class="animated-followup-card">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <span style="font-size:0.8rem;font-weight:700;color:#38bdf8;text-transform:uppercase;letter-spacing:0.06em;">
                        \\u26a1 {persona_name}\'s Follow-Up Challenge
                    </span>
                    <span class="ai-online-badge">PROBING TRADE-OFFS</span>
                </div>
                <p style="font-size:1.22rem;font-weight:700;color:#ffffff;margin-top:8px;margin-bottom:0;line-height:1.5;">
                    \\"{turn.followup_question or q_item.default_followup}\\"
                </p>
            </div>
            """, unsafe_allow_html=True)

            followup_input = st.text_area(
                "Your Follow-Up Response:",
                value=turn.followup_answer,
                height=140,
                placeholder="Elaborate on failure modes, concurrency race conditions, or edge case trade-offs...",
                key=f"followup_input_{curr_idx}",
            )
            f_word_count = len(followup_input.strip().split()) if followup_input.strip() else 0
            st.caption(f"Follow-up length: {f_word_count} words")

            col_f1, col_f2 = st.columns([2, 1])
            with col_f1:
                if st.button("Submit Follow-Up & Score Turn \\U0001f3af", type="primary", use_container_width=True):
                    turn.followup_answer = followup_input.strip()
                    with st.spinner("Executing full 4-part rubric scoring..."):
                        full_eval = evaluate_with_llm(
                            q_item,
                            turn.initial_answer,
                            followup_answer=turn.followup_answer,
                            candidate_context=session.candidate_context,
                            api_key=st.session_state.api_key or None,
                        )
                        turn.turn_evaluation = full_eval
                        turn.completed = True
                        session.in_followup = False
                        save_session(session)
                        st.rerun()
            with col_f2:
                if st.button("Skip Follow-Up", use_container_width=True):
                    turn.followup_answer = "[Skipped]"
                    turn.turn_evaluation = turn.initial_evaluation
                    turn.completed = True
                    session.in_followup = False
                    save_session(session)
                    st.rerun()

        elif turn.completed and turn.turn_evaluation:
            t_eval = turn.turn_evaluation
            st.markdown("### \\U0001f4ca Turn Diagnostic Results")
            col_sc, col_badge = st.columns([1, 2])
            with col_sc:
                st.metric("Turn Practice Score", f"{t_eval.overall_score} / 5.0")
            with col_badge:
                st.markdown("**Mastery Level:**")
                st.markdown(get_performance_badge(t_eval.overall_score), unsafe_allow_html=True)

            if t_eval.technical_breakdown:
                tb = t_eval.technical_breakdown
                st.markdown("#### \\U0001f52c Technical Telemetry")
                col_m1, col_m2, col_m3 = st.columns(3)
                with col_m1:
                    time_comp = ", ".join(tb.get("time_complexity", [])) or "None detected"
                    st.markdown(f\'<div class="telemetry-card"><span style="color:#38bdf8;font-size:0.75rem;">TIME COMPLEXITY</span><h4 style="color:#fff;margin:6px 0;">{time_comp}</h4></div>\', unsafe_allow_html=True)
                with col_m2:
                    concurrency = ", ".join(tb.get("concurrency_primitives", [])) or "None detected"
                    st.markdown(f\'<div class="telemetry-card"><span style="color:#38bdf8;font-size:0.75rem;">CONCURRENCY</span><h4 style="color:#fff;margin:6px 0;">{concurrency}</h4></div>\', unsafe_allow_html=True)
                with col_m3:
                    patterns = ", ".join(tb.get("architectural_patterns", [])) or "None detected"
                    st.markdown(f\'<div class="telemetry-card"><span style="color:#38bdf8;font-size:0.75rem;">PATTERNS</span><h4 style="color:#fff;margin:6px 0;">{patterns}</h4></div>\', unsafe_allow_html=True)

            if t_eval.architecture_diagram_mermaid:
                st.markdown("#### \\U0001f5fa\\ufe0f Architecture Diagram")
                render_mermaid(t_eval.architecture_diagram_mermaid, height=260)

            st.markdown("#### \\u2696\\ufe0f Rubric Breakdown")
            cols_r = st.columns(4)
            for idx, (k, r_crit) in enumerate(t_eval.rubric_scores.items()):
                with cols_r[idx]:
                    st.metric(r_crit.display_name, f"{r_crit.score} / 5.0")
                    st.caption(r_crit.feedback)

            st.markdown(t_eval.stronger_answer_outline)

            st.markdown("---")
            is_last = (curr_idx + 1) >= session.total_questions
            btn_label = "Conclude Round & Export Report \\U0001f389" if is_last else "Next Question \\u27a1\\ufe0f"
            if st.button(btn_label, type="primary", use_container_width=True):
                if is_last:
                    session.is_finished = True
                    session.completed_at = time.time()
                    save_session(session)
                    st.rerun()
                else:
                    session.current_turn_index += 1
                    session.in_followup = False
                    save_session(session)
                    st.rerun()

'''

with open("app.py", "r") as f:
    lines = f.readlines()

# Insert after line 607 (0-indexed: 607), which is "        st.markdown("---")\n"
# That is the last line of the "if session is None:" block.
insert_at = 607   # 0-indexed

new_lines = lines[:insert_at + 1] + [STUDIO_BODY + "\n"] + lines[insert_at + 1:]

with open("app.py", "w") as f:
    f.writelines(new_lines)

print(f"Inserted studio body after line {insert_at + 1}. New total lines: {len(new_lines)}")
