"""
skills_database.py

A categorized dictionary of common professional skills used for skill-matching.
Each skill maps to a list of alias strings that should also count as a match
(e.g. "js" and "javascript" both match the "javascript" skill).

Feel free to extend this list for your industry / role.
"""

SKILLS_DB = {
    "Programming Languages": {
        "python": ["python", "py"],
        "java": ["java"],
        "javascript": ["javascript", "js", "es6"],
        "typescript": ["typescript", "ts"],
        "c++": ["c++", "cpp"],
        "c#": ["c#", "csharp", "c sharp"],
        "go": ["golang", "go lang", " go "],
        "rust": ["rust"],
        "php": ["php"],
        "ruby": ["ruby"],
        "swift": ["swift"],
        "kotlin": ["kotlin"],
        "scala": ["scala"],
        "r": ["r programming", " r language", " r,"],
        "sql": ["sql"],
        "matlab": ["matlab"],
        "shell scripting": ["bash", "shell script", "shell scripting"],
    },
    "Web Frameworks": {
        "react": ["react", "reactjs", "react.js"],
        "angular": ["angular", "angularjs"],
        "vue": ["vue", "vuejs", "vue.js"],
        "django": ["django"],
        "flask": ["flask"],
        "fastapi": ["fastapi"],
        "spring": ["spring boot", "spring framework", "spring"],
        "express": ["express.js", "expressjs", "express"],
        "next.js": ["next.js", "nextjs"],
        "node.js": ["node.js", "nodejs", "node"],
        "asp.net": ["asp.net", "dotnet", ".net"],
        "ruby on rails": ["ruby on rails", "rails"],
        "html/css": ["html", "css", "html5", "css3"],
        "tailwind": ["tailwind", "tailwindcss"],
        "bootstrap": ["bootstrap"],
    },
    "Databases": {
        "mysql": ["mysql"],
        "postgresql": ["postgresql", "postgres"],
        "mongodb": ["mongodb", "mongo"],
        "redis": ["redis"],
        "oracle db": ["oracle database", "oracle db", "oracle sql"],
        "sql server": ["sql server", "mssql"],
        "sqlite": ["sqlite"],
        "cassandra": ["cassandra"],
        "elasticsearch": ["elasticsearch", "elastic search"],
        "dynamodb": ["dynamodb"],
        "firebase": ["firebase", "firestore"],
    },
    "Cloud & DevOps": {
        "aws": ["aws", "amazon web services"],
        "azure": ["azure", "microsoft azure"],
        "gcp": ["gcp", "google cloud", "google cloud platform"],
        "docker": ["docker", "containerization"],
        "kubernetes": ["kubernetes", "k8s"],
        "terraform": ["terraform"],
        "jenkins": ["jenkins"],
        "ci/cd": ["ci/cd", "continuous integration", "continuous deployment"],
        "ansible": ["ansible"],
        "git": ["git", "github", "gitlab", "version control"],
        "linux": ["linux", "unix"],
        "nginx": ["nginx"],
        "microservices": ["microservices", "microservice architecture"],
    },
    "Data Science & ML": {
        "machine learning": ["machine learning", "ml"],
        "deep learning": ["deep learning", "neural networks"],
        "nlp": ["nlp", "natural language processing"],
        "computer vision": ["computer vision", "cv "],
        "tensorflow": ["tensorflow"],
        "pytorch": ["pytorch"],
        "scikit-learn": ["scikit-learn", "sklearn"],
        "pandas": ["pandas"],
        "numpy": ["numpy"],
        "data visualization": ["data visualization", "tableau", "power bi", "powerbi"],
        "statistics": ["statistics", "statistical analysis"],
        "data analysis": ["data analysis", "data analytics"],
        "big data": ["big data", "hadoop", "spark", "pyspark"],
        "etl": ["etl", "data pipeline", "data pipelines"],
        "llm": ["llm", "large language model", "generative ai", "genai"],
    },
    "Project Management & Tools": {
        "agile": ["agile", "scrum", "kanban"],
        "jira": ["jira"],
        "confluence": ["confluence"],
        "project management": ["project management", "pmp"],
        "excel": ["excel", "microsoft excel", "spreadsheets"],
        "figma": ["figma"],
        "salesforce": ["salesforce"],
        "sap": ["sap"],
    },
    "Testing & QA": {
        "unit testing": ["unit testing", "unit tests"],
        "selenium": ["selenium"],
        "test automation": ["test automation", "automated testing"],
        "jest": ["jest"],
        "pytest": ["pytest"],
        "qa": ["quality assurance", " qa "],
    },
    "Soft Skills": {
        "communication": ["communication skills", "communication"],
        "leadership": ["leadership", "team lead", "team leadership"],
        "teamwork": ["teamwork", "collaboration", "cross-functional"],
        "problem solving": ["problem solving", "problem-solving", "analytical skills"],
        "time management": ["time management"],
        "presentation": ["presentation skills", "public speaking"],
        "mentoring": ["mentoring", "mentorship"],
        "stakeholder management": ["stakeholder management", "client management"],
    },
    "Mobile": {
        "android": ["android development", "android"],
        "ios": ["ios development", "ios"],
        "react native": ["react native"],
        "flutter": ["flutter"],
    },
}


def flatten_skills():
    """Return a flat dict: canonical_skill_name -> [alias list], with category attached."""
    flat = {}
    for category, skills in SKILLS_DB.items():
        for canonical, aliases in skills.items():
            flat[canonical] = {"aliases": aliases, "category": category}
    return flat


FLAT_SKILLS = flatten_skills()
