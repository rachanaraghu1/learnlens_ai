"""Application paths and display settings. Override paths with environment variables."""
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "datasets"
MODEL_DIR = Path(os.getenv("LEARNLENS_MODEL_DIR", ROOT / "models"))
DB_PATH = Path(os.getenv("LEARNLENS_DB_PATH", ROOT / "learnlens.db"))
QUESTIONS_PATH = DATA_DIR / "questions.csv"
TRAINING_PATH = DATA_DIR / "synthetic_training_data.csv"
MODEL_PATH = MODEL_DIR / "success_model.joblib"
METRICS_PATH = MODEL_DIR / "metrics.json"
SUBJECT = "Computer Networks"

