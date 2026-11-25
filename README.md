# LearnLens AI

**Understand how you learn. Discover what you don't know.**

LearnLens AI is a local-first EdTech website for Computer Networks. Students create an account, then use their own isolated dashboard, quizzes, analytics, topic mastery, study plan, and recommendations. It stores quiz attempts in SQLite and trains a scikit-learn model to estimate the chance of answering a question correctly.

## Problem and objectives

Quiz scores alone do not show which concepts need practice, whether mistakes recur, or whether a learner is improving. LearnLens turns question-level quiz history into topic trends and a practical study plan. The dashboard separates supervised-model estimates from rule-based insights.

## Features

- 64 curated MCQs across ten Computer Networks topics, with four choices, explanation, concept, prerequisite, difficulty, and estimated time.
- Public landing page with Home, Features, About, Login, and Sign Up navigation.
- Account registration and login by username or email; registration validates name, email, username, password length, and confirmation.
- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes (600,000 iterations); plaintext passwords are never written to SQLite.
- Each registered account maps to a private student profile. Quiz sessions, responses, analytics, and study tasks are scoped to that profile. New accounts start with empty learning history.
- Logout clears authentication and any in-progress quiz from the active Streamlit session.
- Topic, mixed, weak-topic, and adaptive quiz modes; answer review and duplicate-safe persistence.
- SQLite persistence for profiles, questions, sessions, responses, and study tasks.
- Mastery estimates with shrinkage for small samples, recency, trend, and confidence indicators.
- Rule-based recommendations and editable completion tracking for a personalized revision plan.
- Plotly analytics for topic and difficulty results, progress, and response time.
- Logistic Regression and Random Forest training, student-group holdout evaluation, model persistence, probabilities, confusion matrices, and interpretable coefficients/importances.
- Reproducible synthetic attempt generator.

## Architecture

`app.py` contains the public site and authenticated Streamlit workspace. `src/auth.py` validates registration, hashes passwords, authenticates accounts, and clears session state at logout. The `users` table links each account one-to-one to a `students` row. `src/database` owns migration-safe SQLite initialization and profile-scoped repository functions. `src/data` supplies the question bank and synthetic data. `src/features` builds chronological prior-only features. `src/models` trains, evaluates, persists, and loads classifiers. `src/analytics` computes mastery and patterns. `src/recommendations` ranks revision topics and creates study plans.

## Technology

Python 3.11 or compatible, Streamlit, Pandas, NumPy, scikit-learn, Plotly, SQLite, Joblib, and Pytest. Password hashing uses Python's standard library, so no additional auth or paid API dependency is required. No LLM key is required.

## Machine learning workflow

The target is whether an answer is correct. At prediction time, features include previous topic accuracy, number of previous attempts/correct/incorrect answers, recent accuracy, prior average response time, difficulty, performance at that difficulty, days since practice, recent trend, recent mistakes, and attempt number. The current answer is never used to create its own input features.

Logistic Regression is a relatively simple linear baseline whose coefficients show direction and strength. Random Forest averages decision trees and can model nonlinear patterns; its feature importance offers a global view of which inputs the fitted trees used. Both models are compared using a held-out group of synthetic students. Accuracy, precision, recall, F1, ROC-AUC, and confusion matrices are reported. The model with higher ROC-AUC (then F1) is saved. Metrics describe only this synthetic simulation, not real learner performance.

Mastery and recommendations are separate, rule-based calculations. Mastery combines smoothed overall accuracy, recent accuracy, a modest difficulty signal, trend, and practice recency. The score is descriptive rather than a definitive judgment; low sample counts visibly reduce confidence. Recommendations prioritize low mastery, stale practice, and uncertain samples, with a plain-language reason. Adaptive practice chooses among unseen items, favors recommended topics, and adjusts the desired difficulty after recent answers. These rules do not use the trained model.

## Synthetic data and limitations

`python -m src.data.data_generator` creates a seeded dataset. Simulated learners have different skill and topic strengths, varied response times, practice gains, forgetting, question difficulty, and random variation. The answer is not directly copied into the feature columns. Synthetic behavior is necessarily simplified and may create misleading metrics or patterns. Do not claim validation on real students or use predictions to label learner ability. Any future real data collection requires informed consent, data minimization, secure handling, and bias/validity evaluation.

## Setup (Windows PowerShell)

```powershell
python --version
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m src.database.db
python -m src.data.question_bank
python -m src.data.data_generator
python -m src.models.train
streamlit run app.py
```

The SQLite database and model are created in the project folder. The app initializes the database on first launch. The question-bank command exports `datasets/questions.csv` from the reviewed source list. Set `LEARNLENS_DB_PATH` or `LEARNLENS_MODEL_DIR` to use alternate storage locations. If the model is absent, the ML Insights page explains how to train it; quiz and rule-based analytics remain available.

On first launch, use **Sign Up** to create an account. The app signs you in and opens your personal dashboard. Later, log in with either your username or email address. Use **Log out** in the workspace sidebar to end the session. New accounts have no imported/demo attempts. Existing pre-authentication demo profiles remain in the database for backup/compatibility, but they are not selectable or exposed to signed-in users. Registration and login are local account features intended for a local portfolio deployment.

Run automated checks with `pytest`. Train again any time with `python -m src.models.train`.

## Deploy

For a hosted app that keeps student histories, use the included [Render deployment guide](DEPLOYMENT.md) and `render.yaml`. This configuration mounts a persistent disk for SQLite. Render currently lists the Starter web service at $7/month and the 1 GB disk at $0.25/month; confirm current pricing before provisioning. Streamlit Community Cloud can host a portfolio preview, but local database persistence is not guaranteed there.

## Project structure

```text
app.py, config.py, requirements.txt
src/auth.py       registration, password hashing, login, logout
src/database/     SQLite schema and profile-scoped repository
src/data/         question bank, demos, synthetic generator
src/features/     prior-only feature engineering
src/models/       training and prediction
src/analytics/    mastery, trends, gaps, adaptive selection
src/recommendations/  topic ranking and study plan
datasets/         generated training data documentation
models/           generated model and evaluation metrics
tests/             unit tests
```

## Screenshots

Run the app locally to capture screenshots for the landing page, student Dashboard, Knowledge Gaps, and ML Insights pages. The interface uses a responsive light layout, navy and teal palette, and interactive Plotly charts.

## Limitations and future work

- Only Computer Networks questions are currently bundled. The question schema and topic metadata are subject-independent.
- Authentication is designed for a single local application instance. There is no email verification, password recovery, or administrative role.
- Legacy pre-authentication demo records are retained in the database for compatibility, but authenticated students cannot select or view them.
- Use HTTPS, rate limiting, and a production-grade session and account-security review before exposing this local app to the public internet.
- Mastery thresholds and adaptive choice rules are initial transparent heuristics and should be evaluated with educators and real, consented data.
- Future work could add content-authoring tools, calibrated uncertainty, accessibility review, richer student-group and temporal evaluation, and additional reviewed question sets.

## Database backup

Before adding authentication, the existing application, source modules, tests, saved model, datasets, and SQLite database were copied to `backups/pre-auth-20261125/`. The active database is kept at `learnlens.db` by default; back it up before manually editing or replacing it.
