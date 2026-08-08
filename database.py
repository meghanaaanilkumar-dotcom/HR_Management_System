import sqlite3

# Connect to SQLite database
conn = sqlite3.connect("hrms.db")

cursor = conn.cursor()

# Create candidates table
cursor.execute("""
CREATE TABLE IF NOT EXISTS candidates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT,
    position TEXT,
    resume TEXT,
    skills TEXT,
    resume_score INTEGER,
    interview_score INTEGER,
    status TEXT
)
""")

conn.commit()
conn.close()

print("Database created successfully!")