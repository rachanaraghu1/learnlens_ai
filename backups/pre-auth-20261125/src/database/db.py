"""SQLite connection and migration-safe initialization."""
import json
import sqlite3
from pathlib import Path
from config import DB_PATH

class ClosingConnection(sqlite3.Connection):
    """SQLite's native context manager commits but does not close; close at scope exit."""
    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return super().__exit__(exc_type, exc_value, traceback)
        finally:
            self.close()

def connect(path=None):
    db_path = Path(path or DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path), timeout=15, factory=ClosingConnection)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def initialize(path=None):
    from src.data.question_bank import QUESTIONS
    with connect(path) as conn:
        conn.executescript('''
        CREATE TABLE IF NOT EXISTS students(student_id TEXT PRIMARY KEY, student_name TEXT NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, is_demo INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS questions(question_id TEXT PRIMARY KEY, question_text TEXT NOT NULL, options TEXT NOT NULL, correct_answer TEXT NOT NULL, explanation TEXT NOT NULL, topic TEXT NOT NULL, subtopic TEXT NOT NULL, difficulty TEXT NOT NULL, concept TEXT NOT NULL, prerequisite TEXT NOT NULL DEFAULT '', estimated_time INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS quiz_sessions(session_id TEXT PRIMARY KEY, student_id TEXT NOT NULL REFERENCES students(student_id), start_time TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, completion_time TEXT, quiz_type TEXT NOT NULL, total_questions INTEGER NOT NULL DEFAULT 0, submitted INTEGER NOT NULL DEFAULT 0);
        CREATE TABLE IF NOT EXISTS student_responses(response_id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL REFERENCES quiz_sessions(session_id), student_id TEXT NOT NULL REFERENCES students(student_id), question_id TEXT NOT NULL REFERENCES questions(question_id), selected_answer TEXT NOT NULL, is_correct INTEGER NOT NULL, time_taken_seconds REAL NOT NULL DEFAULT 0, attempt_number INTEGER NOT NULL, timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, confidence REAL);
        CREATE TABLE IF NOT EXISTS study_tasks(task_id INTEGER PRIMARY KEY AUTOINCREMENT, student_id TEXT NOT NULL REFERENCES students(student_id), day_number INTEGER NOT NULL, task_text TEXT NOT NULL, topic TEXT NOT NULL, completed INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS topic_mastery(student_id TEXT NOT NULL REFERENCES students(student_id), topic TEXT NOT NULL, mastery_score REAL NOT NULL, accuracy REAL NOT NULL, total_attempts INTEGER NOT NULL, recent_accuracy REAL NOT NULL, last_practiced TEXT, revision_status TEXT NOT NULL, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY(student_id, topic));
        CREATE TABLE IF NOT EXISTS app_metadata(metadata_key TEXT PRIMARY KEY, metadata_value TEXT NOT NULL);
        CREATE INDEX IF NOT EXISTS idx_response_student_time ON student_responses(student_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_session_student ON quiz_sessions(student_id);
        ''')
        for q in QUESTIONS:
            conn.execute('''INSERT INTO questions VALUES(?,?,?,?,?,?,?,?,?,?,?) ON CONFLICT(question_id) DO UPDATE SET question_text=excluded.question_text, options=excluded.options, correct_answer=excluded.correct_answer, explanation=excluded.explanation, topic=excluded.topic, subtopic=excluded.subtopic, difficulty=excluded.difficulty, concept=excluded.concept, prerequisite=excluded.prerequisite, estimated_time=excluded.estimated_time''', (q['question_id'],q['question_text'],json.dumps(q['options']),q['correct_answer'],q['explanation'],q['topic'],q['subtopic'],q['difficulty'],q['concept'],q['prerequisite'],q['estimated_time']))
        conn.commit()
    return True

if __name__ == '__main__':
    initialize()
    print(f'LearnLens database initialized at {DB_PATH}')
