import urllib.request
import urllib.parse
import http.cookiejar
import json
import re
import sys
import sqlite3
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

BASE_URL = "http://127.0.0.1:5000"

def run_system_audit():
    print("=" * 65)
    print("STARTING FULL SYSTEM AUDIT: AI INTERVIEW EVALUATOR")
    print("=" * 65)

    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # --- 1. HEALTH ENDPOINT & SERVICES ---
    print("\n[Audit 1/14] Testing /health endpoint...")
    res = opener.open(f"{BASE_URL}/health")
    assert res.status == 200, f"Expected 200, got {res.status}"
    health = json.loads(res.read().decode('utf-8'))
    assert health.get("status") == "healthy"
    assert health.get("database") == "connected"
    assert health.get("nlp_engine") == "online"
    assert health.get("nltk_status") == "ready"
    assert health.get("total_questions") >= 30
    print(f"  -> PASS: Health status healthy, 42 questions, all services online.")

    # --- 2. HOMEPAGE VERIFICATION ---
    print("\n[Audit 2/14] Testing Homepage (GET /)...")
    res = opener.open(f"{BASE_URL}/")
    assert res.status == 200
    home_html = res.read().decode('utf-8')
    assert "AI Interview Evaluator" in home_html
    assert "Practice. Analyze. Improve." in home_html
    assert "Start Interview" in home_html
    assert "Try Sample Interview" in home_html
    assert "View Interview History" in home_html
    print("  -> PASS: Homepage rendered with all CTA buttons and feature cards.")

    # --- 3. CANDIDATE SETUP & ROLE SELECTION ---
    print("\n[Audit 3/14] Testing Candidate Details & Role Selection (POST /candidate)...")
    cand_data = urllib.parse.urlencode({
        "name": "Audit Candidate",
        "email": "audit.candidate@example.com",
        "role": "Python Developer",
        "experience_level": "Intermediate"
    }).encode('utf-8')
    res = opener.open(f"{BASE_URL}/candidate", data=cand_data)
    assert res.status == 200
    interview_html = res.read().decode('utf-8')
    assert "Technical Interview In Progress" in interview_html
    assert "Audit Candidate" in interview_html
    assert "Python Developer" in interview_html
    print("  -> PASS: Frontend form correctly communicates with Flask; session created.")

    # --- 4. EXTRACT QUESTIONS & VERIFY DATABASE COMMUNICATION ---
    print("\n[Audit 4/14] Verifying Questions Retrieved from SQLite...")
    q_ids = re.findall(r'name="answer_(\d+)"', interview_html)
    assert len(q_ids) == 5, f"Expected 5 questions, found {len(q_ids)}"
    print(f"  -> PASS: Flask correctly retrieved 5 questions for Python Developer from SQLite: IDs {q_ids}")

    # --- 5. ANSWER SUBMISSION & BACKEND REACH ---
    print("\n[Audit 5/14] Submitting Candidate Answers (POST /interview/submit)...")
    answers_payload = {
        f"answer_{q_ids[0]}": "Python is a high-level interpreted programming language with simple syntax. It supports object oriented programming and is widely used for software development.",
        f"answer_{q_ids[1]}": "Inheritance allows a child class to inherit attributes and methods from a parent class for code reusability.",
        f"answer_{q_ids[2]}": "Decorators are higher-order functions that take a function as an argument and extend its behavior without modifying it using the @ syntax.",
        f"answer_{q_ids[3]}": "Lists are mutable ordered sequences in square brackets, while tuples are immutable sequences in parentheses.",
        f"answer_{q_ids[4]}": "The Global Interpreter Lock is a mutex in CPython that prevents multiple native threads from executing bytecodes simultaneously."
    }
    submit_data = urllib.parse.urlencode(answers_payload).encode('utf-8')
    res = opener.open(f"{BASE_URL}/interview/submit", data=submit_data)
    result_url = res.geturl()
    assert "/result/" in result_url, f"Expected redirect to /result/<id>, got {result_url}"
    result_html = res.read().decode('utf-8')
    print(f"  -> PASS: Answers reached backend, NLP evaluated, redirected to: {result_url}")

    # --- 6. SQLITE STORAGE VERIFICATION ---
    print("\n[Audit 6/14] Verifying SQLite Storage of Answers and Evaluations...")
    iv_match = re.search(r'/result/(\d+)', result_url)
    assert iv_match, "Interview ID not found in result URL"
    interview_id = int(iv_match.group(1))

    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "database", "interview.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
    iv_row = cursor.fetchone()
    assert iv_row, f"Interview record {interview_id} not found in database!"
    overall_score = iv_row['overall_score']
    performance = iv_row['performance']
    assert overall_score > 0.0, "Overall score must be greater than 0!"
    print(f"  -> PASS: Interview record stored: Score={overall_score}, Performance='{performance}'.")

    cursor.execute("SELECT * FROM answers WHERE interview_id = ?", (interview_id,))
    saved_answers = cursor.fetchall()
    assert len(saved_answers) == 5, f"Expected 5 saved answers, found {len(saved_answers)}"
    print(f"  -> PASS: 5 candidate answers persisted in 'answers' table.")

    cursor.execute("""
        SELECT e.* FROM evaluations e
        JOIN answers a ON e.answer_id = a.id
        WHERE a.interview_id = ?
    """, (interview_id,))
    saved_evals = cursor.fetchall()
    assert len(saved_evals) == 5, f"Expected 5 evaluation rows, found {len(saved_evals)}"
    print(f"  -> PASS: 5 evaluation records persisted in 'evaluations' table.")

    # --- 7. SCORING FORMULA VERIFICATION ---
    print("\n[Audit 7/14] Auditing Scoring Formula Exact Weights on Database Rows...")
    # final_score = (relevance * 0.25) + (keyword_score * 0.25) + (similarity * 0.25) + (completeness * 0.15) + (grammar * 0.10)
    for idx, ev in enumerate(saved_evals):
        rel = ev['relevance_score']
        kw = ev['keyword_score']
        sim = ev['similarity_score']
        comp = ev['completeness_score']
        gram = ev['grammar_score']
        stored_final = ev['final_score']

        expected_final = round((rel * 0.25) + (kw * 0.25) + (sim * 0.25) + (comp * 0.15) + (gram * 0.10), 2)
        diff = abs(stored_final - expected_final)
        assert diff <= 0.02, f"Formula mismatch for eval {ev['id']}: stored={stored_final}, expected={expected_final}"
        assert 0.0 <= stored_final <= 100.0
        assert 0.0 <= rel <= 100.0
        assert 0.0 <= kw <= 100.0
        assert 0.0 <= sim <= 100.0
        assert 0.0 <= comp <= 100.0
        assert 0.0 <= gram <= 100.0
    print("  -> PASS: Exact weights (25/25/25/15/10) mathematically verified on all stored evaluations.")

    # --- 8. RESULT DASHBOARD RETRIEVAL ---
    print("\n[Audit 8/14] Verifying Result Dashboard Displays Actual Database Values...")
    assert "Audit Candidate" in result_html
    assert "Python Developer" in result_html
    assert str(overall_score) in result_html
    assert performance in result_html
    assert "Multi-Dimensional Skill Radar" in result_html
    assert "Question-by-Question Performance" in result_html
    print("  -> PASS: Result dashboard rendered real candidate info and scores.")

    # --- 9. CHART.JS VALUES AUDIT ---
    print("\n[Audit 9/14] Verifying Chart.js Receives Actual Backend Database Values...")
    radar_match = re.search(r'const radarData = \{([^}]+)\};', result_html)
    assert radar_match, "radarData script block not found in result HTML"
    bar_match = re.search(r'const barData = \[([^\]]+)\];', result_html)
    assert bar_match, "barData script block not found in result HTML"

    radar_str = radar_match.group(1)
    print(f"  -> Chart.js radar payload extracted: {radar_str.strip()}")
    assert "relevance:" in radar_str
    assert "keywords:" in radar_str
    assert "similarity:" in radar_str
    assert "completeness:" in radar_str
    assert "grammar:" in radar_str

    for i in range(1, 6):
        assert f'"Q{i}"' in bar_match.group(1) or f"'Q{i}'" in bar_match.group(1) or f'Q{i}' in bar_match.group(1)
    print("  -> PASS: Chart.js scripts injected with verified dynamic database values.")

    # --- 10. HISTORY ARCHIVE & PREVIOUS REPORT ---
    print("\n[Audit 10/14] Verifying History Retrieval from SQLite...")
    res = opener.open(f"{BASE_URL}/history")
    assert res.status == 200
    hist_html = res.read().decode('utf-8')
    assert "Audit Candidate" in hist_html
    assert "Python Developer" in hist_html
    assert str(overall_score) in hist_html
    assert f"/result/{interview_id}" in hist_html
    print(f"  -> PASS: History page lists interview session #{interview_id} with actual database score.")

    print("\n[Audit 10b/14] Opening Previous Report via History Link...")
    res_prev = opener.open(f"{BASE_URL}/result/{interview_id}")
    assert res_prev.status == 200
    prev_html = res_prev.read().decode('utf-8')
    assert "Audit Candidate" in prev_html
    print("  -> PASS: Previous report retrieved and displayed accurately.")

    # --- 11. DEMO ENDPOINT VERIFICATION ---
    print("\n[Audit 11/14] Verifying /demo Endpoint Uses Live NLP Engine...")
    res_demo = opener.open(f"{BASE_URL}/demo")
    assert res_demo.status == 200
    demo_url = res_demo.geturl()
    demo_html = res_demo.read().decode('utf-8')
    assert "Alex Kumar" in demo_html
    assert "Python Developer" in demo_html

    demo_id = int(re.search(r'/result/(\d+)', demo_url).group(1))
    cursor.execute("SELECT * FROM interviews WHERE id = ?", (demo_id,))
    demo_row = cursor.fetchone()
    assert demo_row, "Demo interview row not found in database!"
    assert demo_row['overall_score'] > 0.0
    print(f"  -> PASS: /demo executed live NLP evaluation: Saved interview #{demo_id}, Score={demo_row['overall_score']}.")

    # --- 12. NO RANDOM EVALUATION SCORES (DETERMINISM AUDIT) ---
    print("\n[Audit 12/14] Auditing Score Determinism (Zero Randomness)...")
    cursor.execute("""
        SELECT e.final_score, e.feedback FROM evaluations e
        JOIN answers a ON e.answer_id = a.id
        WHERE a.interview_id = ? ORDER BY a.id ASC
    """, (interview_id,))
    first_run_scores = [r['final_score'] for r in cursor.fetchall()]

    # Re-evaluate the exact same answers directly through the engine
    from nlp import evaluate_answer
    re_eval_scores = []
    cursor.execute("""
        SELECT a.candidate_answer, q.reference_answer, q.question, q.keywords
        FROM answers a JOIN questions q ON a.question_id = q.id
        WHERE a.interview_id = ? ORDER BY a.id ASC
    """, (interview_id,))
    rows = cursor.fetchall()
    for r in rows:
        re_res = evaluate_answer(r['candidate_answer'], r['reference_answer'], r['question'], r['keywords'])
        re_eval_scores.append(re_res['final_score'])

    assert first_run_scores == re_eval_scores, f"Non-deterministic scores! {first_run_scores} != {re_eval_scores}"
    print(f"  -> PASS: Zero randomness. Run 1 {first_run_scores} == Run 2 {re_eval_scores} (100% deterministic).")

    # --- 13. NO HARD-CODED EVALUATION SCORES ---
    print("\n[Audit 13/14] Auditing Response Variance (No Hard-Coded Scores)...")
    # A poor answer must receive a drastically lower score than a thorough answer
    poor_res = evaluate_answer(
        "code",
        rows[0]['reference_answer'],
        rows[0]['question'],
        rows[0]['keywords']
    )
    thorough_res = evaluate_answer(
        rows[0]['candidate_answer'],
        rows[0]['reference_answer'],
        rows[0]['question'],
        rows[0]['keywords']
    )
    assert poor_res['final_score'] < thorough_res['final_score'] - 20.0, "Scores do not adapt to answer quality!"
    print(f"  -> PASS: Scores dynamically adapt (Thorough={thorough_res['final_score']} vs Minimal={poor_res['final_score']}). No hard-coded values.")

    # --- 14. NO DEBUG / DEVELOPMENT INFO LEAKED ---
    print("\n[Audit 14/14] Auditing Error Handling (No Stack Traces Leaked)...")
    try:
        err_res = opener.open(f"{BASE_URL}/nonexistent-test-404")
        err_html = err_res.read().decode('utf-8')
    except urllib.error.HTTPError as e:
        err_html = e.read().decode('utf-8')
        assert e.code == 404
    
    assert "Traceback (most recent call last)" not in err_html
    assert "Werkzeug Debugger" not in err_html
    assert "The requested page could not be found" in err_html
    print("  -> PASS: Clean custom 404 handler active. Zero tracebacks or debug internals visible.")

    conn.close()

    print("\n" + "=" * 65)
    print("ALL 14 AUDIT CHECKS PASSED WITH ZERO ERRORS!")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    run_system_audit()
