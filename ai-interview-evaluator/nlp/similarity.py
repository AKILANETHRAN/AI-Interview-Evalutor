"""
Similarity and Relevance Analysis using Classical NLP.

NOTE ON METHODOLOGY:
This module uses classical NLP techniques (TF-IDF vectorization and Cosine Similarity
via scikit-learn). TF-IDF measures term frequency-inverse document frequency lexical
and n-gram overlap; it does NOT provide deep contextual semantic understanding like
modern dense transformers/LLMs. It is documented here as an objective, transparent,
and efficient statistical NLP baseline.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .preprocessing import preprocess_pipeline

def compute_tfidf_similarity(candidate_text, reference_text):
    """
    Compute Cosine Similarity between candidate answer and reference answer
    using scikit-learn's TfidfVectorizer with unigrams and bigrams.
    
    Returns:
        float: Similarity score between 0.0 and 100.0.
    """
    if not candidate_text or not reference_text:
        return 0.0

    cand_prep = preprocess_pipeline(candidate_text)
    ref_prep = preprocess_pipeline(reference_text)

    cand_proc = cand_prep["lemmatized_text"]
    ref_proc = ref_prep["lemmatized_text"]

    if not cand_proc.strip() or not ref_proc.strip():
        return 0.0

    try:
        # Standard TF-IDF vectorizer
        tfidf_vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True)
        tfidf_mat = tfidf_vec.fit_transform([cand_proc, ref_proc])
        cos_tfidf = float(cosine_similarity(tfidf_mat[0:1], tfidf_mat[1:2])[0][0])

        # Normalized Term Frequency vectorizer (pure n-gram vector space angle)
        tf_vec = TfidfVectorizer(ngram_range=(1, 2), use_idf=False, norm='l2')
        tf_mat = tf_vec.fit_transform([cand_proc, ref_proc])
        cos_tf = float(cosine_similarity(tf_mat[0:1], tf_mat[1:2])[0][0])

        # Blend both representations to capture both n-gram overlap and distinctiveness
        combined_sim = (cos_tfidf * 0.45) + (cos_tf * 0.55)
        sim_val = max(0.0, min(1.0, combined_sim))
        return round(sim_val * 100.0, 2)
    except Exception:
        c_set = set(cand_prep["filtered_tokens"])
        r_set = set(ref_prep["filtered_tokens"])
        if not c_set or not r_set:
            return 0.0
        jaccard = len(c_set & r_set) / len(c_set | r_set)
        return round(jaccard * 100.0, 2)

def compute_relevance_score(candidate_text, reference_text, question_text, expected_keywords=None):
    """
    Compute Relevance score evaluating how pertinent the candidate answer is
    to the prompt and reference answer.
    
    Combines:
    1. Cosine similarity to the reference answer (weight: 0.40)
    2. Cosine similarity to the question prompt (weight: 0.30)
    3. Content keyword overlap ratio against reference key concepts (weight: 0.30)
    
    Returns:
        float: Relevance score between 0.0 and 100.0.
    """
    if not candidate_text or not candidate_text.strip():
        return 0.0

    cand_prep = preprocess_pipeline(candidate_text)
    ref_prep = preprocess_pipeline(reference_text)
    q_prep = preprocess_pipeline(question_text)

    # 1. Similarity to reference answer
    ref_sim = compute_tfidf_similarity(candidate_text, reference_text)

    # 2. Similarity to question prompt (does answer address question subject?)
    try:
        q_vec = TfidfVectorizer(ngram_range=(1, 2), use_idf=False, norm='l2')
        tfidf_q = q_vec.fit_transform([cand_prep["lemmatized_text"], q_prep["lemmatized_text"]])
        q_sim = float(cosine_similarity(tfidf_q[0:1], tfidf_q[1:2])[0][0]) * 100.0
    except Exception:
        q_sim = 0.0

    # 3. Content overlap with reference tokens
    cand_tokens = set(cand_prep["lemmatized_tokens"])
    ref_tokens = set(ref_prep["lemmatized_tokens"])
    
    if ref_tokens:
        overlap = len(cand_tokens & ref_tokens) / len(ref_tokens)
        overlap_score = min(100.0, overlap * 150.0)
    else:
        overlap_score = ref_sim

    # Blend: reference similarity + question focus + content overlap
    raw_relevance = (ref_sim * 0.40) + (q_sim * 0.30) + (overlap_score * 0.30)
    
    # Floor relevance at reference similarity * 0.9 if answer strongly aligns with reference
    relevance = max(ref_sim * 0.90, raw_relevance)
    
    return round(max(0.0, min(100.0, relevance)), 2)
