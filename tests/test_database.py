import pytest
import uuid
from pathlib import Path
from src.database.db import initialize
from src.database.repository import create_student,start_session,record_response,submit_session,response_frame
from src.data.question_bank import QUESTIONS

def test_init_and_record_duplicate_submission():
    db=Path('tests')/f"test_{uuid.uuid4().hex}.db"
    try:
        initialize(db); initialize(db)
        sid=create_student('A',db); q=QUESTIONS[0]; session=start_session(sid,'test',1,db)
        assert record_response(session,sid,q['question_id'],q['correct_answer'],q['correct_answer'],12,db)
        assert not record_response(session,sid,q['question_id'],'B',q['correct_answer'],12,db)
        submit_session(session,sid,db)
        with pytest.raises(ValueError): record_response(session,sid,q['question_id'],'A',q['correct_answer'],12,db)
        assert len(response_frame(sid,db))==1
    finally: db.unlink(missing_ok=True)

def test_profile_isolation():
    db=Path('tests')/f"test_{uuid.uuid4().hex}.db"
    try:
        initialize(db); a=create_student('A',db); b=create_student('B',db); q=QUESTIONS[0]
        session=start_session(a,'test',1,db); record_response(session,a,q['question_id'],q['correct_answer'],q['correct_answer'],2,db)
        assert response_frame(a,db).shape[0]==1 and response_frame(b,db).empty
    finally: db.unlink(missing_ok=True)
