import uuid
from pathlib import Path

import pytest

from src.auth import authenticate, hash_password, logout, register_account, verify_password
from src.database.db import initialize
from src.database.repository import question_rows, record_response, response_frame, start_session


def test_password_hash_is_salted_and_verifiable():
    first = hash_password('a strong test password')
    second = hash_password('a strong test password')
    assert first != second
    assert verify_password('a strong test password', first)
    assert not verify_password('wrong password', first)


def test_logout_clears_account_and_active_quiz():
    state = {'user_id': 'usr_1', 'quiz_id': 'quiz_1', 'quiz_student': 'stu_1', 'quiz_feedback': {'q': True}}
    logout(state)
    assert state == {'public_nav': 'Home'}


def test_registration_login_and_validation():
    db = Path('tests') / f"auth_{uuid.uuid4().hex}.db"
    try:
        initialize(db)
        account = register_account('A Learner', 'learner@example.com', 'learner.one', 'a strong test password', 'a strong test password', db)
        assert response_frame(account['student_id'], db).empty
        assert authenticate('LEARNER.ONE', 'a strong test password', db)['user_id'] == account['user_id']
        assert authenticate('learner@example.com', 'not the password', db) is None
        assert authenticate('unknown', 'a strong test password', db) is None
        with pytest.raises(ValueError, match='already registered'):
            register_account('Another Learner', 'other@example.com', 'learner.one', 'a strong test password', 'a strong test password', db)
        with pytest.raises(ValueError, match='do not match'):
            register_account('Another Learner', 'other@example.com', 'learner.two', 'a strong test password', 'different password', db)
    finally:
        db.unlink(missing_ok=True)


def test_account_learning_data_is_isolated():
    db = Path('tests') / f"auth_{uuid.uuid4().hex}.db"
    try:
        initialize(db)
        first = register_account('First Learner', 'first@example.com', 'first.learner', 'a strong test password', 'a strong test password', db)
        second = register_account('Second Learner', 'second@example.com', 'second.learner', 'a strong test password', 'a strong test password', db)
        q = question_rows(db)[0]
        session = start_session(first['student_id'], 'Topic-based', 1, db)
        record_response(session, first['student_id'], q['question_id'], q['correct_answer'], q['correct_answer'], 12, db)
        assert len(response_frame(first['student_id'], db)) == 1
        assert response_frame(second['student_id'], db).empty
    finally:
        db.unlink(missing_ok=True)
