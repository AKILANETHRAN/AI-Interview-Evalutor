import os
import sys
import unittest
import tempfile
import json

# Ensure ai-interview-evaluator is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import app as flask_app
import database
from seed_database import seed_questions, QUESTIONS_DATA
from nlp.preprocessing import preprocess_pipeline
from nlp.keyword_extractor import match_keywords, extract_keywords
from nlp.similarity import compute_tfidf_similarity, compute_relevance_score
from nlp.evaluator import evaluate_answer, analyze_completeness, analyze_language_quality
from nlp.feedback import generate_feedback, get_performance_level

class AIInterviewEvaluatorTestCase(unittest.TestCase):
    def setUp(self):
        # Create a temporary database for isolated testing
        self.db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        database.DEFAULT_DB_PATH = self.temp_db_path

        # Configure Flask app for testing
        flask_app.app.config['TESTING'] = True
        flask_app.app.config['WTF_CSRF_ENABLED'] = False
        flask_app.app.secret_key = "test-secret-key"
        self.client = flask_app.app.test_client()

        # Initialize and seed temporary database
        seed_questions(self.temp_db_path)

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.remove(self.temp_db_path)
        except OSError:
            pass

    # 1. Home Page
    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('AI Interview Evaluator', content)
        self.assertIn('Practice. Analyze. Improve.', content)
        self.assertIn('Start Interview', content)
        self.assertIn('Try Sample Interview', content)
        self.assertIn('View Interview History', content)

    # 2. Health Endpoint
    def test_health_endpoint(self):
        response = self.client.get('/health')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data.get('status'), 'healthy')
        self.assertEqual(data.get('database'), 'connected')
        self.assertGreaterEqual(data.get('total_questions', 0), 30)

    # 3. Question Retrieval and Seeding
    def test_question_retrieval_and_seeding(self):
        count = database.get_questions_count(self.temp_db_path)
        self.assertGreaterEqual(count, 30)
        
        # Test roles
        roles = [
            "Software Developer", "Java Developer", "Python Developer",
            "Web Developer", "Data Analyst", "Machine Learning Engineer"
        ]
        for role in roles:
            q_list = database.get_questions_by_role(role, limit=10, db_path=self.temp_db_path)
            self.assertGreaterEqual(len(q_list), 5, f"Role {role} has fewer than 5 questions")
            for q in q_list:
                self.assertTrue(q['question'])
                self.assertTrue(q['reference_answer'])
                self.assertTrue(q['keywords'])
                self.assertIn(q['difficulty'], ['Easy', 'Medium', 'Hard'])

    # 4. Candidate Creation and Validation
    def test_candidate_creation_valid(self):
        with self.client:
            response = self.client.post('/candidate', data={
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'role': 'Python Developer',
                'experience_level': 'Fresher'
            }, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn('Question 1 of 5', response.data.decode('utf-8'))

    def test_candidate_creation_invalid_email(self):
        response = self.client.post('/candidate', data={
            'name': 'Jane Doe',
            'email': 'invalid-email-format',
            'role': 'Python Developer',
            'experience_level': 'Fresher'
        }, follow_redirects=True)
        content = response.data.decode('utf-8')
        self.assertIn('valid email address', content)

    # 5. NLP Preprocessing
    def test_nlp_preprocessing(self):
        sample = "Python is an interpreted, high-level programming language."
        prep = preprocess_pipeline(sample)
        self.assertEqual(prep['lowercase_text'], sample.lower())
        self.assertIn('python', prep['tokens'])
        self.assertIn('language', prep['lemmatized_tokens'])
        # Stopwords like 'is', 'an' should be filtered
        self.assertNotIn('is', prep['filtered_tokens'])
        self.assertNotIn('an', prep['filtered_tokens'])

    # 6. Keyword Extraction and Matching
    def test_keyword_matching(self):
        candidate_ans = "A child class inherits methods and attributes from a parent class in object-oriented programming."
        expected_kw = "inheritance, child class, parent class, attributes, methods, object-oriented"
        
        result = match_keywords(candidate_ans, expected_kw)
        self.assertIn('child class', result['matched_keywords'])
        self.assertIn('parent class', result['matched_keywords'])
        self.assertIn('attributes', result['matched_keywords'])
        self.assertIn('methods', result['matched_keywords'])
        self.assertGreater(result['keyword_score'], 60.0)

    # 7. TF-IDF and Cosine Similarity
    def test_tfidf_cosine_similarity(self):
        text1 = "Inheritance allows a child class to acquire properties and methods from a parent class."
        text2 = "Inheritance allows a child class to inherit attributes and methods from a parent class."
        text_disjoint = "Cooking pasta requires boiling water and adding salt with tomato sauce."

        sim_high = compute_tfidf_similarity(text1, text2)
        sim_low = compute_tfidf_similarity(text1, text_disjoint)

        self.assertGreater(sim_high, 50.0)
        self.assertLess(sim_low, 15.0)

    # 8. Relevance and Completeness
    def test_relevance_and_completeness(self):
        q = "What is Python?"
        ref = "Python is a high-level interpreted programming language with clean syntax and object-oriented capabilities."
        kw = "high-level, interpreted, programming language, object-oriented, clean syntax"

        good_ans = "Python is a high-level interpreted programming language. It has clean syntax and supports object-oriented code."
        poor_ans = "It is code."

        res_good = evaluate_answer(good_ans, ref, q, kw)
        res_poor = evaluate_answer(poor_ans, ref, q, kw)

        self.assertGreater(res_good['relevance_score'], res_poor['relevance_score'])
        self.assertGreater(res_good['completeness_score'], res_poor['completeness_score'])
        self.assertGreater(res_good['final_score'], res_poor['final_score'])

    # 9. Language Quality / Grammar
    def test_language_quality(self):
        good_text = "Python is a versatile programming language used for automation and data science."
        bad_text = "language language language language language"
        very_short = "yes"

        score_good = analyze_language_quality(good_text)
        score_bad = analyze_language_quality(bad_text)
        score_short = analyze_language_quality(very_short)

        self.assertGreater(score_good, score_bad)
        self.assertGreater(score_good, score_short)

    # 10. Scoring Formula Verification
    def test_scoring_formula_exact_weights(self):
        """
        Verify: final_score = (relevance * 0.25) + (keyword_score * 0.25) + (similarity * 0.25) + (completeness * 0.15) + (grammar * 0.10)
        """
        q = "What is inheritance?"
        ref = "Inheritance allows a child class to inherit properties from a parent class."
        kw = "child class, parent class, inheritance, properties"
        ans = "Inheritance allows a child class to inherit attributes from a parent class."

        res = evaluate_answer(ans, ref, q, kw)
        expected_final = round(
            (res['relevance_score'] * 0.25) +
            (res['keyword_score'] * 0.25) +
            (res['similarity_score'] * 0.25) +
            (res['completeness_score'] * 0.15) +
            (res['grammar_score'] * 0.10),
            2
        )
        self.assertEqual(res['final_score'], expected_final)
        self.assertTrue(0.0 <= res['final_score'] <= 100.0)

    # 11. Performance Level Mapping
    def test_performance_level_mapping(self):
        self.assertEqual(get_performance_level(95.0), "Excellent")
        self.assertEqual(get_performance_level(85.0), "Very Good")
        self.assertEqual(get_performance_level(75.0), "Good")
        self.assertEqual(get_performance_level(65.0), "Average")
        self.assertEqual(get_performance_level(45.0), "Needs Improvement")

    # 12. Feedback Generation Logic
    def test_feedback_generation(self):
        # Low keyword score
        fb_low_kw = generate_feedback({
            "final_score": 50.0, "relevance_score": 40.0, "keyword_score": 20.0,
            "similarity_score": 30.0, "completeness_score": 40.0, "grammar_score": 50.0
        }, missed_keywords=["GIL", "mutex"])
        self.assertIn("missed several important technical concepts", fb_low_kw)

        # High score
        fb_high = generate_feedback({
            "final_score": 92.0, "relevance_score": 90.0, "keyword_score": 95.0,
            "similarity_score": 90.0, "completeness_score": 90.0, "grammar_score": 95.0
        }, matched_keywords=["inheritance", "polymorphism"])
        self.assertIn("Strong answer", fb_high)

    # 13. Database Operations
    def test_database_storage_and_report(self):
        cand_id = database.create_candidate("Alice Smith", "alice@example.com", "Software Developer", "Intermediate", self.temp_db_path)
        self.assertIsNotNone(cand_id)

        interview_id = database.create_interview(cand_id, self.temp_db_path)
        self.assertIsNotNone(interview_id)

        q_list = database.get_questions_by_role("Software Developer", limit=1, db_path=self.temp_db_path)
        qid = q_list[0]['id']

        ans_id = database.save_answer(interview_id, qid, "SOLID principles make software robust.", self.temp_db_path)
        self.assertIsNotNone(ans_id)

        eval_id = database.save_evaluation(ans_id, 80.0, 75.0, 70.0, 80.0, 90.0, 77.5, "Good answer.", self.temp_db_path)
        self.assertIsNotNone(eval_id)

        database.update_interview_score(interview_id, 77.5, "Good", self.temp_db_path)

        report = database.get_interview_report(interview_id, self.temp_db_path)
        self.assertEqual(report['candidate_name'], "Alice Smith")
        self.assertEqual(report['overall_score'], 77.5)
        self.assertEqual(report['performance'], "Good")
        self.assertEqual(len(report['qa_list']), 1)

    # 14. Demo Flow End-to-End
    def test_demo_flow_end_to_end(self):
        response = self.client.get('/demo', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Alex Kumar', content)
        self.assertIn('Python Developer', content)
        self.assertIn('Overall', content)
        self.assertIn('Performance Level', content)
        self.assertIn('Radar', content)

    # 15. History Page
    def test_history_page(self):
        # Create an interview first
        cand_id = database.create_candidate("Bob Stone", "bob@example.com", "Java Developer", "Fresher", self.temp_db_path)
        iv_id = database.create_interview(cand_id, self.temp_db_path)
        database.update_interview_score(iv_id, 82.0, "Very Good", self.temp_db_path)

        response = self.client.get('/history')
        self.assertEqual(response.status_code, 200)
        content = response.data.decode('utf-8')
        self.assertIn('Bob Stone', content)
        self.assertIn('Java Developer', content)
        self.assertIn('82.0', content)

    # 16. E2E Form Submission
    def test_interview_form_submission_e2e(self):
        # Register candidate
        self.client.post('/candidate', data={
            'name': 'E2E Tester',
            'email': 'tester@example.com',
            'role': 'Python Developer',
            'experience_level': 'Fresher'
        }, follow_redirects=False)

        with self.client.session_transaction() as sess:
            iv_id = sess['interview_id']

        questions = database.get_questions_by_role('Python Developer', limit=5, db_path=self.temp_db_path)
        form_payload = {'interview_id': str(iv_id)}
        for q in questions:
            form_payload[f'answer_{q["id"]}'] = f"Python explanation covering {q['keywords']}"

        res = self.client.post('/interview/answer', data=form_payload, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Interview Results', res.data.decode('utf-8'))
        self.assertIn('E2E Tester', res.data.decode('utf-8'))

if __name__ == '__main__':
    unittest.main()
