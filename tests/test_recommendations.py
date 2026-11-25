import pandas as pd
from src.recommendations.recommender import recommend_topics
from src.analytics.mastery import calculate_mastery
from src.analytics.adaptive import select_next_question
from src.data.question_bank import QUESTIONS

def test_recommendation_explanation():
    d=pd.DataFrame({'topic':['DNS']*3,'is_correct':[0,0,1],'difficulty':['Easy']*3,'timestamp':pd.date_range('2025-01-01',periods=3)})
    rec=recommend_topics(calculate_mastery(d),d)
    assert rec and rec[0]['topic']=='DNS' and rec[0]['reason']

def test_adaptive_selection_avoids_attempted():
    q=select_next_question(QUESTIONS,[QUESTIONS[0]['question_id']],{'DNS':1},[False])
    assert q and q['question_id']!=QUESTIONS[0]['question_id']
