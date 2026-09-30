import re
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import wordnet

# Fallback English stopwords list in case of network/NLTK unavailability
FALLBACK_STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "aren't", "as", "at", "be", "because", "been", "before", "being",
    "below", "between", "both", "but", "by", "can", "cannot", "could", "couldn't",
    "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down", "during",
    "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't",
    "have", "haven't", "having", "he", "he'd", "he'll", "he's", "her", "here",
    "here's", "hers", "herself", "him", "himself", "his", "how", "how's", "i",
    "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it", "it's",
    "its", "itself", "let's", "me", "more", "most", "mustn't", "my", "myself",
    "no", "nor", "not", "of", "off", "on", "once", "only", "or", "other", "ought",
    "our", "ours", "ourselves", "out", "over", "own", "same", "shan't", "she",
    "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such",
    "than", "that", "that's", "the", "their", "theirs", "them", "themselves",
    "then", "there", "there's", "these", "they", "they'd", "they'll", "they're",
    "they've", "this", "those", "through", "to", "too", "under", "until", "up",
    "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were",
    "weren't", "what", "what's", "when", "when's", "where", "where's", "which",
    "while", "who", "who's", "whom", "why", "why's", "with", "won't", "would",
    "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your", "yours",
    "yourself", "yourselves"
}

_RESOURCES_VERIFIED = False

def ensure_nltk_resources():
    """
    Ensure all necessary NLTK packages are downloaded safely.
    Catches errors gracefully to avoid runtime crashes.
    """
    global _RESOURCES_VERIFIED
    if _RESOURCES_VERIFIED:
        return

    resources = [
        ('tokenizers/punkt', 'punkt'),
        ('tokenizers/punkt_tab', 'punkt_tab'),
        ('corpora/stopwords', 'stopwords'),
        ('corpora/wordnet', 'wordnet'),
        ('corpora/omw-1.4', 'omw-1.4'),
        ('taggers/averaged_perceptron_tagger', 'averaged_perceptron_tagger'),
        ('taggers/averaged_perceptron_tagger_eng', 'averaged_perceptron_tagger_eng'),
    ]

    for path, pkg in resources:
        try:
            nltk.data.find(path)
        except (LookupError, Exception):
            try:
                nltk.download(pkg, quiet=True)
            except Exception:
                pass

    _RESOURCES_VERIFIED = True

# Call on import
ensure_nltk_resources()

lemmatizer = WordNetLemmatizer()

def get_wordnet_pos(treebank_tag):
    """
    Map POS tag to first character lemmatize() accepts.
    """
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def tokenize_words(text):
    """
    Robust word tokenization using NLTK or regex fallback.
    """
    try:
        return word_tokenize(text)
    except Exception:
        return re.findall(r'\b[a-zA-Z0-9_\-\+\#\.]+\b', text)

def tokenize_sentences(text):
    """
    Robust sentence tokenization using NLTK or regex fallback.
    """
    try:
        return sent_tokenize(text)
    except Exception:
        sentences = re.split(r'[.!?]+(?:\s+|$)', text)
        return [s.strip() for s in sentences if s.strip()]

def get_stopwords_set():
    """
    Get stopwords from NLTK or fallback set.
    """
    try:
        return set(stopwords.words('english'))
    except Exception:
        return FALLBACK_STOPWORDS

def preprocess_pipeline(text):
    """
    Complete classical NLP preprocessing pipeline:
    Candidate Answer -> Lowercase -> Tokenization -> Stopword Removal -> POS Tagging -> Lemmatization.
    """
    if not text or not isinstance(text, str):
        return {
            "raw_text": "",
            "lowercase_text": "",
            "tokens": [],
            "filtered_tokens": [],
            "lemmatized_tokens": [],
            "lemmatized_text": "",
            "pos_tags": [],
            "sentences": []
        }

    raw_text = text.strip()
    lowercase_text = raw_text.lower()
    sentences = tokenize_sentences(raw_text)

    # Tokenize
    raw_tokens = tokenize_words(lowercase_text)

    # Filter punctuation and keep alphanumeric words or known tech symbols like c++, c#
    clean_tokens = [
        t for t in raw_tokens 
        if t not in string.punctuation and re.search(r'[a-zA-Z0-9]', t)
    ]

    # Stopword removal
    stop_words = get_stopwords_set()
    filtered_tokens = [t for t in clean_tokens if t not in stop_words]

    # POS Tagging
    try:
        pos_tags = nltk.pos_tag(clean_tokens)
    except Exception:
        pos_tags = [(t, 'NN') for t in clean_tokens]

    # POS-aware Lemmatization
    lemmatized_tokens = []
    for word, tag in pos_tags:
        if word not in stop_words:
            wn_pos = get_wordnet_pos(tag)
            try:
                lemma = lemmatizer.lemmatize(word, wn_pos)
            except Exception:
                lemma = word
            lemmatized_tokens.append(lemma)

    lemmatized_text = " ".join(lemmatized_tokens)

    return {
        "raw_text": raw_text,
        "lowercase_text": lowercase_text,
        "tokens": clean_tokens,
        "filtered_tokens": filtered_tokens,
        "lemmatized_tokens": lemmatized_tokens,
        "lemmatized_text": lemmatized_text,
        "pos_tags": pos_tags,
        "sentences": sentences
    }
