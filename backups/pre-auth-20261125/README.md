# LearnLens AI

**Understand how you learn. Discover what you don't know.**

LearnLens AI is a local-first learning analytics application for Computer Networks. It stores quiz attempts in SQLite, estimates topic mastery, gives explainable revision suggestions, adapts practice using transparent rules, and trains a real scikit-learn model to estimate the chance of answering a question correctly.

## Problem and objectives

Quiz scores alone do not show which concepts need practice, whether mistakes recur, or whether a learner is improving. LearnLens turns question-level quiz history into topic trends and a practical study plan. The dashboard separates supervised-model estimates from rule-based insights.

## Features

- 64 curated MCQs across ten Computer Networks topics, with four choices, explanation, concept, prerequisite, difficulty, and estimated time.
- Multiple local student profiles, first-launch demo profiles, and per-profile history reset.
- Topic, mixed, weak-topic, and adaptive quiz modes; answer review and duplicate-safe persistence.
- SQLite persistence for profiles, questions, sessions, responses, and study tasks.
- Mastery estimates with shrinkage for small samples, recency, trend, and confidence indicators.
- Rule-based recommendations and editable completion tracking for a personalized revision plan.
- Plotly analytics for topic and difficulty results, progress, and response time.
- Logistic Regression and Random Forest training, student-group holdout evaluation, model persistence, probabilities, confusion matrices, and interpretable coefficients/importances.
- Reproducible synthetic attempt generator.

## Architecture

`app.py` contains the Streamlit user interface. `src/database` owns SQLite and profile-scoped repository functions. `src/data` supplies the question bank and synthetic data. `src/features` builds chronological prior-only features. `src/models` trains, evaluates, persists, and loads classifiers. `src/analytics` computes mastery and patterns. `src/recommendations` ranks revision topics and creates study plans.

## Technology

Python 3.11 or compatible, Streamlit, Pandas, NumPy, scikit-learn, Plotly, SQLite, Joblib, and Pytest. No paid API or LLM key is required.

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

The SQLite database and model are created in the project folder. The app initializes SQLite and seeds demo profiles on first launch. The question-bank command exports `datasets/questions.csv` from the reviewed source list. Set `LEARNLENS_DB_PATH` or `LEARNLENS_MODEL_DIR` to use alternate storage locations. If the model is absent, the ML Insights page explains how to train it; quiz and rule-based analytics remain available.

Run automated checks with `pytest`. Train again any time with `python -m src.models.train`.

## Project structure

```text
app.py, config.py, requirements.txt
src/database/     SQLite schema and repository
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

Run the app locally to capture screenshots for the Dashboard, Knowledge Gaps, and ML Insights pages. The interface is responsive and uses interactive Plotly charts.

## Limitations and future work

- Only Computer Networks questions are currently bundled. The question schema and topic metadata are subject-independent.
- Demo histories are illustrative and synthetic; they can be cleared from Profile settings.
- Mastery thresholds and adaptive choice rules are initial transparent heuristics and should be evaluated with educators and real, consented data.
- No authentication is provided; this is intended for local demonstrations.
- Future work could add content-authoring tools, calibrated uncertainty, accessibility review, richer student-group and temporal evaluation, and additional reviewed question sets.
