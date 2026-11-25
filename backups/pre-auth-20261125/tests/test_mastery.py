import pandas as pd
from src.analytics.mastery import calculate_mastery

def test_mastery_empty_and_low_sample():
    assert calculate_mastery(pd.DataFrame()).empty
    d=pd.DataFrame({'topic':['DNS']*2,'is_correct':[1,1],'difficulty':['Easy']*2,'timestamp':pd.to_datetime(['2025-01-01','2025-01-02'])})
    row=calculate_mastery(d).iloc[0]
    assert row.total_attempts==2 and row.confidence<1 and row.mastery_score<100
