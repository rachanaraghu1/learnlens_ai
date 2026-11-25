"""Pattern summaries for transparent learning analytics."""
import pandas as pd

def mistake_summary(responses):
    if responses.empty:return pd.DataFrame(columns=['topic','subtopic','mistakes'])
    wrong=responses[responses['is_correct']==0]
    if wrong.empty:return pd.DataFrame(columns=['topic','subtopic','mistakes'])
    return wrong.groupby(['topic','subtopic']).size().reset_index(name='mistakes').sort_values('mistakes',ascending=False)

def performance_patterns(responses):
    patterns=[]
    if responses.empty:return patterns
    for topic,g in responses.groupby('topic'):
        if len(g)>=2 and g['is_correct'].tail(min(5,len(g))).mean()-g['is_correct'].head(min(5,len(g))).mean()>.2: patterns.append(f"{topic}: accuracy is improving across the recorded attempts.")
        easy=g[g.difficulty=='Easy']; hard=g[g.difficulty=='Hard']
        if len(easy)>=2 and len(hard)>=2 and easy.is_correct.mean()>.7 and hard.is_correct.mean()<.5: patterns.append(f"{topic}: fundamentals look stronger than harder application questions.")
    return patterns
