import os
import sqlite3
from datetime import datetime

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database", "interview.db")

def get_db_connection(db_path=None):
    """
    Establish a connection to the SQLite database.
    Enables foreign keys and returns rows as dictionaries.
    """
    path = db_path or DEFAULT_DB_PATH
    os.makedirs(os.path.dirname(path), exist_ok=True)
    conn = sqlite3.connect(path, timeout=10.0)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn

def init_db(db_path=None):
    """
    Initialize all database tables with appropriate constraints.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS candidates (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        role TEXT NOT NULL,
        experience_level TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        question TEXT NOT NULL,
        reference_answer TEXT NOT NULL,
        keywords TEXT NOT NULL,
        difficulty TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER NOT NULL,
        date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        overall_score REAL DEFAULT 0.0,
        performance TEXT DEFAULT 'Pending',
        FOREIGN KEY(candidate_id) REFERENCES candidates(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        candidate_answer TEXT NOT NULL,
        FOREIGN KEY(interview_id) REFERENCES interviews(id) ON DELETE CASCADE,
        FOREIGN KEY(question_id) REFERENCES questions(id) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS evaluations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        answer_id INTEGER NOT NULL,
        relevance_score REAL NOT NULL,
        keyword_score REAL NOT NULL,
        similarity_score REAL NOT NULL,
        completeness_score REAL NOT NULL,
        grammar_score REAL NOT NULL,
        final_score REAL NOT NULL,
        feedback TEXT NOT NULL,
        FOREIGN KEY(answer_id) REFERENCES answers(id) ON DELETE CASCADE
    );
    """)

    conn.commit()
    conn.close()

def create_candidate(name, email, role, experience_level, db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO candidates (name, email, role, experience_level) VALUES (?, ?, ?, ?)",
        (name.strip(), email.strip().lower(), role.strip(), experience_level.strip())
    )
    candidate_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return candidate_id

def create_interview(candidate_id, db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO interviews (candidate_id, date, overall_score, performance) VALUES (?, ?, ?, ?)",
        (candidate_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 0.0, 'Pending')
    )
    interview_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return interview_id

def update_interview_score(interview_id, overall_score, performance, db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE interviews SET overall_score = ?, performance = ? WHERE id = ?",
        (round(float(overall_score), 2), performance, interview_id)
    )
    conn.commit()
    conn.close()

def save_answer(interview_id, question_id, candidate_answer, db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO answers (interview_id, question_id, candidate_answer) VALUES (?, ?, ?)",
        (interview_id, question_id, candidate_answer.strip())
    )
    answer_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return answer_id

def save_evaluation(answer_id, relevance_score, keyword_score, similarity_score, completeness_score, grammar_score, final_score, feedback, db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO evaluations 
           (answer_id, relevance_score, keyword_score, similarity_score, completeness_score, grammar_score, final_score, feedback)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (answer_id, round(float(relevance_score), 2), round(float(keyword_score), 2),
         round(float(similarity_score), 2), round(float(completeness_score), 2),
         round(float(grammar_score), 2), round(float(final_score), 2), feedback)
    )
    eval_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return eval_id

def get_questions_by_role(role, limit=5, db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM questions WHERE role = ? ORDER BY id ASC LIMIT ?",
        (role, limit)
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_question_by_id(question_id, db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM questions WHERE id = ?", (question_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_interview_by_id(interview_id, db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_interview_report(interview_id, db_path=None):
    """
    Fetch comprehensive interview report including candidate information,
    each question, candidate answer, reference answer, component scores, and feedback.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT i.id AS interview_id, i.date, i.overall_score, i.performance,
               c.id AS candidate_id, c.name AS candidate_name, c.email AS candidate_email,
               c.role AS candidate_role, c.experience_level
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        WHERE i.id = ?
    """, (interview_id,))
    interview_meta = cursor.fetchone()

    if not interview_meta:
        conn.close()
        return None

    report = dict(interview_meta)

    cursor.execute("""
        SELECT a.id AS answer_id, a.candidate_answer,
               q.id AS question_id, q.question, q.reference_answer, q.keywords, q.difficulty,
               e.id AS eval_id, e.relevance_score, e.keyword_score, e.similarity_score,
               e.completeness_score, e.grammar_score, e.final_score, e.feedback
        FROM answers a
        JOIN questions q ON a.question_id = q.id
        LEFT JOIN evaluations e ON e.answer_id = a.id
        WHERE a.interview_id = ?
        ORDER BY a.id ASC
    """, (interview_id,))
    qa_list = [dict(row) for row in cursor.fetchall()]
    report['qa_list'] = qa_list

    # Calculate average category scores for radar chart
    if qa_list and any(item.get('relevance_score') is not None for item in qa_list):
        count = len(qa_list)
        report['avg_relevance'] = round(sum(item.get('relevance_score', 0) for item in qa_list) / count, 2)
        report['avg_keywords'] = round(sum(item.get('keyword_score', 0) for item in qa_list) / count, 2)
        report['avg_similarity'] = round(sum(item.get('similarity_score', 0) for item in qa_list) / count, 2)
        report['avg_completeness'] = round(sum(item.get('completeness_score', 0) for item in qa_list) / count, 2)
        report['avg_grammar'] = round(sum(item.get('grammar_score', 0) for item in qa_list) / count, 2)
    else:
        report['avg_relevance'] = 0.0
        report['avg_keywords'] = 0.0
        report['avg_similarity'] = 0.0
        report['avg_completeness'] = 0.0
        report['avg_grammar'] = 0.0

    conn.close()
    return report

def get_all_interviews(db_path=None):
    """
    Retrieve all interviews sorted by date descending for interview history.
    """
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT i.id, i.date, i.overall_score, i.performance,
               c.name AS candidate_name, c.email AS candidate_email,
               c.role AS candidate_role, c.experience_level
        FROM interviews i
        JOIN candidates c ON i.candidate_id = c.id
        ORDER BY i.date DESC, i.id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_questions_count(db_path=None):
    conn = get_db_connection(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS total FROM questions")
    count = cursor.fetchone()['total']
    conn.close()
    return count
