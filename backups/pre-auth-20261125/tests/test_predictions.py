import pandas as pd
from src.models.predict import predict_probability
from src.models.train import train_models

def test_prediction_when_model_missing():
    from pathlib import Path
    p=predict_probability({},None,Path('models/definitely_missing.joblib'))
    assert p['probability'] is None and p['source']=='fallback'

def test_training_small_synthetic():
    from src.data.data_generator import generate_training_data
    data=generate_training_data(students=12,attempts_per_student=20,output_path=__import__('pathlib').Path('datasets/test_training_tmp.csv'))
    bundle=train_models(data)
    assert bundle['model_name'] in bundle['metrics']
    __import__('pathlib').Path('datasets/test_training_tmp.csv').unlink(missing_ok=True)
