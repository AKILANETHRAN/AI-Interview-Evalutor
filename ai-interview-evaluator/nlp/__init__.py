"""
AI Interview Evaluator - NLP Engine
Classical NLP pipeline using NLTK and scikit-learn for evaluating technical interview answers.
"""

from .preprocessing import preprocess_pipeline, ensure_nltk_resources
from .keyword_extractor import match_keywords, extract_keywords
from .similarity import compute_tfidf_similarity, compute_relevance_score
from .feedback import generate_feedback, get_performance_level
from .evaluator import evaluate_answer

__all__ = [
    "preprocess_pipeline",
    "ensure_nltk_resources",
    "match_keywords",
    "extract_keywords",
    "compute_tfidf_similarity",
    "compute_relevance_score",
    "generate_feedback",
    "get_performance_level",
    "evaluate_answer",
]
