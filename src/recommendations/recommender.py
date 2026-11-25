"""Explainable rule-based revision ranking; ML estimates are displayed separately."""
import pandas as pd

def recommend_topics(mastery, responses, limit=5):
    if mastery.empty:return []
    last={}
    if not responses.empty:
        for topic,g in responses.groupby('topic'):
            last[topic]=pd.to_datetime(g.timestamp.max(),errors='coerce')
    now=pd.Timestamp.now(); recs=[]
    for _,r in mastery.iterrows():
        practiced=last.get(r.topic); days=(now-practiced).days if practiced is not None and pd.notna(practiced) else 90
        prerequisite=''
        if not responses.empty and 'prerequisite' in responses:
            missed=responses[(responses['topic']==r.topic)&(responses['is_correct']==0)]
            prerequisites=missed['prerequisite'].dropna().astype(str)
            prerequisites=prerequisites[prerequisites.str.len()>0]
            if not prerequisites.empty: prerequisite=prerequisites.mode().iloc[0]
        low=max(0,75-float(r.mastery_score))/75; stale=min(days/90,1); sample=max(0,1-float(r.confidence))
        score=.65*low+.2*stale+.15*sample
        reasons=[]
        if r.recent_accuracy<60: reasons.append(f"recent accuracy is {r.recent_accuracy:.0f}%")
        if r.total_attempts<5: reasons.append(f"there are only {int(r.total_attempts)} attempts, so the estimate is uncertain")
        if days>30: reasons.append(f"it has been about {days} days since practice")
        if not reasons: reasons.append(f"mastery is {r.mastery_score:.0f}%")
        recs.append({'topic':r.topic,'priority':round(score,3),'reason':'; '.join(reasons),'mastery_score':r.mastery_score,'suggested_difficulty':'Easy' if r.mastery_score<45 else 'Medium','prerequisite':prerequisite})
    return sorted(recs,key=lambda x:x['priority'],reverse=True)[:limit]
