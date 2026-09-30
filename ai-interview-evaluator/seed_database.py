import os
from database import get_db_connection, init_db

QUESTIONS_DATA = [
    # ==================== PYTHON DEVELOPER ====================
    {
        "role": "Python Developer",
        "question": "What is Python?",
        "reference_answer": "Python is a high-level, interpreted, dynamically typed programming language known for its simple and readable syntax. It supports multiple programming paradigms including object-oriented, procedural, and functional programming, and is widely used for software development, data science, web development, and automation.",
        "keywords": "high-level, interpreted, dynamically typed, simple syntax, object-oriented, programming paradigms, software development",
        "difficulty": "Easy"
    },
    {
        "role": "Python Developer",
        "question": "What is inheritance in Python?",
        "reference_answer": "Inheritance is a fundamental concept of object-oriented programming that allows a child or derived class to inherit attributes and methods from a parent or base class. It promotes code reusability, supports method overriding, and enables hierarchical class relationships.",
        "keywords": "inheritance, child class, parent class, attributes, methods, object-oriented, code reusability, method overriding",
        "difficulty": "Easy"
    },
    {
        "role": "Python Developer",
        "question": "What are Python decorators and how do they work?",
        "reference_answer": "Decorators in Python are higher-order functions that take another function as an argument, extend or modify its behavior without altering its source code, and return a callable object. They are commonly applied using the @decorator syntax for logging, authentication, and caching.",
        "keywords": "decorators, higher-order functions, modify behavior, wrapper function, callable, @ syntax, closure",
        "difficulty": "Medium"
    },
    {
        "role": "Python Developer",
        "question": "Explain the difference between lists and tuples in Python.",
        "reference_answer": "Lists are mutable ordered sequences enclosed in square brackets, meaning elements can be added, removed, or changed in place. Tuples are immutable ordered sequences enclosed in parentheses, meaning they cannot be modified after creation, making tuples faster, hashable, and memory efficient.",
        "keywords": "lists, tuples, mutable, immutable, square brackets, parentheses, hashable, memory efficient",
        "difficulty": "Easy"
    },
    {
        "role": "Python Developer",
        "question": "What is the Global Interpreter Lock (GIL) in CPython?",
        "reference_answer": "The Global Interpreter Lock (GIL) is a mutex used by the CPython implementation to prevent multiple native threads from executing Python bytecodes simultaneously. It simplifies memory management and ensures thread safety for reference counting, but limits CPU-bound multithreaded performance.",
        "keywords": "global interpreter lock, GIL, mutex, CPython, native threads, bytecode, thread safety, reference counting, CPU-bound",
        "difficulty": "Hard"
    },
    {
        "role": "Python Developer",
        "question": "Explain the difference between shallow copy and deep copy in Python.",
        "reference_answer": "A shallow copy creates a new compound object and inserts references to the original nested objects, so modifying nested objects affects both copies. A deep copy recursively duplicates the compound object and all nested objects, creating completely independent copies.",
        "keywords": "shallow copy, deep copy, references, nested objects, recursive duplication, copy module, independent",
        "difficulty": "Medium"
    },
    {
        "role": "Python Developer",
        "question": "How does memory management and garbage collection work in Python?",
        "reference_answer": "Python manages memory automatically using a private heap space managed by the Python memory manager. It primarily uses reference counting to deallocate objects when reference count drops to zero, supplemented by a cyclic garbage collector that detects and cleans up circular reference cycles across three generations.",
        "keywords": "memory management, private heap, reference counting, garbage collection, circular references, generations, cyclic gc",
        "difficulty": "Hard"
    },

    # ==================== SOFTWARE DEVELOPER ====================
    {
        "role": "Software Developer",
        "question": "Explain the SOLID design principles in software engineering.",
        "reference_answer": "SOLID principles are five design guidelines for maintainable object-oriented software: Single Responsibility Principle (a class has one reason to change), Open/Closed Principle (open for extension, closed for modification), Liskov Substitution Principle (subtypes must be substitutable for base types), Interface Segregation Principle (small specific interfaces rather than large bloated ones), and Dependency Inversion Principle (depend on abstractions, not concretions).",
        "keywords": "SOLID, single responsibility, open closed, liskov substitution, interface segregation, dependency inversion, abstractions, maintainability",
        "difficulty": "Medium"
    },
    {
        "role": "Software Developer",
        "question": "What is the difference between synchronous and asynchronous programming?",
        "reference_answer": "Synchronous programming executes tasks sequentially, where each operation blocks execution until completion before moving to the next. Asynchronous programming is non-blocking, allowing long-running operations like I/O or network requests to run concurrently via event loops, promises, or callbacks without stalling the main execution thread.",
        "keywords": "synchronous, asynchronous, blocking, non-blocking, sequential, concurrency, event loop, I/O operations",
        "difficulty": "Easy"
    },
    {
        "role": "Software Developer",
        "question": "Explain how a RESTful API works and its core architectural constraints.",
        "reference_answer": "A RESTful API conforms to Representational State Transfer constraints including stateless communication, client-server architecture, cacheability, uniform interface, and layered systems. It typically uses HTTP methods like GET, POST, PUT, DELETE to operate on resource URIs and exchange standard representations like JSON.",
        "keywords": "RESTful API, stateless, client-server, HTTP methods, GET, POST, PUT, DELETE, URIs, JSON, uniform interface",
        "difficulty": "Medium"
    },
    {
        "role": "Software Developer",
        "question": "What is Git and how does branch merging differ between merge and rebase?",
        "reference_answer": "Git is a distributed version control system. A git merge combines changes from two branches by creating a new merge commit, preserving historical chronology and context. A git rebase reapplies commits from the feature branch on top of the base branch, producing a linear, clean commit history without merge commits.",
        "keywords": "git, distributed version control, merge, rebase, merge commit, linear history, commit history, branch",
        "difficulty": "Medium"
    },
    {
        "role": "Software Developer",
        "question": "Explain Big-O notation and why time and space complexity matter.",
        "reference_answer": "Big-O notation describes the limiting behavior and scalability of an algorithm by measuring worst-case upper bound of time execution or memory usage relative to input size N. It helps developers choose efficient algorithms and predict performance bottlenecks under heavy data scale.",
        "keywords": "Big-O notation, time complexity, space complexity, upper bound, scalability, algorithm, input size, performance",
        "difficulty": "Easy"
    },
    {
        "role": "Software Developer",
        "question": "What is continuous integration and continuous deployment (CI/CD)?",
        "reference_answer": "CI/CD is a DevOps automated software delivery methodology. Continuous Integration automatically builds and tests code commits pushed to a repository to catch integration issues early. Continuous Deployment automatically packages, tests, and deploys validated releases directly to staging or production environments.",
        "keywords": "CI/CD, continuous integration, continuous deployment, automated testing, pipeline, build, deployment, DevOps",
        "difficulty": "Medium"
    },
    {
        "role": "Software Developer",
        "question": "How do microservices architecture differ from monolithic architecture?",
        "reference_answer": "A monolithic architecture bundles UI, business logic, and database access into a single unified codebase and deployment unit. Microservices decompose an application into autonomous, loosely coupled services communicating via APIs, allowing independent scaling, deployment, and technology diversity at the cost of network complexity.",
        "keywords": "microservices, monolithic architecture, loosely coupled, autonomous, scalability, independent deployment, APIs",
        "difficulty": "Hard"
    },

    # ==================== JAVA DEVELOPER ====================
    {
        "role": "Java Developer",
        "question": "What is the difference between JDK, JRE, and JVM in Java?",
        "reference_answer": "JVM (Java Virtual Machine) is an abstract computing machine that executes compiled Java bytecode. JRE (Java Runtime Environment) bundles the JVM along with standard Java class libraries to run Java applications. JDK (Java Development Kit) is the full development software containing JRE, compilers (javac), debuggers, and tools needed to write and compile Java code.",
        "keywords": "JDK, JRE, JVM, bytecode, execution, javac, class libraries, compiler, runtime environment",
        "difficulty": "Easy"
    },
    {
        "role": "Java Developer",
        "question": "Explain the difference between method overloading and method overriding in Java.",
        "reference_answer": "Method overloading occurs within the same class when multiple methods share the same name but differ in parameters (number, type, or order), resolved at compile-time (static polymorphism). Method overriding occurs when a subclass provides a specific implementation of a method already declared in its superclass with the exact same signature, resolved at runtime (dynamic polymorphism).",
        "keywords": "method overloading, method overriding, polymorphism, compile-time, runtime, subclass, method signature, parameters",
        "difficulty": "Easy"
    },
    {
        "role": "Java Developer",
        "question": "How does Java handle memory management and Garbage Collection?",
        "reference_answer": "Java delegates memory management to the JVM, allocating primitive variables and method call stacks in Stack memory and objects in Heap memory. The Garbage Collector automatically reclaims memory by identifying unreferenced objects using mark-and-sweep, copying, or generational algorithms (Young and Old generations, G1GC, ZGC).",
        "keywords": "memory management, JVM, heap memory, stack memory, garbage collection, mark and sweep, generational, unreferenced objects",
        "difficulty": "Medium"
    },
    {
        "role": "Java Developer",
        "question": "Explain the differences between HashMap, HashTable, and ConcurrentHashMap in Java.",
        "reference_answer": "HashMap is unsynchronized, fast, and permits one null key and multiple null values, making it unsuitable for multi-threaded writes. HashTable is legacy and synchronized at the method level, causing lock contention. ConcurrentHashMap achieves high concurrent performance by using bucket-level locking and lock-free CAS operations without locking the entire map.",
        "keywords": "HashMap, HashTable, ConcurrentHashMap, synchronized, thread-safe, lock contention, CAS, bucket-level locking",
        "difficulty": "Hard"
    },
    {
        "role": "Java Developer",
        "question": "What are Java Streams and lambda expressions introduced in Java 8?",
        "reference_answer": "Lambda expressions provide clear, concise syntax to represent anonymous functions and implement functional interfaces. The Streams API enables functional-style declarative processing of sequences of elements with operations like filter, map, reduce, and collect, supporting lazy evaluation and parallel execution.",
        "keywords": "streams, lambda expressions, functional interface, declarative, filter, map, reduce, lazy evaluation, parallel execution",
        "difficulty": "Medium"
    },
    {
        "role": "Java Developer",
        "question": "What is the Spring Boot framework and what is Inversion of Control (IoC)?",
        "reference_answer": "Spring Boot is an opinionated framework built on top of Spring that simplifies enterprise Java application development through auto-configuration and embedded servers. Inversion of Control (IoC) transfers the responsibility of object instantiation and lifecycle management to the Spring IoC container, typically implemented via Dependency Injection.",
        "keywords": "Spring Boot, Inversion of Control, IoC, dependency injection, container, auto-configuration, lifecycle management",
        "difficulty": "Medium"
    },
    {
        "role": "Java Developer",
        "question": "Explain the difference between checked and unchecked exceptions in Java.",
        "reference_answer": "Checked exceptions inherit from Exception (excluding RuntimeException) and are checked at compile-time, requiring mandatory handling via try-catch or throws clause. Unchecked exceptions inherit from RuntimeException or Error and occur at runtime (like NullPointerException), reflecting programming logic bugs without mandatory compile-time checks.",
        "keywords": "checked exceptions, unchecked exceptions, RuntimeException, compile-time, try-catch, throws, NullPointerException",
        "difficulty": "Easy"
    },

    # ==================== WEB DEVELOPER ====================
    {
        "role": "Web Developer",
        "question": "Explain how the Document Object Model (DOM) works and what the Virtual DOM is.",
        "reference_answer": "The DOM is a tree-structured programmatic representation of an HTML document created by the browser, allowing JavaScript to dynamically inspect and manipulate page structure, styles, and content. The Virtual DOM is an in-memory lightweight abstraction of the real DOM used by frameworks like React to compute efficient diffs and batch updates, minimizing costly direct DOM repaints.",
        "keywords": "DOM, Document Object Model, Virtual DOM, tree representation, JavaScript, React, diffing, repaints, in-memory",
        "difficulty": "Medium"
    },
    {
        "role": "Web Developer",
        "question": "Explain the CSS Box Model and how box-sizing affects it.",
        "reference_answer": "The CSS Box Model describes the rectangular boxes generated for elements, consisting from inside out of content, padding, border, and margin. By default (content-box), width and height only apply to content. Setting box-sizing: border-box includes padding and border within the specified element width and height, simplifying responsive layouts.",
        "keywords": "CSS Box Model, content, padding, border, margin, box-sizing, border-box, layout",
        "difficulty": "Easy"
    },
    {
        "role": "Web Developer",
        "question": "Explain the JavaScript Event Loop, Call Stack, and Task Queue.",
        "reference_answer": "JavaScript is single-threaded and executes synchronous code on a Call Stack. Asynchronous tasks (like fetch, setTimeout) are delegated to browser Web APIs, which push callbacks into the Task Queue or Microtask Queue. When the Call Stack becomes empty, the Event Loop pulls pending callbacks onto the stack for execution.",
        "keywords": "event loop, call stack, task queue, microtask queue, asynchronous, single-threaded, callbacks, Web APIs",
        "difficulty": "Hard"
    },
    {
        "role": "Web Developer",
        "question": "What is Cross-Origin Resource Sharing (CORS) and how is it resolved?",
        "reference_answer": "CORS is a browser security mechanism that restricts web applications running at one origin from requesting resources from a different origin. It relies on HTTP response headers like Access-Control-Allow-Origin, Access-Control-Allow-Methods, and preflight OPTIONS requests sent by the browser to determine permitted cross-origin access.",
        "keywords": "CORS, cross-origin resource sharing, same-origin policy, HTTP headers, Access-Control-Allow-Origin, preflight, OPTIONS",
        "difficulty": "Medium"
    },
    {
        "role": "Web Developer",
        "question": "What is the difference between sessionStorage, localStorage, and Cookies?",
        "reference_answer": "localStorage stores key-value strings persistently across browser sessions without expiration. sessionStorage stores data isolated to the current browser tab and is cleared when the tab closes. Cookies store small text payloads (up to 4KB) with explicit expiration dates that are automatically sent to the server in HTTP request headers, often used for authentication sessions.",
        "keywords": "localStorage, sessionStorage, cookies, client-side storage, persistence, expiration, HTTP headers, authentication",
        "difficulty": "Easy"
    },
    {
        "role": "Web Developer",
        "question": "How can web application performance and Core Web Vitals be optimized?",
        "reference_answer": "Web performance is optimized by code splitting, lazy loading images and assets, minifying CSS and JavaScript, leveraging browser caching and CDNs, optimizing database queries, and improving Core Web Vitals such as Largest Contentful Paint (LCP), First Input Delay/INP, and Cumulative Layout Shift (CLS).",
        "keywords": "performance optimization, Core Web Vitals, code splitting, lazy loading, caching, CDN, minification, LCP, CLS",
        "difficulty": "Medium"
    },
    {
        "role": "Web Developer",
        "question": "What are Progressive Web Apps (PWAs) and their key technical components?",
        "reference_answer": "Progressive Web Apps (PWAs) are web applications built with modern web technologies that offer app-like experiences. Their key technical components include a Web App Manifest for installation metadata, Service Workers to handle background caching, offline capability, and push notifications, and mandatory HTTPS security.",
        "keywords": "PWA, progressive web apps, service workers, web app manifest, offline capability, caching, push notifications, HTTPS",
        "difficulty": "Hard"
    },

    # ==================== DATA ANALYST ====================
    {
        "role": "Data Analyst",
        "question": "What is the difference between INNER JOIN, LEFT JOIN, RIGHT JOIN, and FULL OUTER JOIN in SQL?",
        "reference_answer": "An INNER JOIN returns only records with matching keys in both tables. A LEFT JOIN returns all rows from the left table and matched rows from the right table, filling nulls where no match exists. A RIGHT JOIN returns all rows from the right table with matched rows from the left. A FULL OUTER JOIN returns all rows from both tables, combining matches and supplying nulls for unmatched keys.",
        "keywords": "INNER JOIN, LEFT JOIN, RIGHT JOIN, FULL OUTER JOIN, SQL, matching keys, null values, relational database",
        "difficulty": "Easy"
    },
    {
        "role": "Data Analyst",
        "question": "How do you detect and handle missing data and outliers in a dataset?",
        "reference_answer": "Missing data is detected using functions like isna() or null checks and handled via deletion (listwise), mean/median/mode imputation, forward/backward fill, or model-based imputation. Outliers are identified using Z-scores, IQR (interquartile range) thresholds, or boxplots, and managed by trimming, capping (winsorization), or data transformation.",
        "keywords": "missing data, outliers, imputation, mean, median, IQR, interquartile range, Z-score, winsorization, boxplots",
        "difficulty": "Medium"
    },
    {
        "role": "Data Analyst",
        "question": "Explain the difference between descriptive, diagnostic, predictive, and prescriptive analytics.",
        "reference_answer": "Descriptive analytics summarizes past data to answer what happened (e.g., reports, dashboards). Diagnostic analytics investigates historical patterns to answer why it happened (e.g., root cause analysis, drill-downs). Predictive analytics uses historical data and statistical models to forecast what will happen. Prescriptive analytics uses optimization and decision models to suggest what action should be taken.",
        "keywords": "descriptive, diagnostic, predictive, prescriptive, analytics, forecasting, root cause, optimization, dashboards",
        "difficulty": "Medium"
    },
    {
        "role": "Data Analyst",
        "question": "What are SQL window functions and how do they differ from GROUP BY?",
        "reference_answer": "SQL window functions (such as ROW_NUMBER, RANK, DENSE_RANK, and SUM() OVER()) perform calculations across a set of table rows related to the current row without collapsing them into a single summary row. Unlike GROUP BY, window functions retain the individual identity and cardinality of every row in the output.",
        "keywords": "window functions, GROUP BY, OVER clause, PARTITION BY, ROW_NUMBER, RANK, aggregation, cardinality",
        "difficulty": "Medium"
    },
    {
        "role": "Data Analyst",
        "question": "Explain the concept of correlation versus causation and how to avoid analytical bias.",
        "reference_answer": "Correlation measures statistical association between two variables, while causation proves that changes in one variable directly cause changes in another. Assuming causation from correlation is a fallacy often caused by confounding variables or reverse causality. Controlled experiments, A/B testing, and regression controls help identify true causal relationships.",
        "keywords": "correlation, causation, confounding variables, A/B testing, statistical association, bias, regression",
        "difficulty": "Easy"
    },
    {
        "role": "Data Analyst",
        "question": "What is exploratory data analysis (EDA) and what are its key stages?",
        "reference_answer": "Exploratory Data Analysis (EDA) is the preliminary investigation of datasets to discover patterns, anomalies, test hypotheses, and verify assumptions using summary statistics and graphical visualizations. Key stages include data structure inspection, summary statistics calculation, univariate analysis, bivariate correlation analysis, missing value handling, and distribution plotting.",
        "keywords": "exploratory data analysis, EDA, summary statistics, univariate, bivariate, visualization, distributions, anomalies",
        "difficulty": "Easy"
    },
    {
        "role": "Data Analyst",
        "question": "What are common business metrics like CAC, LTV, Churn Rate, and ROI?",
        "reference_answer": "Customer Acquisition Cost (CAC) is total sales and marketing spend divided by number of customers acquired. Customer Lifetime Value (LTV) is total expected gross margin revenue generated by a customer over their relationship. Churn Rate is the percentage of customers who cancel service within a given period. Return on Investment (ROI) is net profit divided by total cost of investment.",
        "keywords": "CAC, LTV, churn rate, ROI, business metrics, customer acquisition cost, lifetime value, profitability",
        "difficulty": "Hard"
    },

    # ==================== MACHINE LEARNING ENGINEER ====================
    {
        "role": "Machine Learning Engineer",
        "question": "Explain the bias-variance tradeoff and how it relates to overfitting and underfitting.",
        "reference_answer": "The bias-variance tradeoff balances two sources of error: bias (erroneous assumptions causing underfitting and poor training performance) and variance (excessive sensitivity to small fluctuations in training data causing overfitting and poor test generalization). The goal is to minimize total expected generalization error by finding optimal model complexity.",
        "keywords": "bias-variance tradeoff, bias, variance, overfitting, underfitting, generalization error, model complexity, regularization",
        "difficulty": "Medium"
    },
    {
        "role": "Machine Learning Engineer",
        "question": "What is the difference between supervised, unsupervised, and reinforcement learning?",
        "reference_answer": "Supervised learning trains models on labeled datasets to learn mappings between inputs and target outputs (classification, regression). Unsupervised learning discovers hidden patterns, groupings, or representations from unlabeled data (clustering, dimensionality reduction). Reinforcement learning trains agents to make sequential decisions by taking actions in an environment to maximize cumulative reward.",
        "keywords": "supervised learning, unsupervised learning, reinforcement learning, labeled data, clustering, classification, agent, reward",
        "difficulty": "Easy"
    },
    {
        "role": "Machine Learning Engineer",
        "question": "How do Gradient Descent and its variants like Adam and SGD optimize loss functions?",
        "reference_answer": "Gradient Descent is an optimization algorithm that iteratively updates model parameters in the direction opposite to the gradient of the loss function. Stochastic Gradient Descent (SGD) computes gradients on single samples or mini-batches for faster updates. Adam (Adaptive Moment Estimation) combines momentum and RMSprop to adapt individual learning rates using first and second moments of gradients.",
        "keywords": "gradient descent, SGD, Adam, loss function, learning rate, momentum, backpropagation, optimization, mini-batch",
        "difficulty": "Hard"
    },
    {
        "role": "Machine Learning Engineer",
        "question": "Explain evaluation metrics for classification: Precision, Recall, F1-Score, and ROC-AUC.",
        "reference_answer": "Precision measures the proportion of true positive predictions among all positive predictions (TP / (TP + FP)). Recall (sensitivity) measures true positive detections among actual positives (TP / (TP + FN)). The F1-score is the harmonic mean of precision and recall. ROC-AUC measures the area under the True Positive Rate versus False Positive Rate curve across classification thresholds.",
        "keywords": "precision, recall, F1-score, ROC-AUC, classification metrics, true positive, false positive, harmonic mean, sensitivity",
        "difficulty": "Medium"
    },
    {
        "role": "Machine Learning Engineer",
        "question": "What is regularization in machine learning and how do L1 (Lasso) and L2 (Ridge) differ?",
        "reference_answer": "Regularization prevents overfitting by penalizing large model coefficients in the loss function. L1 regularization (Lasso) adds the absolute magnitude of coefficients, driving non-essential coefficients to exact zero for feature selection. L2 regularization (Ridge) adds the squared magnitude of coefficients, shrinking weights smoothly toward zero without eliminating them.",
        "keywords": "regularization, L1 regularization, L2 regularization, Lasso, Ridge, overfitting, loss penalty, feature selection, shrinkage",
        "difficulty": "Medium"
    },
    {
        "role": "Machine Learning Engineer",
        "question": "What are transformer models and how does the self-attention mechanism work?",
        "reference_answer": "Transformers are neural network architectures designed for sequential data processing without recurrent loops. The self-attention mechanism computes pairwise attention weights between all tokens in a sequence using query, key, and value vector projections, enabling the model to capture global context and long-range dependencies in parallel.",
        "keywords": "transformer, self-attention, attention mechanism, query, key, value, neural network, sequence, parallel processing",
        "difficulty": "Hard"
    },
    {
        "role": "Machine Learning Engineer",
        "question": "What is cross-validation and why is K-fold cross-validation preferred over a single train-test split?",
        "reference_answer": "Cross-validation is a model validation technique assessing how statistical analysis generalizes to an independent dataset. K-fold cross-validation divides data into K equal partitions, training on K-1 folds and validating on the remaining fold K times. This averages out variance and sampling bias from a single arbitrary train-test split.",
        "keywords": "cross-validation, K-fold, train-test split, model evaluation, generalization, variance, validation fold, overfitting",
        "difficulty": "Easy"
    }
]

def seed_questions(db_path=None):
    """
    Populate the SQLite questions table with questions across all 6 job roles.
    """
    init_db(db_path)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    # Clear existing questions to allow clean reseeding if desired
    cursor.execute("DELETE FROM questions")

    for q in QUESTIONS_DATA:
        cursor.execute(
            """INSERT INTO questions (role, question, reference_answer, keywords, difficulty)
               VALUES (?, ?, ?, ?, ?)""",
            (q["role"], q["question"], q["reference_answer"], q["keywords"], q["difficulty"])
        )

    conn.commit()
    cursor.execute("SELECT COUNT(*) AS total FROM questions")
    total = cursor.fetchone()["total"]
    conn.close()
    print(f"Successfully seeded {total} questions across 6 roles.")
    return total

if __name__ == "__main__":
    seed_questions()
