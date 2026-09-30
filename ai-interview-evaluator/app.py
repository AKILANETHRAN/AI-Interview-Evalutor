import os
import re
from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, session
from database import (
    init_db, get_questions_count, create_candidate, create_interview,
    update_interview_score, save_answer, save_evaluation, get_questions_by_role,
    get_question_by_id, get_interview_report, get_all_interviews, get_interview_by_id
)
from seed_database import seed_questions
from nlp import evaluate_answer, ensure_nltk_resources, get_performance_level

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "ai-interview-evaluator-super-secret-key-2026")

# Supported roles
SUPPORTED_ROLES = [
    "Software Developer",
    "Java Developer",
    "Python Developer",
    "Web Developer",
    "Data Analyst",
    "Machine Learning Engineer"
]

EXPERIENCE_LEVELS = ["Fresher", "Intermediate", "Experienced"]

def setup_application():
    """Ensure database and NLTK are initialized."""
    ensure_nltk_resources()
    init_db()
    if get_questions_count() == 0:
        seed_questions()

# Run initialization once on startup
setup_application()

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))

# ----------------- ROUTES -----------------

@app.route('/')
def index():
    total_q = get_questions_count()
    return render_template('index.html', total_questions=total_q, roles=SUPPORTED_ROLES)

@app.route('/candidate', methods=['GET', 'POST'])
def candidate():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        role = request.form.get('role', '').strip()
        experience_level = request.form.get('experience_level', '').strip()

        # Validation
        errors = []
        if not name or len(name) < 2:
            errors.append("Please enter a valid candidate name (at least 2 characters).")
        if not email or not is_valid_email(email):
            errors.append("Please provide a valid email address.")
        if role not in SUPPORTED_ROLES:
            errors.append("Please select a valid job role from the list.")
        if experience_level not in EXPERIENCE_LEVELS:
            errors.append("Please select a valid experience level.")

        if errors:
            for err in errors:
                flash(err, "danger")
            return render_template(
                'candidate.html',
                roles=SUPPORTED_ROLES,
                experience_levels=EXPERIENCE_LEVELS,
                form_data=request.form
            )

        # Database operations
        try:
            cand_id = create_candidate(name, email, role, experience_level)
            interview_id = create_interview(cand_id)

            session['interview_id'] = interview_id
            session['candidate_id'] = cand_id
            session['candidate_name'] = name
            session['candidate_role'] = role

            return redirect(url_for('interview'))
        except Exception as e:
            flash(f"Error creating interview session: {str(e)}", "danger")
            return render_template(
                'candidate.html',
                roles=SUPPORTED_ROLES,
                experience_levels=EXPERIENCE_LEVELS,
                form_data=request.form
            )

    return render_template(
        'candidate.html',
        roles=SUPPORTED_ROLES,
        experience_levels=EXPERIENCE_LEVELS,
        form_data={}
    )

@app.route('/interview', methods=['GET'])
def interview():
    interview_id = session.get('interview_id')
    role = session.get('candidate_role')
    cand_name = session.get('candidate_name')

    if not interview_id or not role:
        flash("Please register your details to begin an interview.", "warning")
        return redirect(url_for('candidate'))

    questions = get_questions_by_role(role, limit=5)
    if not questions:
        flash("No questions found for the selected role. Please contact support.", "danger")
        return redirect(url_for('candidate'))

    return render_template(
        'interview.html',
        interview_id=interview_id,
        candidate_name=cand_name,
        role=role,
        questions=questions,
        total_questions=len(questions)
    )

