"""
cli.py — Command-line version of the AI Resume Screening System.

Usage:
    python cli.py --jd job_description.txt --resumes resumes_folder/ --output results.csv

    --jd         Path to the job description file (.pdf, .docx, or .txt)
    --resumes    Path to a folder containing resume files (.pdf, .docx, .txt)
    --output     (optional) Path to save the CSV report. Default: ranking_report.csv
    --top        (optional) Only show the top N results in the console. Default: show all.
"""
import argparse
import os
import sys

import pandas as pd

from parser import extract_text
from matcher import ResumeMatcher

SUPPORTED_EXT = (".pdf", ".docx", ".txt")


def load_resumes_from_folder(folder_path):
    resumes = {}
    for fname in sorted(os.listdir(folder_path)):
        if fname.lower().endswith(SUPPORTED_EXT):
            fpath = os.path.join(folder_path, fname)
            try:
                resumes[fname] = extract_text(fpath, filename=fname)
            except Exception as e:
                print(f"  [warning] Could not parse {fname}: {e}", file=sys.stderr)
    return resumes


def main():
    parser = argparse.ArgumentParser(description="Rank resumes against a job description.")
    parser.add_argument("--jd", required=True, help="Path to job description file (.pdf/.docx/.txt)")
    parser.add_argument("--resumes", required=True, help="Path to folder containing resumes")
    parser.add_argument("--output", default="ranking_report.csv", help="Path to save CSV report")
    parser.add_argument("--top", type=int, default=None, help="Show only top N results in console")
    args = parser.parse_args()

    if not os.path.isfile(args.jd):
        sys.exit(f"Error: job description file not found: {args.jd}")
    if not os.path.isdir(args.resumes):
        sys.exit(f"Error: resumes folder not found: {args.resumes}")

    print(f"Reading job description from {args.jd} ...")
    jd_text = extract_text(args.jd, filename=args.jd)

    print(f"Loading resumes from {args.resumes} ...")
    resumes = load_resumes_from_folder(args.resumes)
    if not resumes:
        sys.exit("No supported resume files (.pdf/.docx/.txt) found in that folder.")
    print(f"Loaded {len(resumes)} resume(s). Scoring...")

    matcher = ResumeMatcher()
    results = matcher.rank_resumes(jd_text, resumes)

    rows = []
    for r in results:
        rows.append({
            "Rank": r["rank"],
            "Resume": r["resume_name"],
            "Overall Score": r["overall_score"],
            "Skill Match %": r["skill_score"],
            "Keyword Match %": r["keyword_score"],
            "Experience Match %": r["experience_score"],
            "Years Found": r["resume_years"],
            "JD Years Required": r["jd_years_required"],
            "Matched Skills": ", ".join(r["matched_skills"]),
            "Missing Skills": ", ".join(r["missing_skills"]),
        })
    df = pd.DataFrame(rows)
    df.to_csv(args.output, index=False)
    print(f"\nSaved full report to: {args.output}\n")

    top_n = args.top or len(results)
    print(f"{'Rank':<5}{'Score':<8}{'Resume'}")
    print("-" * 60)
    for r in results[:top_n]:
        print(f"{r['rank']:<5}{r['overall_score']:<8}{r['resume_name']}")


if __name__ == "__main__":
    main()
