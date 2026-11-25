import pandas as pd
from src.features.feature_engineering import build_features

def test_prior_only_features_and_order():
    df=pd.DataFrame([{'topic':'DNS','difficulty':'Easy','is_correct':0,'time_taken_seconds':40,'timestamp':'2025-01-01'}, {'topic':'DNS','difficulty':'Easy','is_correct':1,'time_taken_seconds':20,'timestamp':'2025-01-02'}])
    x=build_features(df)
    assert x.loc[0,'topic_attempts']==0 and x.loc[1,'topic_attempts']==1
    assert x.loc[1,'topic_accuracy']==0 and x.loc[1,'topic_correct']==0

def test_empty_features():
    assert build_features(pd.DataFrame()).empty