@app.route('/interview/answer', methods=['POST'])
@app.route('/interview/submit', methods=['POST'])
def submit_interview():
    """
    Submits all answers, evaluates each via NLP engine, updates SQLite, and returns result.
    Accepts both JSON and standard multipart/form-data.
    """
    is_json = request.is_json
    data = request.get_json(silent=True) if is_json else request.form

    interview_id = data.get('interview_id') or session.get('interview_id')
    if not interview_id:
        if is_json:
            return jsonify({"success": False, "error": "Interview session expired or not found."}), 400
        flash("Interview session expired. Please start a new interview.", "danger")
        return redirect(url_for('candidate'))

    interview_obj = get_interview_by_id(interview_id)
    if not interview_obj:
        if is_json:
            return jsonify({"success": False, "error": "Interview record not found."}), 404
        flash("Interview not found.", "danger")
        return redirect(url_for('candidate'))

    # Parse submitted answers
    answers_map = {}
    if is_json and 'answers' in data:
        # Expected format: {"interview_id": 1, "answers": {"q_1": "text...", ...}} or [{"question_id": 1, "answer": "..."}]
        raw_ans = data.get('answers')
        if isinstance(raw_ans, dict):
            for k, v in raw_ans.items():
                qid = int(k.replace('q_', '')) if 'q_' in str(k) else int(k)
                answers_map[qid] = str(v).strip()
        elif isinstance(raw_ans, list):
            for item in raw_ans:
                answers_map[int(item['question_id'])] = str(item['answer']).strip()
    else:
        # Form data submission
        for key in request.form:
            if key.startswith('answer_'):
                qid = int(key.replace('answer_', ''))
                answers_map[qid] = request.form[key].strip()

    # Validate that at least one answer exists and none are completely empty
    if not answers_map:
        if is_json:
            return jsonify({"success": False, "error": "No answers submitted."}), 400
        flash("Please provide answers to all questions before submitting.", "warning")
        return redirect(url_for('interview'))

    empty_answers = [qid for qid, ans in answers_map.items() if not ans]
    if empty_answers:
        msg = f"Empty answers are not allowed. Please answer all questions before submitting."
        if is_json:
            return jsonify({"success": False, "error": msg}), 400
        flash(msg, "warning")
        return redirect(url_for('interview'))

    # Process each answer through the NLP evaluation pipeline
    final_scores_list = []
    
    for qid, cand_answer in answers_map.items():
        question_data = get_question_by_id(qid)
        if not question_data:
            continue

        ref_answer = question_data['reference_answer']
        q_text = question_data['question']
        keywords = question_data['keywords']

        # Run NLP Engine
        eval_result = evaluate_answer(cand_answer, ref_answer, q_text, keywords)

        # Save to SQLite
        answer_id = save_answer(interview_id, qid, cand_answer)
        save_evaluation(
            answer_id=answer_id,
            relevance_score=eval_result['relevance_score'],
            keyword_score=eval_result['keyword_score'],
            similarity_score=eval_result['similarity_score'],
            completeness_score=eval_result['completeness_score'],
            grammar_score=eval_result['grammar_score'],
            final_score=eval_result['final_score'],
            feedback=eval_result['feedback']
        )
        final_scores_list.append(eval_result['final_score'])

    # Compute overall score and performance level
    if final_scores_list:
        overall_score = round(sum(final_scores_list) / len(final_scores_list), 2)
    else:
        overall_score = 0.0

    overall_performance = get_performance_level(overall_score)
    update_interview_score(interview_id, overall_score, overall_performance)

    # Clear active session
    session.pop('interview_id', None)

    redirect_target = url_for('result', interview_id=interview_id)
    if is_json:
        return jsonify({
            "success": True,
            "overall_score": overall_score,
            "performance": overall_performance,
            "redirect_url": redirect_target
        })
    return redirect(redirect_target)

@app.route('/result/<int:interview_id>')
def result(interview_id):
    report = get_interview_report(interview_id)
    if not report:
        flash("Interview report not found.", "danger")
        return redirect(url_for('history'))
    return render_template('result.html', report=report)

@app.route('/history')
def history():
    all_interviews = get_all_interviews()
    return render_template('history.html', interviews=all_interviews)

