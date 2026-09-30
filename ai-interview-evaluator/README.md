# AI Interview Evaluator Using NLP

> **Practice. Analyze. Improve.**  
> An automated mock technical interview evaluation system powered by classical Natural Language Processing (NLP), Flask, SQLite, and Chart.js.

---

## 1. Project Overview
The **AI Interview Evaluator Using NLP** is a full-stack technical interview assessment application. It presents candidates with curated engineering interview questions across 6 core industry domains, evaluates candidate answers using a deterministic, multi-stage classical NLP pipeline (Tokenization, Stopword Removal, Lemmatization, POS Tagging, Keyword Extraction, TF-IDF Vectorization, Cosine Similarity, Relevance, Completeness, and Language Quality), computes objective performance scores, generates actionable constructive feedback, and visualizes multi-dimensional skill analytics on a modern dashboard.

---

## 2. Problem Statement
Traditional technical screening interviews suffer from several critical shortcomings:
1. **Human Evaluation Inconsistency:** Different interviewers grade the same answer with varying bias and subjectivity.
2. **Delayed or Opaque Feedback:** Candidates rarely receive immediate, granular breakdowns of why their response fell short.
3. **Black-box AI Hallucinations:** Generative LLMs often output inconsistent grades across runs, hallucinate inaccuracies, and are costly or complex to run locally.
4. **Lack of Objective Baseline:** Teams need an explainable, auditable, and transparent NLP scoring engine that evaluates answers against verified benchmark answers.

---

## 3. Objectives
- Provide a fully automated, 100% reproducible technical mock interview experience.
- Implement an explainable classical NLP evaluation engine using NLTK and scikit-learn without black-box randomness.
- Assess candidate answers across 5 weighted dimensions: **Relevance (25%)**, **Keyword Coverage (25%)**, **Similarity (25%)**, **Completeness (15%)**, and **Language Quality (10%)**.
- Persist candidates, interview sessions, answers, and evaluations in a normalized SQLite database with foreign key constraints.
- Render multi-dimensional skill radar charts and question-by-question trajectory charts via Chart.js.
- Maintain a full historical archive of candidate evaluations for longitudinal progress tracking.

---

## 4. Key Features
- **6 Supported Engineering Roles:** Software Developer, Java Developer, Python Developer, Web Developer, Data Analyst, and Machine Learning Engineer.
- **42 Curated Technical Questions:** Spanning Easy, Medium, and Hard tiers, complete with benchmark reference answers and key domain terminology.
- **Interactive Question Stepper:** Clean 5-question carousel with live word counter, character counter, animated progress bar, and empty answer validation.
- **Explainable Scoring Engine:** Deterministic calculation using the exact required mathematical formula.
- **Qualitative Feedback Engine:** Actionable guidance identifying covered technical terminology, missing core concepts, and structural recommendations.
- **Performance Tier Mapping:** Standardized grading from *Excellent* (90-100) down to *Needs Improvement* (<60).
- **One-Click Automated Demo:** Evaluates 5 sample Python Developer answers through the genuine live NLP pipeline and persists the report.
- **Interactive Result Dashboard:** Chart.js Radar Chart, Question-wise Bar Chart, score pills, and expandable candidate vs. benchmark comparisons.
- **Searchable Interview History:** Filter past interview sessions by candidate name, email, or targeted job role.
- **Health & API Endpoints:** JSON health metrics and RESTful access to interview records.

---

## 5. Technology Stack
- **Frontend:**
  - HTML5 (Semantic document hierarchy, accessible forms, meta tags)
  - Vanilla CSS3 (Custom design system, AI-themed dark glassmorphism, responsive grid, glowing accents, Inter typography)
  - Modern JavaScript (ES6+, DOM manipulation, dynamic stepper navigation, input verification)
  - Chart.js (Interactive Multi-Dimensional Radar and Bar visualizations)
- **Backend:**
  - Python 3.10+ / 3.12+ / 3.14+
  - Flask (REST routing, session state, template rendering, JSON responses)
  - Gunicorn (WSGI HTTP Server for production deployment)
- **Database:**
  - SQLite3 (Relational persistence, `PRAGMA foreign_keys = ON;`, parameterized SQL queries)
- **Natural Language Processing (NLP):**
  - **NLTK:** Safe resource management (`punkt`, `stopwords`, `wordnet`, `averaged_perceptron_tagger`), word and sentence tokenization, stopword filtering, POS tagging, WordNet POS-aware lemmatization.
  - **scikit-learn:** `TfidfVectorizer` (unigrams + bigrams), `cosine_similarity`.
  - **NumPy:** Vector computations and numerical matrix scaling.

---

