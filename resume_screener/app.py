"""
app.py — AI Resume Screening System (Streamlit UI)

Run locally with:
    streamlit run app.py

Then open the local URL Streamlit prints (usually http://localhost:8501).
"""
import io
import pandas as pd
import streamlit as st

from parser import extract_text
from matcher import ResumeMatcher

st.set_page_config(page_title="AI Resume Screener", page_icon="📄", layout="wide")

st.title("📄 AI Resume Screening System")
st.caption(
    "Rank resumes against a job description using skill matching, keyword "
    "(TF-IDF) analysis, and experience matching — 100% local, no API calls."
)

with st.sidebar:
    st.header("⚙️ Scoring Weights")
    st.caption("Adjust how much each signal contributes to the overall score.")
    skill_w = st.slider("Skill Match weight", 0.0, 1.0, 0.50, 0.05)
    keyword_w = st.slider("Keyword/TF-IDF weight", 0.0, 1.0, 0.35, 0.05)
    exp_w = st.slider("Experience weight", 0.0, 1.0, 0.15, 0.05)
    total_w = skill_w + keyword_w + exp_w
    if abs(total_w - 1.0) > 1e-6:
        st.warning(f"Weights sum to {total_w:.2f}, they will be normalized to 1.0.")
        if total_w > 0:
            skill_w, keyword_w, exp_w = (w / total_w for w in (skill_w, keyword_w, exp_w))

    st.divider()
    st.header("📊 About the scores")
    st.markdown(
        "- **Skill Match** — % of skills mentioned in the JD (from a built-in "
        "skills dictionary) that also appear in the resume.\n"
        "- **Keyword Match** — TF-IDF cosine similarity between the full JD "
        "and resume text, catching relevant terms outside the skills list.\n"
        "- **Experience Match** — compares years of experience mentioned in "
        "the resume vs. the years required in the JD."
    )

col1, col2 = st.columns(2)

with col1:
    st.subheader("1️⃣ Job Description")
    jd_input_mode = st.radio("Input method", ["Paste text", "Upload file"], horizontal=True, key="jd_mode")
    jd_text = ""
    if jd_input_mode == "Paste text":
        jd_text = st.text_area("Paste the job description here", height=280, placeholder="e.g. We are looking for a Senior Python Developer with 5+ years of experience...")
    else:
        jd_file = st.file_uploader("Upload job description (.pdf, .docx, .txt)", type=["pdf", "docx", "txt"], key="jd_file")
        if jd_file is not None:
            jd_text = extract_text(jd_file, filename=jd_file.name)
            st.text_area("Extracted JD text (preview)", value=jd_text, height=200, disabled=True)

with col2:
    st.subheader("2️⃣ Resumes")
    resume_files = st.file_uploader(
        "Upload one or more resumes (.pdf, .docx, .txt)",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
    )
    if resume_files:
        st.success(f"{len(resume_files)} resume(s) uploaded.")

run_button = st.button("🚀 Rank Resumes", type="primary", use_container_width=True)

if run_button:
    if not jd_text or not jd_text.strip():
        st.error("Please provide a job description first.")
    elif not resume_files:
        st.error("Please upload at least one resume.")
    else:
        with st.spinner("Parsing resumes and computing scores..."):
            resumes = {}
            parse_errors = []
            for f in resume_files:
                try:
                    resumes[f.name] = extract_text(f, filename=f.name)
                except Exception as e:
                    parse_errors.append(f"{f.name}: {e}")

            if parse_errors:
                st.warning("Some files could not be parsed:\n" + "\n".join(parse_errors))

            matcher = ResumeMatcher(skill_weight=skill_w, keyword_weight=keyword_w, experience_weight=exp_w)
            results = matcher.rank_resumes(jd_text, resumes)

        st.success(f"Ranked {len(results)} resume(s).")

        # Summary table
        table_rows = []
        for r in results:
            table_rows.append({
                "Rank": r["rank"],
                "Resume": r["resume_name"],
                "Overall Score": r["overall_score"],
                "Skill Match %": r["skill_score"],
                "Keyword Match %": r["keyword_score"],
                "Experience Match %": r["experience_score"],
                "Years Found": r["resume_years"],
                "Matched Skills": ", ".join(r["matched_skills"]) or "—",
                "Missing Skills": ", ".join(r["missing_skills"]) or "—",
            })
        df = pd.DataFrame(table_rows)

        st.subheader("🏆 Ranking Results")
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Overall Score": st.column_config.ProgressColumn(
                    "Overall Score", min_value=0, max_value=100, format="%.1f"
                ),
            },
        )

        st.subheader("📈 Score Comparison")
        chart_df = df.set_index("Resume")[["Overall Score", "Skill Match %", "Keyword Match %", "Experience Match %"]]
        st.bar_chart(chart_df["Overall Score"])

        # Download CSV
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        st.download_button(
            "⬇️ Download Full Report (CSV)",
            data=csv_buffer.getvalue(),
            file_name="resume_ranking_report.csv",
            mime="text/csv",
        )

        st.divider()
        st.subheader("🔍 Candidate Details")
        for r in results:
            with st.expander(f"#{r['rank']} — {r['resume_name']}  (Score: {r['overall_score']})"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Skill Match", f"{r['skill_score']}%")
                c2.metric("Keyword Match", f"{r['keyword_score']}%")
                c3.metric("Experience Match", f"{r['experience_score']}%")
                st.markdown(f"**Years of experience found in resume:** {r['resume_years']}  |  **Years required in JD:** {r['jd_years_required'] or 'not specified'}")
                st.markdown(f"**✅ Matched skills ({len(r['matched_skills'])}):** {', '.join(r['matched_skills']) or 'None'}")
                st.markdown(f"**❌ Missing skills ({len(r['missing_skills'])}):** {', '.join(r['missing_skills']) or 'None'}")
else:
    st.info("👆 Provide a job description and upload resumes, then click **Rank Resumes**.")
