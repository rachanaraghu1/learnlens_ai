"""Transparent rule-based adaptive question selection."""
import random

def select_next_question(candidates, attempted_ids, topic_priority=None, recent_correct=None, rng=None):
    rng=rng or random.Random(); topic_priority=topic_priority or {}; recent_correct=recent_correct or []
    available=[q for q in candidates if q['question_id'] not in set(attempted_ids)]
    if not available:return None
    if len(recent_correct)>=2 and all(recent_correct[-2:]): target='Hard'
    elif recent_correct and not recent_correct[-1]: target='Easy'
    else: target='Medium'
    max_priority=max(topic_priority.values(),default=0)
    ranked=[]
    for q in available:
        score=(2.0 if q['difficulty']==target else 0.0)+topic_priority.get(q['topic'],0)*2+rng.random()*.15
        ranked.append((score,q))
    ranked.sort(key=lambda x:x[0],reverse=True)
    return ranked[0][1]
