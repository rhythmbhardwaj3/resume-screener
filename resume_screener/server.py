"""
server.py — Local web server for the AI Resume Screening System.

Serves the custom HTML/CSS/JS frontend (in /frontend) and exposes a JSON API
that reuses the same matcher/parser logic as app.py and cli.py.

Run locally with:
    python server.py

Then open http://localhost:5000 in your browser.
"""
import os
import traceback

from flask import Flask, request, jsonify, send_from_directory

from parser import extract_text
from matcher import ResumeMatcher

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

SUPPORTED_EXT = (".pdf", ".docx", ".txt")


@app.route("/")
def index():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/api/rank", methods=["POST"])
def rank():
    try:
        # --- Job description: either pasted text or an uploaded file ---
        jd_text = request.form.get("jd_text", "").strip()
        jd_file = request.files.get("jd_file")
        if jd_file and jd_file.filename:
            ext = os.path.splitext(jd_file.filename)[1].lower()
            if ext not in SUPPORTED_EXT:
                return jsonify({"error": f"Unsupported JD file type: {ext}"}), 400
            jd_text = extract_text(jd_file, filename=jd_file.filename)

        if not jd_text:
            return jsonify({"error": "No job description provided."}), 400

        # --- Resumes: one or more uploaded files ---
        resume_files = request.files.getlist("resume_files")
        if not resume_files:
            return jsonify({"error": "No resume files uploaded."}), 400

        resumes = {}
        skipped = []
        for f in resume_files:
            if not f or not f.filename:
                continue
            ext = os.path.splitext(f.filename)[1].lower()
            if ext not in SUPPORTED_EXT:
                skipped.append(f.filename)
                continue
            try:
                resumes[f.filename] = extract_text(f, filename=f.filename)
            except Exception as e:
                skipped.append(f"{f.filename} ({e})")

        if not resumes:
            return jsonify({"error": "None of the uploaded resumes could be parsed.", "skipped": skipped}), 400

        # --- Optional custom weights ---
        def get_weight(key, default):
            try:
                return float(request.form.get(key, default))
            except (TypeError, ValueError):
                return default

        skill_w = get_weight("skill_weight", 0.50)
        keyword_w = get_weight("keyword_weight", 0.35)
        exp_w = get_weight("experience_weight", 0.15)
        total = skill_w + keyword_w + exp_w
        if total <= 0:
            skill_w, keyword_w, exp_w = 0.50, 0.35, 0.15
        else:
            skill_w, keyword_w, exp_w = (w / total for w in (skill_w, keyword_w, exp_w))

        matcher = ResumeMatcher(skill_weight=skill_w, keyword_weight=keyword_w, experience_weight=exp_w)
        results = matcher.rank_resumes(jd_text, resumes)

        return jsonify({"results": results, "skipped": skipped})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": f"Server error: {e}"}), 500


if __name__ == "__main__":
    print("\n  Resume Screening Desk running at: http://localhost:5000\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