@app.route('/demo')
def demo():
    """
    Sample Interview / Demo:
    Candidate: Alex Kumar (alex@example.com, Python Developer, Fresher)
    Evaluates 5 sample answers through the actual NLP engine and redirects to the generated report.
    """
    demo_candidate_name = "Alex Kumar"
    demo_email = "alex@example.com"
    demo_role = "Python Developer"
    demo_exp = "Fresher"

    # 1. Fetch 5 Python Developer questions
    questions = get_questions_by_role(demo_role, limit=5)
    if len(questions) < 5:
        # Fallback to reseed if questions missing
        seed_questions()
        questions = get_questions_by_role(demo_role, limit=5)

    # 5 Sample candidate answers requested by requirements
    sample_answers_text = [
        # Q1: What is Python?
        "Python is a high level interpreted programming language with simple syntax. It supports object oriented programming and is widely used for software development.",
        # Q2: What is inheritance?
        "Inheritance allows a child class to acquire properties and methods from a parent class. It is an important concept in object oriented programming.",
        # Q3: What are Python decorators?
        "Decorators are functions that take another function as an argument and extend its behavior without modifying the original function code using the @ syntax.",
        # Q4: Difference between lists and tuples?
        "Lists are mutable sequences defined with square brackets that can be modified, while tuples are immutable sequences defined with parentheses that cannot be changed after creation.",
        # Q5: What is Global Interpreter Lock (GIL)?
        "The Global Interpreter Lock is a mutex that protects access to Python objects, preventing multiple native threads from executing Python bytecodes simultaneously in CPython."
    ]

    try:
        cand_id = create_candidate(demo_candidate_name, demo_email, demo_role, demo_exp)
        interview_id = create_interview(cand_id)

        final_scores_list = []

        for i, q in enumerate(questions):
            ans_text = sample_answers_text[i] if i < len(sample_answers_text) else sample_answers_text[0]
            
            # Run the genuine NLP evaluation pipeline
            eval_result = evaluate_answer(
                candidate_answer=ans_text,
                reference_answer=q['reference_answer'],
                question=q['question'],
                expected_keywords=q['keywords']
            )

            # Save answer and NLP evaluation in SQLite
            answer_id = save_answer(interview_id, q['id'], ans_text)
            save_evaluation(
                answer_id=answer_id,
                relevance_score=eval_result['relevance_score'],
                keyword_score=eval_result['keyword_score'],
                similarity_score=eval_result['similarity_score'],
                completeness_score=eval_result['completeness_score'],
                grammar_score=eval_result['grammar_score'],
                final_score=eval_result['final_score'],
                feedback=eval_result['feedback']
            )
            final_scores_list.append(eval_result['final_score'])

        # Update overall score and performance
        overall_score = round(sum(final_scores_list) / len(final_scores_list), 2)
        performance = get_performance_level(overall_score)
        update_interview_score(interview_id, overall_score, performance)

        flash("Sample demo interview evaluated successfully using the live NLP engine!", "success")
        return redirect(url_for('result', interview_id=interview_id))
    except Exception as e:
        flash(f"Error executing demo interview: {str(e)}", "danger")
        return redirect(url_for('index'))

@app.route('/health')
def health():
    try:
        q_count = get_questions_count()
        return jsonify({
            "status": "healthy",
            "database": "connected",
            "total_questions": q_count,
            "supported_roles": len(SUPPORTED_ROLES),
            "nlp_engine": "online",
            "nltk_status": "ready"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "error": str(e)
        }), 500

@app.route('/api/interview/<int:interview_id>')
def api_interview_report(interview_id):
    report = get_interview_report(interview_id)
    if not report:
        return jsonify({"error": "Report not found"}), 404
    return jsonify(report)

@app.errorhandler(404)
def not_found_error(error):
    return render_template('index.html', error_msg="The requested page could not be found."), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('index.html', error_msg="An internal server error occurred. Please try again."), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(host="0.0.0.0", port=port, debug=debug)

