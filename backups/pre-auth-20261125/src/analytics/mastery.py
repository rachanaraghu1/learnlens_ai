"""Transparent mastery estimate that shrinks low-sample topics toward a neutral prior."""
import numpy as np
import pandas as pd

THRESHOLDS=[(40,'Needs significant revision'),(60,'Developing'),(75,'Intermediate'),(90,'Strong'),(101,'Excellent')]

def calculate_mastery(responses, minimum_attempts=5):
    if responses.empty:return pd.DataFrame(columns=['topic','mastery_score','accuracy','recent_accuracy','total_attempts','confidence','revision_status','trend'])
    results=[]
    for topic,g in responses.groupby('topic'):
        g=g.sort_values('timestamp') if 'timestamp' in g else g
        y=g['is_correct'].astype(float).to_numpy(); n=len(y); acc=float(y.mean()); recent=float(y[-5:].mean());
        # Half prior of 0.5 limits overconfidence from tiny samples; difficulty credit is modest.
        difficulty=g['difficulty'].map({'Easy':0,'Medium':.5,'Hard':1}).fillna(.5).mean() if 'difficulty' in g else .5
        adjusted=(y.sum()+1)/(n+2); trend=float(y[-min(5,n):].mean()-y[:min(5,n)].mean()) if n>=2 else 0
        recency=1. if 'timestamp' not in g else max(.55,1-min(180,(pd.Timestamp.now()-pd.to_datetime(g['timestamp'].iloc[-1])).days)/400)
        score=float(np.clip(100*(.62*adjusted+.2*recent+.1*difficulty*.25+.08*np.clip(trend,-.5,.5))*recency,0,100))
        status=next(label for cut,label in THRESHOLDS if score<cut)
        results.append({'topic':topic,'mastery_score':round(score,1),'accuracy':round(acc*100,1),'recent_accuracy':round(recent*100,1),'total_attempts':n,'confidence':min(1,n/minimum_attempts),'revision_status':status,'trend':round(trend*100,1)})
    return pd.DataFrame(results).sort_values('mastery_score')
