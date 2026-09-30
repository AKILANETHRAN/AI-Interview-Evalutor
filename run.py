#!/usr/bin/env python
"""
Root runner script for AI Interview Evaluator.
Allows launching the Flask application directly from the repository root.
"""
import os
import sys

# Change working directory to ai-interview-evaluator
project_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ai-interview-evaluator")
sys.path.insert(0, project_dir)
os.chdir(project_dir)

from app import app

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    print(f"Starting AI Interview Evaluator on http://127.0.0.1:{port}")
    app.run(host="0.0.0.0", port=port, debug=True)