## 6. System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       Web Browser UI                        │
│   Landing Page  •  Candidate Setup  •  Live Stepper Room    │
│            Result Dashboard (Chart.js)  •  History          │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP GET / POST
┌──────────────────────────────▼──────────────────────────────┐
│                    Flask Application (app.py)               │
│  - Session Handling       - Form / JSON Validation          │
│  - RESTful API Routes     - Error Handling (404/500)        │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
┌──────────────▼─────────────┐   ┌─────────────▼──────────────┐
│   SQLite Database Engine   │   │    NLP Evaluation Engine   │
│       (database.py)        │   │           (nlp/)           │
│  - candidates              │   │  - Preprocessing (NLTK)    │
│  - questions (42 seeded)   │   │  - Keyword Extractor       │
│  - interviews              │   │  - TF-IDF & Cosine Sim     │
│  - answers                 │   │  - Completeness & Grammar  │
│  - evaluations             │   │  - Feedback Generator      │
└────────────────────────────┘   └────────────────────────────┘
```

---

## 7. NLP Evaluation Pipeline
For every submitted candidate answer:

```
Candidate Answer Text
         ↓
Lowercase Normalization
         ↓
Sentence & Word Tokenization (NLTK)
         ↓
Stopword Removal (Standard English Stopwords)
         ↓
POS Tagging (Penn Treebank Tagger)
         ↓
POS-Aware Lemmatization (WordNet Lemmatizer)
         ↓
Keyword Extraction & N-Gram Matching
         ↓
TF-IDF Vector Space Representation (scikit-learn)
         ↓
Cosine Similarity Computation
         ↓
Relevance Analysis (Question + Reference Alignment)
         ↓
Completeness Analysis (Concept Coverage & Depth)
         ↓
Language Quality Heuristics (Grammar, POS Diversity, Punctuation)
         ↓
Weighted Final Score Calculation (0 - 100)
         ↓
Deterministic Constructive Feedback Generation
```

> **Classical NLP Notice:** This system purposefully applies classical statistical NLP (TF-IDF vector space modeling and lexical overlap). TF-IDF measures term frequency and inverse document frequency across unigram and bigram tokens; it does not claim to provide deep contextual neural understanding like dense transformers or Large Language Models. This makes the system transparent, reproducible, lightweight, and auditable.

---

## 8. Scoring Formula & Weights
Component scores are independently calculated on a scale of **0 to 100**:

$$\text{final\_score} = (\text{relevance} \times 0.25) + (\text{keyword\_score} \times 0.25) + (\text{similarity} \times 0.25) + (\text{completeness} \times 0.15) + (\text{grammar} \times 0.10)$$

| Component | Weight | Methodology |
|---|:---:|---|
| **Relevance** | 25% | Multi-factor alignment measuring topical focus on question prompt, cosine proximity to reference answer, and reference concept coverage. |
| **Keyword Match** | 25% | Lemmatized n-gram search matching domain technical keywords (e.g., "object-oriented", "global interpreter lock", "virtual dom"). |
| **Cosine Similarity** | 25% | Vector space cosine angle using `TfidfVectorizer(ngram_range=(1,2))` with sublinear TF scaling. |
| **Completeness** | 15% | Concept coverage ratio combined with technical elaboration depth relative to the reference benchmark. |
| **Language Quality** | 10% | Structural integrity, sentence boundaries, capitalization, terminal punctuation, POS balance (nouns & verbs), and repetition penalty. |

### Performance Tiers:
- **90 – 100:** Excellent
- **80 – 89:** Very Good
- **70 – 79:** Good
- **60 – 69:** Average
- **Below 60:** Needs Improvement

---

## 9. Database Design (SQLite)
Foreign keys are enforced on every connection using `PRAGMA foreign_keys = ON;`.

### Schema:
1. **`candidates`**
   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `name` (TEXT NOT NULL)
   - `email` (TEXT NOT NULL)
   - `role` (TEXT NOT NULL)
   - `experience_level` (TEXT NOT NULL)
   - `created_at` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

2. **`questions`**
   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `role` (TEXT NOT NULL)
   - `question` (TEXT NOT NULL)
   - `reference_answer` (TEXT NOT NULL)
   - `keywords` (TEXT NOT NULL)
   - `difficulty` (TEXT NOT NULL: Easy, Medium, Hard)

3. **`interviews`**
   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `candidate_id` (INTEGER NOT NULL, FK → `candidates(id)`)
   - `date` (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)
   - `overall_score` (REAL DEFAULT 0.0)
   - `performance` (TEXT DEFAULT 'Pending')

4. **`answers`**
   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `interview_id` (INTEGER NOT NULL, FK → `interviews(id)`)
   - `question_id` (INTEGER NOT NULL, FK → `questions(id)`)
   - `candidate_answer` (TEXT NOT NULL)

5. **`evaluations`**
   - `id` (INTEGER PRIMARY KEY AUTOINCREMENT)
   - `answer_id` (INTEGER NOT NULL, FK → `answers(id)`)
   - `relevance_score` (REAL NOT NULL)
   - `keyword_score` (REAL NOT NULL)
   - `similarity_score` (REAL NOT NULL)
   - `completeness_score` (REAL NOT NULL)
   - `grammar_score` (REAL NOT NULL)
   - `final_score` (REAL NOT NULL)
   - `feedback` (TEXT NOT NULL)

---

## 10. Folder Structure

```
ai-interview-evaluator/
├── app.py                  # Flask web application and route definitions
├── database.py             # SQLite schema, connection helpers, and parameterized queries
├── seed_database.py        # Seed script containing 42 technical questions across 6 roles
├── requirements.txt        # Production dependency specifications
├── Procfile                # Gunicorn deployment configuration
├── README.md               # Complete architectural and operational documentation
│
├── nlp/
│   ├── __init__.py         # Package exports
│   ├── preprocessing.py    # NLTK tokenization, stopword removal, POS tagging, lemmatization
│   ├── keyword_extractor.py# Multi-word keyword matching and salient term extraction
│   ├── similarity.py       # scikit-learn TF-IDF vectorizer and cosine similarity
│   ├── evaluator.py        # Exact scoring formula, completeness, language heuristics
│   └── feedback.py         # Deterministic feedback generator and performance tier mapping
│
├── templates/
│   ├── index.html          # Hero landing page, feature highlights, pipeline overview
│   ├── candidate.html      # Candidate registration and role selection form
│   ├── interview.html      # Question carousel, progress bar, answer input room
│   ├── result.html         # Chart.js radar & bar dashboard, detailed question breakdown
│   └── history.html        # Searchable table of past interview sessions
│
├── static/
│   ├── css/
│   │   └── style.css       # Responsive dark-theme design system and glassmorphism
│   └── js/
│       └── script.js       # Stepper navigation, answer validation, Chart.js integrations
│
├── database/
│   └── interview.db        # SQLite database file (auto-created on first run)
│
└── tests/
    └── test_app.py         # 17 comprehensive automated unit and integration tests
