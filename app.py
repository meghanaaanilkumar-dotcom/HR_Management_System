from flask import Flask, render_template, request
import sqlite3
import os
from werkzeug.utils import secure_filename
from resume_analyzer import analyze_resume

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


# ---------------- HOME ----------------

@app.route("/")
def home():
    return render_template("index.html")


# ---------------- REGISTER + RESUME ANALYSIS ----------------

@app.route("/interview", methods=["POST"])
def interview():

    name = request.form["name"]
    email = request.form["email"]
    position = request.form["position"]

    resume = request.files["resume"]

    filename = secure_filename(resume.filename)
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    resume.save(filepath)

    # AI Resume Analysis
    skills, resume_score = analyze_resume(filepath)

    conn = sqlite3.connect("hrms.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO candidates
        (name,email,position,resume,skills,resume_score,interview_score,status)
        VALUES (?,?,?,?,?,?,?,?)
    """, (
        name,
        email,
        position,
        filename,
        ", ".join(skills),
        resume_score,
        0,
        "Pending"
    ))

    conn.commit()
    conn.close()

    return render_template(
        "interview.html",
        name=name,
        skills=skills,
        score=resume_score
    )


# ---------------- RESULT ----------------

@app.route("/result")
def result():

    conn = sqlite3.connect("hrms.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id,resume_score
        FROM candidates
        ORDER BY id DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    if row is None:
        conn.close()
        return "No candidate found."

    candidate_id = row[0]
    resume_score = row[1]

    technical_score = 90
    communication_score = 85

    overall_score = int(
        (resume_score + technical_score + communication_score) / 3
    )

    if overall_score >= 80:
        status = "Selected"
    else:
        status = "Rejected"

    cursor.execute("""
        UPDATE candidates
        SET interview_score=?,
            status=?
        WHERE id=?
    """, (
        overall_score,
        status,
        candidate_id
    ))

    conn.commit()
    conn.close()

    return render_template(
        "result.html",
        resume_score=resume_score,
        technical_score=technical_score,
        communication_score=communication_score,
        overall_score=overall_score,
        status=status
    )


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("hrms.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
        name,
        email,
        position,
        skills,
        resume_score,
        status
        FROM candidates
    """)

    candidates = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM candidates")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM candidates WHERE status='Selected'")
    selected = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM candidates WHERE status='Rejected'")
    rejected = cursor.fetchone()[0]

    cursor.execute("SELECT AVG(resume_score) FROM candidates")
    avg_score = cursor.fetchone()[0]

    if avg_score is None:
        avg_score = 0

    # AI Recommendation
    if avg_score >= 80:
        recommendation = "Excellent candidate pool. Most resumes match the required technical skills."
    elif avg_score >= 60:
        recommendation = "Average candidate quality. Conduct technical interviews before selection."
    else:
        recommendation = "Candidate quality is below expectations. Recruit more skilled applicants."

    conn.close()

    return render_template(
        "dashboard.html",
        candidates=candidates,
        total=total,
        selected=selected,
        rejected=rejected,
        avg_score=round(avg_score, 1),
        recommendation=recommendation
    )


# ---------------- RUN APP ----------------

if __name__ == "__main__":
    app.run(debug=True)