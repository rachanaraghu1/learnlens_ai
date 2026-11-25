"""Local account registration and authentication with salted PBKDF2 hashes."""
from __future__ import annotations

import hashlib
import hmac
import re
import secrets
import sqlite3
import uuid

from src.database.db import connect

PASSWORD_ITERATIONS = 600_000
PASSWORD_MIN_LENGTH = 10
DUMMY_PASSWORD_HASH = 'pbkdf2_sha256$600000$00000000000000000000000000000000$' + ('0' * 64)
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def hash_password(password: str, *, salt: bytes | None = None) -> str:
    """Return a versioned PBKDF2-SHA256 record with a unique random salt."""
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, PASSWORD_ITERATIONS)
    return f"pbkdf2_sha256${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iteration_text, salt_hex, digest_hex = stored_hash.split('$', 3)
        if algorithm != 'pbkdf2_sha256':
            return False
        computed = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), bytes.fromhex(salt_hex), int(iteration_text))
        return hmac.compare_digest(computed.hex(), digest_hex)
    except (ValueError, TypeError, AttributeError):
        return False


def validate_registration(name: str, email: str, username: str, password: str, confirmation: str) -> tuple[str, str, str]:
    name, email, username = name.strip(), email.strip().lower(), username.strip().lower()
    if len(name) < 2 or len(name) > 80:
        raise ValueError('Enter a name between 2 and 80 characters.')
    if not EMAIL_RE.fullmatch(email):
        raise ValueError('Enter a valid email address.')
    if not USERNAME_RE.fullmatch(username):
        raise ValueError('Username must be 3–32 characters using letters, numbers, dot, underscore, or hyphen.')
    if len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(f'Use a password with at least {PASSWORD_MIN_LENGTH} characters.')
    if len(password) > 256:
        raise ValueError('Password must be 256 characters or fewer.')
    if password != confirmation:
        raise ValueError('Passwords do not match.')
    return name, email, username


def register_account(name: str, email: str, username: str, password: str, confirmation: str, path=None) -> dict:
    name, email, username = validate_registration(name, email, username, password, confirmation)
    user_id = 'usr_' + uuid.uuid4().hex[:16]
    student_id = 'stu_' + uuid.uuid4().hex[:16]
    password_hash = hash_password(password)
    try:
        with connect(path) as conn:
            conn.execute('INSERT INTO students(student_id, student_name, is_demo) VALUES(?,?,0)', (student_id, name))
            conn.execute('INSERT INTO users(user_id, username, email, password_hash, student_id) VALUES(?,?,?,?,?)', (user_id, username, email, password_hash, student_id))
    except sqlite3.IntegrityError as exc:
        raise ValueError('That username or email is already registered.') from exc
    return {'user_id': user_id, 'student_id': student_id, 'student_name': name, 'username': username, 'email': email}


def _account_row(row):
    if row is None:
        return None
    return {'user_id': row['user_id'], 'username': row['username'], 'email': row['email'], 'student_id': row['student_id'], 'student_name': row['student_name']}


def authenticate(identifier: str, password: str, path=None) -> dict | None:
    identifier = identifier.strip().lower()
    with connect(path) as conn:
        row = conn.execute('''SELECT u.user_id,u.username,u.email,u.password_hash,u.student_id,s.student_name
                              FROM users u JOIN students s ON s.student_id=u.student_id
                              WHERE u.username=? OR u.email=?''', (identifier, identifier)).fetchone()
    if row is None:
        # Keep unknown-account and wrong-password work roughly comparable.
        verify_password(password, DUMMY_PASSWORD_HASH)
        return None
    if not verify_password(password, row['password_hash']):
        return None
    return _account_row(row)


def account_for_user(user_id: str, path=None) -> dict | None:
    with connect(path) as conn:
        row = conn.execute('''SELECT u.user_id,u.username,u.email,u.student_id,s.student_name
                              FROM users u JOIN students s ON s.student_id=u.student_id WHERE u.user_id=?''', (user_id,)).fetchone()
    return _account_row(row)


def logout(session_state) -> None:
    """Clear the login and any in-progress quiz data from Streamlit session state."""
    for key in ('user_id', 'quiz_id', 'quiz_student', 'quiz_mode', 'quiz_qids', 'quiz_index', 'quiz_started', 'quiz_feedback', 'quiz_done'):
        session_state.pop(key, None)
    session_state['public_nav'] = 'Home'
