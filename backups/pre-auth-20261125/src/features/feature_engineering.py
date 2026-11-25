"""Chronological, prior-only features. A row never sees its own outcome."""
import numpy as np
import pandas as pd

FEATURE_COLUMNS=['topic_accuracy','topic_attempts','topic_correct','topic_incorrect','recent_accuracy','average_time','difficulty_level','difficulty_accuracy','days_since_topic','recent_trend','repeated_mistakes','attempt_number']
DIFFICULTY={'Easy':0,'Medium':1,'Hard':2}

def build_features(attempts, include_target=True):
    df=attempts.copy()
    if df.empty:
        return pd.DataFrame(columns=FEATURE_COLUMNS+(['is_correct'] if include_target else []))
    df['timestamp']=pd.to_datetime(df.get('timestamp',pd.Series(pd.Timestamp.now(),index=df.index)),errors='coerce').fillna(pd.Timestamp.now())
    df=df.sort_values(['timestamp'] + (['response_id'] if 'response_id' in df else [])).reset_index(drop=True)
    output=[]; histories={}; global_times=[]
    for _,r in df.iterrows():
        topic=str(r.get('topic','Unknown')); diff=str(r.get('difficulty','Easy')); hist=histories.setdefault(topic,[])
        prior=hist; last=prior[-1]['timestamp'] if prior else None
        recent=prior[-5:]; acc=float(np.mean([x['correct'] for x in prior])) if prior else .5
        recent_acc=float(np.mean([x['correct'] for x in recent])) if recent else .5
        half=max(1,len(recent)//2); trend=(float(np.mean([x['correct'] for x in recent[-half:]])-np.mean([x['correct'] for x in recent[:half]])) if len(recent)>1 else 0.)
        same=[x for x in prior if x['difficulty']==diff]
        # Count earlier wrong repeats of this same item, not merely any topic errors.
        current_question=str(r.get('question_id',''))
        mistakes=sum(1 for x in prior if x.get('question_id')==current_question and not x['correct'])
        now=r['timestamp']
        output.append({'topic_accuracy':acc,'topic_attempts':len(prior),'topic_correct':sum(x['correct'] for x in prior),'topic_incorrect':sum(not x['correct'] for x in prior),'recent_accuracy':recent_acc,'average_time':float(np.mean([x['seconds'] for x in prior])) if prior else float(r.get('estimated_time',45)),'difficulty_level':DIFFICULTY.get(diff,1),'difficulty_accuracy':float(np.mean([x['correct'] for x in same])) if same else .5,'days_since_topic':min(365.,max(0.,(now-last).total_seconds()/86400)) if last is not None else 30.,'recent_trend':trend,'repeated_mistakes':mistakes,'attempt_number':int(r.get('attempt_number',1))})
        hist.append({'question_id':current_question,'correct':int(r.get('is_correct',0)),'difficulty':diff,'seconds':float(r.get('time_taken_seconds',45) or 0),'timestamp':now})
    result=pd.DataFrame(output,index=df.index)
    if include_target: result['is_correct']=df['is_correct'].astype(int).to_numpy()
    return result.replace([np.inf,-np.inf],np.nan).fillna(0)
