import fitz

SKILLS = [
    "python",
    "java",
    "sql",
    "flask",
    "machine learning",
    "artificial intelligence",
    "ai",
    "html",
    "css",
    "javascript",
    "c++",
    "communication",
    "teamwork",
    "leadership"
]

def analyze_resume(file_path):

    text = ""

    doc = fitz.open(file_path)

    for page in doc:
        text += page.get_text().lower()

    doc.close()

    found_skills = []

    for skill in SKILLS:
        if skill in text:
            found_skills.append(skill)

    score = min(len(found_skills) * 10, 100)

    return found_skills, score