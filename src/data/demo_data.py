"""Populate five clearly labeled local demo profiles once on first launch."""
import random, uuid
from src.database.db import connect
from src.database.repository import students, clear_student
from src.data.question_bank import QUESTIONS

DEMO_PROFILES=[('Alex Morgan','High-performing student'),('Sam Rivera','Inconsistent performance'),('Jordan Lee','Strong fundamentals, weaker problem-solving'),('Taylor Kim','Improves through practice'),('Casey Patel','Previously learned concepts need refreshing')]

def seed_demo(path=None):
    with connect(path) as c:
        seeded=c.execute("SELECT 1 FROM app_metadata WHERE metadata_key='demo_seeded'").fetchone()
    if seeded:return
    existing=[s for s in students(path) if s['is_demo']]
    if len(existing)==len(DEMO_PROFILES): return
    # Recover cleanly if an earlier interrupted first launch left only some demo profiles.
    for profile in existing:
        clear_student(profile['student_id'],path)
        with connect(path) as c:c.execute('DELETE FROM students WHERE student_id=?',(profile['student_id'],))
    rng=random.Random(71)
    with connect(path) as c:
        for idx,(name,_) in enumerate(DEMO_PROFILES):
            sid='demo_'+uuid.uuid4().hex[:12]
            c.execute('INSERT INTO students(student_id,student_name,is_demo) VALUES(?,?,1)',(sid,name))
            # One session per demo profile; individual records retain chronological ordering.
            sid_session='quiz_'+uuid.uuid4().hex[:12]
            c.execute('INSERT INTO quiz_sessions(session_id,student_id,quiz_type,total_questions) VALUES(?,?,?,?)',(sid_session,sid,'Demo history',len(QUESTIONS)))
            for j,q in enumerate(QUESTIONS):
                if idx==0: p=.88
                elif idx==1: p=.48 if j%2 else .82
                elif idx==2: p=.82 if q['difficulty']=='Easy' else .32
                elif idx==3: p=.35 if j==0 else .88
                else: p=.82 if j==0 else .3
                correct=rng.random()<p; ans=q['correct_answer'] if correct else next(x for x in 'ABCD' if x!=q['correct_answer'])
                c.execute('INSERT INTO student_responses(session_id,student_id,question_id,selected_answer,is_correct,time_taken_seconds,attempt_number) VALUES(?,?,?,?,?,?,1)',(sid_session,sid,q['question_id'],ans,int(correct),q['estimated_time']*(.85 if correct else 1.4)))
            c.execute('UPDATE quiz_sessions SET submitted=1,completion_time=CURRENT_TIMESTAMP WHERE session_id=?',(sid_session,))
        c.execute("INSERT OR REPLACE INTO app_metadata(metadata_key,metadata_value) VALUES('demo_seeded','1')")
