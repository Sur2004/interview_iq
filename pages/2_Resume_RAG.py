from __future__ import annotations

import streamlit as st

from backend.resume_rag import ingest_resume, compare_resume_to_job
from backend.rag_store import init_rag_database, list_resumes

st.set_page_config(page_title="InterviewIQ | Resume Intelligence", page_icon="📄", layout="wide")
st.title("Resume Intelligence")
st.caption("PostgreSQL + pgvector retrieval-augmented analysis. Resume evidence is retrieved before comparison; missing evidence is not proof that a candidate lacks a skill.")

try:
    init_rag_database()
    resumes = list_resumes()
except Exception as exc:
    st.error("The resume database is not available. Start the app with Docker Compose and check the database service.")
    st.code(str(exc))
    st.stop()

upload_tab, compare_tab = st.tabs(["Upload & index resume", "Compare with job description"])

with upload_tab:
    st.subheader("Build a searchable resume profile")
    candidate_name = st.text_input("Candidate name", max_chars=120)
    uploaded = st.file_uploader("Upload text-based PDF resume", type=["pdf"])
    if st.button("Extract, embed and save resume", type="primary", disabled=not (candidate_name.strip() and uploaded)):
        with st.spinner("Extracting resume text and creating semantic embeddings. The first run may download the embedding model."):
            try:
                resume_id = ingest_resume(candidate_name, uploaded.name, uploaded)
                st.success("Resume indexed successfully.")
                st.code(resume_id)
                st.rerun()
            except Exception as exc:
                st.error(str(exc))

with compare_tab:
    st.subheader("Compare resume evidence against a role")
    if not resumes:
        st.info("Upload a resume first.")
    else:
        labels = {f"{r['candidate_name']} — {r['filename']} — {r['created_at'].strftime('%Y-%m-%d %H:%M')}": r["id"] for r in resumes}
        selected = st.selectbox("Choose indexed resume", list(labels))
        job_description = st.text_area("Paste the job description / requirements", height=220, placeholder="Required skills, responsibilities, qualifications...")
        if st.button("Retrieve evidence and compare", type="primary", disabled=not job_description.strip()):
            with st.spinner("Retrieving the most relevant resume passages for each job requirement..."):
                try:
                    results = compare_resume_to_job(labels[selected], job_description)
                    for item in results:
                        st.markdown(f"**Requirement:** {item['requirement']}")
                        if not item["matches"]:
                            st.warning("No matching passage retrieved.")
                            continue
                        for match in item["matches"]:
                            st.write(f"**{match['section']} · semantic similarity {match['similarity']:.2f}**")
                            st.write(match["content"])
                        st.divider()
                    st.caption("Similarity is a retrieval signal, not an ATS score or hiring probability. Review the quoted evidence and decide whether it genuinely demonstrates each requirement.")
                except Exception as exc:
                    st.error(str(exc))