```

---

## 11. Installation & Setup

### Prerequisites
- Python 3.10 or higher
- Git (optional)

### Step 1: Navigate to Project Directory
```bash
cd ai-interview-evaluator
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Seed Database (Optional — Auto-initializes on startup)
```bash
python seed_database.py
```

---

## 12. Running the Application

### Development Server:
```bash
python app.py
```
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

### Production Server (Linux / Mac / Container):
```bash
gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 120 app:app
```

---

## 13. Sample Demo Flow (`/demo`)
To verify the entire system instantly without manual typing, visit:
```
http://127.0.0.1:5000/demo
```
The demo automatically:
1. Registers candidate **Alex Kumar** (`alex@example.com`, Python Developer, Fresher).
2. Submits 5 realistic technical answers across Python concepts (Python overview, Inheritance, Decorators, Lists vs. Tuples, GIL).
3. Executes the full NLP evaluation pipeline on all 5 answers.
4. Stores candidate, interview, answers, and evaluations into SQLite.
5. Redirects to the generated Result Dashboard displaying the interactive Radar and Bar charts.

---

## 14. Automated Testing
Run the comprehensive test suite covering all 17 scenarios:
```bash
python -m unittest tests/test_app.py
```
### Test Coverage Highlights:
- [x] Home page route and content rendering
- [x] Candidate registration and validation (valid and invalid email)
- [x] Database seeding verification (42 questions across 6 roles)
- [x] NLP preprocessing (tokenization, stopword removal, lemmatization)
- [x] Multi-word and lemmatized keyword extraction
- [x] TF-IDF vectorization and cosine similarity
- [x] Relevance analysis and prompt alignment
- [x] Completeness analysis and technical depth checking
- [x] Grammar and language quality heuristics
- [x] Exact scoring formula weight verification (25/25/25/15/10)
- [x] Performance tier classification
- [x] Score-dependent constructive feedback generation
- [x] SQLite relational storage with foreign key constraints
- [x] End-to-end question submission form flow
- [x] Demo flow end-to-end execution
- [x] Historical report retrieval and search
- [x] Health check JSON endpoint

---

## 15. Deployment Guide (Render / Railway / Cloud)

### Deployment on Render:
1. Push the repository to GitHub.
2. Create a new **Web Service** on Render and connect your repository.
3. Set the **Root Directory** to `ai-interview-evaluator`.
4. Set the **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
5. Set the **Start Command**:
   ```bash
   gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
   ```
