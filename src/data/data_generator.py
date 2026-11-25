"""Generate reproducible synthetic student attempts for a demonstration model."""
import numpy as np
import pandas as pd
from src.data.question_bank import QUESTIONS
from src.features.feature_engineering import build_features
from config import TRAINING_PATH

def generate_training_data(students=120, attempts_per_student=70, seed=42, output_path=TRAINING_PATH):
    rng=np.random.default_rng(seed); rows=[]; topics=list({q['topic'] for q in QUESTIONS});
    topic_skill={}
    for s in range(students):
        sid=f'synthetic_{s:03d}'; skill=float(rng.beta(4,4)); topic_skill[sid]={t:float(np.clip(skill+rng.normal(0,.17),.08,.92)) for t in topics}; practice={t:0 for t in topics}; ts=pd.Timestamp('2025-01-01')+pd.Timedelta(days=int(rng.integers(0,300)))
        history=[]; question_attempts={}; seen_questions=[]
        for idx in range(attempts_per_student):
            # About one in six attempts revisits an earlier item, creating realistic retries.
            if seen_questions and rng.random()<.17:
                q=seen_questions[int(rng.integers(0,len(seen_questions)))]
            else:
                q=QUESTIONS[int(rng.integers(0,len(QUESTIONS)))]; seen_questions.append(q)
            topic=q['topic']; practice[topic]+=1; question_attempts[q['question_id']]=question_attempts.get(q['question_id'],0)+1
            # Skill, modest practice gains, difficulty and forgetting influence outcomes.
            days=(ts-(history[-1]['timestamp'] if history else ts-pd.Timedelta(days=20))).days
            p=np.clip(topic_skill[sid][topic]+min(.16,practice[topic]*.012)-({'Easy':-.17,'Medium':0,'Hard':.20}[q['difficulty']])-max(0,days-45)*.0008,.08,.95)
            correct=int(rng.random()<p); seconds=float(np.clip(rng.normal(q['estimated_time']*(1.25 if not correct else .9),12),8,180))
            history.append({'question_id':q['question_id'],'topic':topic,'difficulty':q['difficulty'],'is_correct':correct,'time_taken_seconds':seconds,'attempt_number':question_attempts[q['question_id']],'estimated_time':q['estimated_time'],'timestamp':ts})
            ts += pd.Timedelta(hours=int(rng.integers(1,72)))
        f=build_features(pd.DataFrame(history)); f['student_id']=sid; rows.append(f)
    out=pd.concat(rows,ignore_index=True); output_path.parent.mkdir(parents=True,exist_ok=True); out.to_csv(output_path,index=False); return out

if __name__=='__main__':
    data=generate_training_data(); print(f'Wrote {len(data):,} synthetic attempts to {TRAINING_PATH}')
