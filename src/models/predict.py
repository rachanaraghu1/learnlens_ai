"""Load a fitted model and return a calibrated-looking estimate, or explicit fallback."""
from joblib import load
import pandas as pd
from config import MODEL_PATH
from src.features.feature_engineering import FEATURE_COLUMNS

def load_model(path=MODEL_PATH):
    try: return load(path)
    except (FileNotFoundError, OSError): return None

def predict_probability(features, bundle=None, model_path=MODEL_PATH):
    bundle=bundle or load_model(model_path)
    if bundle is None: return {'probability':None,'source':'fallback','reason':'No trained model is available yet. Train the model to enable estimates.'}
    row={c:features.get(c,0) for c in bundle.get('feature_columns',FEATURE_COLUMNS)}
    probability=float(bundle['model'].predict_proba(pd.DataFrame([row]))[0,1])
    return {'probability':probability,'source':'synthetic-trained model','model_name':bundle['model_name'],'reason':'Estimate from prior behavior and question difficulty; synthetic-data evaluation is not evidence of real-student accuracy.'}
