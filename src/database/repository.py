"""Small, explicit repository methods; all student queries are scoped by student_id."""
import json, uuid
import pandas as pd
from src.database.db import connect

def create_student(name, path=None, is_demo=False):
    student_id = 'stu_' + uuid.uuid4().hex[:12]
    with connect(path) as c: c.execute('INSERT INTO students(student_id,student_name,is_demo) VALUES(?,?,?)',(student_id,name.strip(),int(is_demo)))
    return student_id

def students(path=None):
    with connect(path) as c: return [dict(r) for r in c.execute('SELECT * FROM students ORDER BY is_demo DESC, student_name')]

def question_rows(path=None):
    with connect(path) as c: rows=[dict(r) for r in c.execute('SELECT * FROM questions ORDER BY question_id')]
    for r in rows: r['options']=json.loads(r['options'])
    return rows

def start_session(student_id, quiz_type, total, path=None):
    sid='quiz_'+uuid.uuid4().hex[:12]
    with connect(path) as c: c.execute('INSERT INTO quiz_sessions(session_id,student_id,quiz_type,total_questions) VALUES(?,?,?,?)',(sid,student_id,quiz_type,total))
    return sid

def record_response(session_id, student_id, question_id, selected, correct_answer, seconds, path=None, confidence=None):
    if selected not in ('A','B','C','D'): raise ValueError('Answer must be A, B, C, or D')
    with connect(path) as c:
        session=c.execute('SELECT submitted,student_id FROM quiz_sessions WHERE session_id=?',(session_id,)).fetchone()
        if not session or session['student_id'] != student_id: raise ValueError('Quiz session does not belong to this student')
        if session['submitted']: raise ValueError('This quiz was already submitted')
        if c.execute('SELECT 1 FROM questions WHERE question_id=?',(question_id,)).fetchone() is None: raise ValueError('Unknown question')
        if c.execute('SELECT 1 FROM student_responses WHERE session_id=? AND question_id=?',(session_id,question_id)).fetchone(): return False
        n=c.execute('SELECT COUNT(*) FROM student_responses WHERE student_id=? AND question_id=?',(student_id,question_id)).fetchone()[0]+1
        c.execute('INSERT INTO student_responses(session_id,student_id,question_id,selected_answer,is_correct,time_taken_seconds,attempt_number,confidence) VALUES(?,?,?,?,?,?,?,?)',(session_id,student_id,question_id,selected,int(selected==correct_answer),max(0,float(seconds)),n,confidence))
    return True

def submit_session(session_id, student_id, path=None):
    with connect(path) as c:
        c.execute("UPDATE quiz_sessions SET submitted=1, completion_time=CURRENT_TIMESTAMP WHERE session_id=? AND student_id=? AND submitted=0",(session_id,student_id))

def response_frame(student_id, path=None):
    with connect(path) as c: return pd.read_sql_query('''SELECT r.*,q.topic,q.subtopic,q.difficulty,q.concept,q.prerequisite,q.estimated_time,s.quiz_type FROM student_responses r JOIN questions q USING(question_id) JOIN quiz_sessions s USING(session_id) WHERE r.student_id=? ORDER BY r.timestamp,r.response_id''',c,params=(student_id,))

def sessions_frame(student_id, path=None):
    with connect(path) as c: return pd.read_sql_query('SELECT * FROM quiz_sessions WHERE student_id=? ORDER BY start_time DESC',(c),params=(student_id,))

def question_map(path=None): return {q['question_id']:q for q in question_rows(path)}

def save_tasks(student_id, tasks, path=None):
    with connect(path) as c:
        c.execute('DELETE FROM study_tasks WHERE student_id=?',(student_id,))
        for day,text,topic in tasks: c.execute('INSERT INTO study_tasks(student_id,day_number,task_text,topic) VALUES(?,?,?,?)',(student_id,day,text,topic))

def tasks(student_id,path=None):
    with connect(path) as c:return [dict(r) for r in c.execute('SELECT * FROM study_tasks WHERE student_id=? ORDER BY day_number,task_id',(student_id,))]

def complete_task(task_id, student_id, done, path=None):
    with connect(path) as c:c.execute('UPDATE study_tasks SET completed=? WHERE task_id=? AND student_id=?',(int(done),task_id,student_id))

def clear_student(student_id,path=None):
    with connect(path) as c:
        c.execute('DELETE FROM study_tasks WHERE student_id=?',(student_id,)); c.execute('DELETE FROM student_responses WHERE student_id=?',(student_id,)); c.execute('DELETE FROM quiz_sessions WHERE student_id=?',(student_id,)); c.execute('DELETE FROM topic_mastery WHERE student_id=?',(student_id,))

