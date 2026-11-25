"""Time-series aggregation helpers."""
import pandas as pd

def accuracy_over_time(responses):
    if responses.empty:return pd.DataFrame(columns=['date','accuracy','attempts'])
    d=responses.copy(); d['date']=pd.to_datetime(d.timestamp).dt.date
    return d.groupby('date').is_correct.agg(accuracy='mean',attempts='count').reset_index().assign(accuracy=lambda x:x.accuracy*100)
