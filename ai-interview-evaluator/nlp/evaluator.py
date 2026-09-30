import re
from .preprocessing import preprocess_pipeline
from .keyword_extractor import match_keywords
from .similarity import compute_tfidf_similarity, compute_relevance_score
from .feedback import generate_feedback, get_performance_level

def analyze_completeness(candidate_text, reference_text, keyword_score):
    """
    Evaluate completeness by assessing concept coverage and technical depth
    relative to the reference answer.
    """
    if not candidate_text or not candidate_text.strip():
        return 0.0

    cand_prep = preprocess_pipeline(candidate_text)
    ref_prep = preprocess_pipeline(reference_text)

    cand_tokens = set(cand_prep["filtered_tokens"])
    ref_tokens = set(ref_prep["filtered_tokens"])

    # 1. Concept / token coverage of reference key lemmas
    if ref_tokens:
        token_coverage = min(1.0, len(cand_tokens & ref_tokens) / (len(ref_tokens) * 0.65)) * 100.0
    else:
        token_coverage = 100.0

    # 2. Elaboration depth ratio (word count vs reference word count)
    cand_word_count = len(cand_prep["tokens"])
    ref_word_count = len(ref_prep["tokens"])
    
    if ref_word_count > 0:
        depth_ratio = min(1.0, cand_word_count / (ref_word_count * 0.75)) * 100.0
    else:
        depth_ratio = 100.0

    # 3. Blend keyword score (40%), token coverage (35%), and depth ratio (25%)
    raw_completeness = (keyword_score * 0.40) + (token_coverage * 0.35) + (depth_ratio * 0.25)
    return round(max(0.0, min(100.0, raw_completeness)), 2)

def analyze_language_quality(text):
    """
    Evaluate basic grammar and language quality using structural heuristics:
    - Capitalization at sentence starts
    - Proper terminal punctuation (. ! ?)
    - Word count sufficiency
    - POS tag structural diversity (presence of nouns and verbs)
    - Absence of excessive token repetition
    """
    if not text or not text.strip():
        return 0.0

    prep = preprocess_pipeline(text)
    sentences = prep["sentences"]
    tokens = prep["tokens"]
    pos_tags = prep["pos_tags"]

    if not tokens:
        return 0.0

    score = 100.0

    # 1. Word count check (penalize extreme brevity)
    if len(tokens) < 5:
        score -= 40.0
    elif len(tokens) < 10:
        score -= 20.0

    # 2. Sentence capitalization
    valid_starts = 0
    valid_ends = 0
    for s in sentences:
        s_clean = s.strip()
        if s_clean and s_clean[0].isupper():
            valid_starts += 1
        if s_clean and s_clean[-1] in '.!?':
            valid_ends += 1

    total_s = max(1, len(sentences))
    if (valid_starts / total_s) < 0.6:
        score -= 15.0
    if (valid_ends / total_s) < 0.5:
        score -= 10.0

    # 3. Grammatical structure (must have nouns and verbs)
    has_noun = any(tag.startswith('N') for _, tag in pos_tags)
    has_verb = any(tag.startswith('V') for _, tag in pos_tags)

    if not has_noun:
        score -= 25.0
    if not has_verb:
        score -= 25.0

    # 4. Excessive repetition penalty
    from collections import Counter
    counts = Counter(tokens)
    if counts:
        most_common_word, highest_freq = counts.most_common(1)[0]
        if highest_freq / len(tokens) > 0.4 and len(tokens) > 5:
            score -= 30.0

    return round(max(10.0, min(100.0, score)), 2)

def evaluate_answer(candidate_answer, reference_answer, question, expected_keywords):
    """
    Execute the full NLP evaluation pipeline on a candidate answer:
    1. Preprocessing (NLTK Tokenization, Lemmatization, Stopwords)
    2. Keyword Extraction & Matching
    3. TF-IDF & Cosine Similarity
    4. Relevance Scoring
    5. Completeness Scoring
    6. Grammar & Language Quality Scoring
    7. Final Score = (Relevance * 0.25) + (Keywords * 0.25) + (Similarity * 0.25) + (Completeness * 0.15) + (Grammar * 0.10)
    8. Qualitative Constructive Feedback
    """
    cleaned_answer = candidate_answer.strip() if candidate_answer else ""

    if not cleaned_answer:
        return {
            "relevance_score": 0.0,
            "keyword_score": 0.0,
            "similarity_score": 0.0,
            "completeness_score": 0.0,
            "grammar_score": 0.0,
            "final_score": 0.0,
            "performance": "Needs Improvement",
            "feedback": "No answer provided. Please provide a substantive technical response.",
            "matched_keywords": [],
            "missed_keywords": [k.strip() for k in expected_keywords.split(",") if k.strip()] if isinstance(expected_keywords, str) else list(expected_keywords or [])
        }

    # 1. Keyword Match
    kw_result = match_keywords(cleaned_answer, expected_keywords)
    keyword_score = kw_result["keyword_score"]
    matched_keywords = kw_result["matched_keywords"]
    missed_keywords = kw_result["missed_keywords"]

    # 2. Similarity (TF-IDF Cosine Similarity)
    similarity_score = compute_tfidf_similarity(cleaned_answer, reference_answer)

    # 3. Relevance
    relevance_score = compute_relevance_score(cleaned_answer, reference_answer, question, expected_keywords)

    # 4. Completeness
    completeness_score = analyze_completeness(cleaned_answer, reference_answer, keyword_score)

    # 5. Grammar & Language Quality
    grammar_score = analyze_language_quality(cleaned_answer)

    # 6. Final Score Calculation (exact formula weights):
    # final_score = (relevance * 0.25) + (keyword_score * 0.25) + (similarity * 0.25) + (completeness * 0.15) + (grammar * 0.10)
    final_score = (
        (relevance_score * 0.25) +
        (keyword_score * 0.25) +
        (similarity_score * 0.25) +
        (completeness_score * 0.15) +
        (grammar_score * 0.10)
    )
    final_score = round(max(0.0, min(100.0, final_score)), 2)

    # 7. Performance Tier
    performance = get_performance_level(final_score)

    # 8. Feedback Generation
    scores_dict = {
        "final_score": final_score,
        "relevance_score": relevance_score,
        "keyword_score": keyword_score,
        "similarity_score": similarity_score,
        "completeness_score": completeness_score,
        "grammar_score": grammar_score
    }
    feedback = generate_feedback(scores_dict, matched_keywords, missed_keywords)

    return {
        "relevance_score": relevance_score,
        "keyword_score": keyword_score,
        "similarity_score": similarity_score,
        "completeness_score": completeness_score,
        "grammar_score": grammar_score,
        "final_score": final_score,
        "performance": performance,
        "feedback": feedback,
        "matched_keywords": matched_keywords,
        "missed_keywords": missed_keywords
    }
