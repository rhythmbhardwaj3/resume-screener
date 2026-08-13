"""
matcher.py

Core scoring engine. Combines three signals into one overall match score:

  1. Skill Match   (50%) - overlap between skills detected in the JD and skills
                            detected in the resume, using the SKILLS_DB dictionary.
  2. Keyword/TF-IDF (35%) - cosine similarity between the JD and resume text using
                            TF-IDF vectors, catching relevant keywords/phrases not
                            in the fixed skills dictionary.
  3. Experience Fit (15%) - compares years of experience mentioned in the resume
                            against years required in the JD (if stated).

Weights are configurable via the ResumeMatcher constructor.
"""
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from skills_database import FLAT_SKILLS

YEARS_PATTERN = re.compile(
    r"(\d+)\+?\s*(?:years|yrs|year)\b", re.IGNORECASE
)


class ResumeMatcher:
    def __init__(self, skill_weight=0.50, keyword_weight=0.35, experience_weight=0.15):
        assert abs(skill_weight + keyword_weight + experience_weight - 1.0) < 1e-6, \
            "Weights must sum to 1.0"
        self.skill_weight = skill_weight
        self.keyword_weight = keyword_weight
        self.experience_weight = experience_weight

    # ---------- Skill extraction ----------
    @staticmethod
    def extract_skills(text):
        """Return the set of canonical skill names found in `text`."""
        text_lower = f" {text.lower()} "
        found = set()
        for canonical, meta in FLAT_SKILLS.items():
            for alias in meta["aliases"]:
                pattern = r"(?<![a-zA-Z0-9+#.])" + re.escape(alias.strip()) + r"(?![a-zA-Z0-9+#])"
                if re.search(pattern, text_lower):
                    found.add(canonical)
                    break
        return found

    # ---------- Experience extraction ----------
    @staticmethod
    def extract_years_experience(text):
        """Return the max number of years mentioned in the text (heuristic)."""
        matches = YEARS_PATTERN.findall(text)
        years = [int(m) for m in matches if m.isdigit()]
        return max(years) if years else 0

    # ---------- Skill score ----------
    @staticmethod
    def compute_skill_score(jd_skills, resume_skills):
        if not jd_skills:
            return 100.0, set(), set()
        matched = jd_skills & resume_skills
        missing = jd_skills - resume_skills
        score = (len(matched) / len(jd_skills)) * 100
        return score, matched, missing

    # ---------- Keyword / TF-IDF score ----------
    @staticmethod
    def compute_keyword_score(jd_text, resume_text):
        try:
            vectorizer = TfidfVectorizer(stop_words="english", max_features=2000)
            tfidf_matrix = vectorizer.fit_transform([jd_text, resume_text])
            sim = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return round(sim * 100, 2)
        except ValueError:
            # e.g. empty vocabulary after stopword removal
            return 0.0

    # ---------- Experience score ----------
    @staticmethod
    def compute_experience_score(jd_years, resume_years):
        if jd_years == 0:
            return 100.0  # JD doesn't specify a requirement -> full marks
        if resume_years >= jd_years:
            return 100.0
        return round((resume_years / jd_years) * 100, 2)

    # ---------- Master scoring for one resume ----------
    def score_resume(self, jd_text, resume_text, resume_name="resume"):
        jd_skills = self.extract_skills(jd_text)
        resume_skills = self.extract_skills(resume_text)

        skill_score, matched_skills, missing_skills = self.compute_skill_score(
            jd_skills, resume_skills
        )
        keyword_score = self.compute_keyword_score(jd_text, resume_text)

        jd_years = self.extract_years_experience(jd_text)
        resume_years = self.extract_years_experience(resume_text)
        experience_score = self.compute_experience_score(jd_years, resume_years)

        overall = (
            skill_score * self.skill_weight
            + keyword_score * self.keyword_weight
            + experience_score * self.experience_weight
        )

        return {
            "resume_name": resume_name,
            "overall_score": round(overall, 2),
            "skill_score": round(skill_score, 2),
            "keyword_score": round(keyword_score, 2),
            "experience_score": round(experience_score, 2),
            "resume_years": resume_years,
            "jd_years_required": jd_years,
            "matched_skills": sorted(matched_skills),
            "missing_skills": sorted(missing_skills),
            "total_jd_skills": len(jd_skills),
        }

    # ---------- Rank many resumes ----------
    def rank_resumes(self, jd_text, resumes):
        """
        resumes: dict of {resume_name: resume_text}
        Returns list of score dicts sorted by overall_score descending.
        """
        results = [
            self.score_resume(jd_text, text, name) for name, text in resumes.items()
        ]
        results.sort(key=lambda r: r["overall_score"], reverse=True)
        for i, r in enumerate(results, start=1):
            r["rank"] = i
        return results
