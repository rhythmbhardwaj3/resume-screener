# AI Resume Screening System

Rank resumes against a job description using **skill matching**, **keyword (TF-IDF)
analysis**, and **experience matching** — entirely locally, no external API keys
or internet connection required at run time.

## How it scores resumes

Each resume gets an **Overall Score (0–100)** made of three parts:

| Signal | Default Weight | What it measures |
|---|---|---|
| **Skill Match** | 50% | % of skills detected in the job description (from a 100+ skill dictionary covering languages, frameworks, cloud/devops, data science, soft skills, etc.) that are also found in the resume. |
| **Keyword Match (TF-IDF)** | 35% | Cosine similarity between the full JD text and resume text, catching relevant terms/phrases outside the fixed skill list. |
| **Experience Match** | 15% | Compares years of experience mentioned in the resume vs. years required in the JD (if stated). |

Weights are adjustable in the sidebar of the web app, or in code via
`ResumeMatcher(skill_weight=..., keyword_weight=..., experience_weight=...)`.

## Setup

1. **Install Python 3.9+** if you don't already have it.
2. Open a terminal in this folder and install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Option A: Custom Web Frontend (recommended)

A standalone HTML/CSS/JS frontend backed by a local Flask API — no Streamlit
required.

```bash
python server.py
```

Then open **http://localhost:5000** in your browser. You can:
- Paste or drag-and-drop a job description (.pdf / .docx / .txt)
- Drag-and-drop multiple resumes (.pdf / .docx / .txt)
- Adjust scoring weights live (optional, under "Adjust scoring weights")
- Click **Screen Candidates** to see each resume as a ranked "case card" with
  a match-grade stamp (Strong Match / Review / Weak Match), score meters,
  matched/missing skill tags, and a downloadable CSV report.

Everything runs locally — the browser talks only to `localhost:5000`.

## Option B: Streamlit App

A simpler alternative UI, if you prefer Streamlit's built-in components:

```bash
streamlit run app.py
```

This opens a local browser tab (usually `http://localhost:8501`) with the same
core features: paste/upload a JD, upload resumes, rank, and download a CSV.

## Option C: Command Line (for batch processing)

Put all resumes to screen into one folder, then run:

```bash
python cli.py --jd sample_data/job_description.txt --resumes sample_data/resumes --output ranking_report.csv
```

Arguments:
- `--jd` — path to the job description file (.pdf/.docx/.txt)
- `--resumes` — path to a folder containing resume files (.pdf/.docx/.txt)
- `--output` — (optional) where to save the CSV report (default: `ranking_report.csv`)
- `--top` — (optional) only print the top N results to the console

## Try it with the included sample data

The `sample_data/` folder has a sample job description and two sample resumes
(one strong match, one weak match) so you can test the system immediately:

```bash
python cli.py --jd sample_data/job_description.txt --resumes sample_data/resumes
```

or upload those same files in the web app.

## Customizing the skills dictionary

Edit `skills_database.py` to add/remove skills or aliases relevant to your
industry or role. It's organized by category (Programming Languages, Web
Frameworks, Databases, Cloud & DevOps, Data Science & ML, Project Management,
Testing & QA, Soft Skills, Mobile). Each entry looks like:

```python
"python": ["python", "py"],
```

The key is the canonical skill name shown in results; the list contains all
text variants that should count as a match.

## Project structure

```
resume_screener/
├── server.py               # Flask backend + serves the custom frontend (recommended)
├── frontend/                # Custom HTML/CSS/JS UI ("case file" design)
│   ├── index.html
│   ├── styles.css
│   └── script.js
├── app.py                   # Alternative Streamlit web UI
├── cli.py                   # Command-line interface
├── matcher.py                # Scoring engine (skill/keyword/experience)
├── parser.py                  # PDF/DOCX/TXT text extraction
├── skills_database.py        # Skill dictionary used for skill matching
├── requirements.txt
├── sample_data/              # Sample JD + resumes for testing
└── README.md
```

## Notes & limitations

- Skill matching relies on the built-in dictionary — extend it for niche or
  emerging skills not yet included.
- Years-of-experience extraction is a simple regex heuristic (looks for
  patterns like "5 years", "5+ yrs") and may not catch every resume format.
- TF-IDF keyword matching works best when the JD and resume both use full,
  meaningful sentences rather than sparse bullet fragments.
- This tool is meant to help **prioritize** review, not replace human judgment
  in hiring decisions.