6. Add Environment Variables:
   - `SECRET_KEY`: `<Generate-a-random-secret-string>`
   - `PORT`: `10000` (or leave default assigned by platform)

### Deployment on Railway:
Railway automatically detects the `Procfile` and launches the Gunicorn server:
```
web: gunicorn --bind 0.0.0.0:$PORT --workers 2 --timeout 120 app:app
```

---

## 16. Limitations
1. **Lexical vs. Semantic Boundaries:** TF-IDF measures n-gram frequency and lexical overlap; it cannot detect synonyms not captured by lemmatization or WordNet synsets.
2. **Grammar Heuristic Scope:** Basic rule-based grammar analysis checks sentence boundaries, structural POS tags, and token diversity; it does not replace a full dependency parser.
3. **Fixed Question Pools:** Each role currently has a fixed bank of curated questions rather than dynamic real-time question generation.

---

## 17. Future Enhancements
- **Sentence-Transformers Embeddings:** Integrate local bi-encoder models (e.g. `all-MiniLM-L6-v2`) alongside TF-IDF for hybrid dense-sparse semantic retrieval.
- **Audio Voice Interviews:** Incorporate WebRTC speech-to-text (Whisper API) for real-time oral interview practice.
- **Resume-Driven Custom Questions:** Allow candidates to upload their PDF resume to dynamically tailor interview questions.
- **PDF Report Generation:** Provide downloadable, branded PDF certificates and assessment reports for university placement preparation.

---

## 18. Viva & Interview Questions

### Q1: What is the difference between Lemmatization and Stemming?
**Answer:** Stemming is a heuristic, rule-based approach (e.g., Porter Stemmer) that chops off suffixes (e.g., "running" → "run", "studies" → "studi"), often resulting in non-words. Lemmatization uses a morphological vocabulary and grammatical context (WordNet) to reduce words to their true dictionary base form or lemma (e.g., "better" with POS adjective → "good", "studies" → "study"). This project uses NLTK's `WordNetLemmatizer` with POS tag mapping.

### Q2: Why use TF-IDF and Cosine Similarity instead of simple word count?
**Answer:** Simple word count or raw keyword matching can be easily gamed by repeating words or using filler text. Term Frequency-Inverse Document Frequency (TF-IDF) balances how often a term appears in a document against how common it is across documents, giving higher weight to distinctive technical terms. Cosine similarity measures the angle between the two TF-IDF vectors rather than their magnitude, ensuring that longer answers are not artificially rewarded solely for length.

### Q3: How is Cosine Similarity mathematically defined?
**Answer:** Given two vectors $\mathbf{A}$ and $\mathbf{B}$:
$$\text{Cosine Similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\| \|\mathbf{B}\|} = \frac{\sum_{i=1}^{n} A_i B_i}{\sqrt{\sum_{i=1}^{n} A_i^2} \sqrt{\sum_{i=1}^{n} B_i^2}}$$
Values range from 0 (completely orthogonal/dissimilar) to 1 (identical direction in vector space). In our engine, this is scaled to a 0–100 percentage.

### Q4: Why does the system use parameterized SQL queries?
**Answer:** Parameterized queries (using `?` placeholders) ensure that user input is treated strictly as data rather than executable SQL code, completely preventing SQL Injection attacks.

### Q5: How is SQLite configured for relational integrity?
**Answer:** By default, SQLite does not enforce foreign keys for backward compatibility. In `database.py`, every connection explicitly executes `PRAGMA foreign_keys = ON;`, ensuring cascading deletes and referential integrity between candidates, interviews, answers, and evaluations.

### Q6: What are the exact weights used in the scoring formula?
**Answer:**
- **Relevance:** 25%
- **Keyword Match:** 25%
- **Similarity:** 25%
- **Completeness:** 15%
- **Grammar/Language Quality:** 10%
Sum = 100%.

---

## 19. Final Verification Checklist
- [x] Python 3.10+ compatible
- [x] Dependencies properly configured in `requirements.txt`
- [x] SQLite database with 5 normalized tables and foreign keys
- [x] 42 technical questions seeded across all 6 roles
- [x] Classical NLP pipeline implemented using NLTK and scikit-learn
- [x] Scoring formula strictly follows 25/25/25/15/10 weights
- [x] Dynamic, score-dependent constructive feedback
- [x] Result dashboard with Chart.js Multi-Dimensional Radar and Bar charts
- [x] Interview history with full previous report view
- [x] Automated `/demo` endpoint evaluating Alex Kumar's answers live
- [x] 17 automated tests passing with 100% success
- [x] Production ready with Gunicorn and Procfile
