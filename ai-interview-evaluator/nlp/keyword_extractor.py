import re
from collections import Counter
from .preprocessing import preprocess_pipeline, lemmatizer, get_wordnet_pos

def normalize_keyword(kw):
    """
    Normalize a keyword phrase: lowercase, replace hyphens with spaces, remove punctuation.
    """
    clean = re.sub(r'[^\w\s]', ' ', kw.lower()).strip()
    return re.sub(r'\s+', ' ', clean)

def lemmatize_phrase(phrase):
    """
    Lemmatize each word in a keyword phrase.
    """
    words = phrase.split()
    lemmas = []
    for w in words:
        try:
            lemma = lemmatizer.lemmatize(w)
        except Exception:
            lemma = w
        lemmas.append(lemma)
    return " ".join(lemmas)

def match_keywords(candidate_text, expected_keywords):
    """
    Match candidate answer against expected keywords list or comma-separated string.
    Supports single-word and multi-word keywords, lemmatized matching, and variations.
    
    Returns:
    {
        "matched_keywords": list of matched keywords,
        "missed_keywords": list of missed keywords,
        "keyword_score": float (0.0 to 100.0),
        "total_expected": int,
        "matched_count": int
    }
    """
    if isinstance(expected_keywords, str):
        keywords_list = [k.strip() for k in expected_keywords.split(",") if k.strip()]
    elif isinstance(expected_keywords, (list, tuple, set)):
        keywords_list = [str(k).strip() for k in expected_keywords if str(k).strip()]
    else:
        keywords_list = []

    if not keywords_list:
        return {
            "matched_keywords": [],
            "missed_keywords": [],
            "keyword_score": 100.0,
            "total_expected": 0,
            "matched_count": 0
        }

    prep = preprocess_pipeline(candidate_text)
    candidate_raw_lower = candidate_text.lower()
    candidate_lemmatized_text = prep["lemmatized_text"]
    candidate_lemmatized_tokens = set(prep["lemmatized_tokens"])
    candidate_tokens = set(prep["tokens"])

    matched = []
    missed = []

    for kw in keywords_list:
        norm_kw = normalize_keyword(kw)
        lemma_kw = lemmatize_phrase(norm_kw)
        kw_words = norm_kw.split()

        # 1. Direct phrase containment in lowercased candidate text
        pattern = r'\b' + re.escape(norm_kw) + r'\b'
        hyphen_pattern = r'\b' + re.escape(norm_kw.replace(" ", "-")) + r'\b'
        no_space_pattern = r'\b' + re.escape(norm_kw.replace(" ", "")) + r'\b'

        if (re.search(pattern, candidate_raw_lower) or 
            re.search(hyphen_pattern, candidate_raw_lower) or
            re.search(no_space_pattern, candidate_raw_lower)):
            matched.append(kw)
            continue

        # 2. Lemmatized phrase containment in lemmatized text
        lemma_pattern = r'\b' + re.escape(lemma_kw) + r'\b'
        if re.search(lemma_pattern, candidate_lemmatized_text):
            matched.append(kw)
            continue

        # 3. For single-word keywords, check token/lemma sets
        if len(kw_words) == 1:
            w = kw_words[0]
            w_lemma = lemmatize_phrase(w)
            if w in candidate_tokens or w_lemma in candidate_lemmatized_tokens:
                matched.append(kw)
                continue

        # 4. For multi-word keywords, if every constituent significant lemma is present
        if len(kw_words) > 1:
            all_found = True
            for part in kw_words:
                part_lemma = lemmatize_phrase(part)
                if part not in candidate_tokens and part_lemma not in candidate_lemmatized_tokens:
                    all_found = False
                    break
            if all_found:
                matched.append(kw)
                continue

        missed.append(kw)

    total = len(keywords_list)
    matched_count = len(matched)
    score = round((matched_count / total) * 100.0, 2) if total > 0 else 0.0

    return {
        "matched_keywords": matched,
        "missed_keywords": missed,
        "keyword_score": min(score, 100.0),
        "total_expected": total,
        "matched_count": matched_count
    }

def extract_keywords(text, top_n=10):
    """
    Extract salient candidate keywords using POS tagging (nouns and adjectives).
    """
    prep = preprocess_pipeline(text)
    pos_tags = prep["pos_tags"]
    
    # Target Nouns (NN, NNS, NNP, NNPS) and Adjectives (JJ, JJR, JJS)
    candidate_words = [
        word for word, tag in pos_tags 
        if tag.startswith('N') or tag.startswith('J')
    ]
    
    # Filter stopwords and short tokens
    stop_words = set(prep["lowercase_text"])
    meaningful = [w for w in candidate_words if len(w) > 2]
    
    counts = Counter(meaningful)
    return [word for word, _ in counts.most_common(top_n)]
