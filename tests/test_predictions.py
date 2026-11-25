import pandas as pd
from src.models.predict import predict_probability
from src.models.train import train_models

def test_prediction_when_model_missing():
    from pathlib import Path
    p=predict_probability({},None,Path('models/definitely_missing.joblib'))
    assert p['probability'] is None and p['source']=='fallback'

def test_training_small_synthetic():
    from src.data.data_generator import generate_training_data
    from pathlib import Path
    import uuid
    data_path=Path('tests')/f"training_{uuid.uuid4().hex}.csv"
    model_path=Path('tests')/f"model_{uuid.uuid4().hex}.joblib"
    metrics_path=Path('tests')/f"metrics_{uuid.uuid4().hex}.json"
    try:
        data=generate_training_data(students=12,attempts_per_student=20,output_path=data_path)
        bundle=train_models(data,model_path=model_path,metrics_path=metrics_path)
        assert bundle['model_name'] in bundle['metrics']
        from src.models.predict import predict_probability
        prediction=predict_probability(data.iloc[0].to_dict(),bundle)
        assert 0 <= prediction['probability'] <= 1
    finally:
        data_path.unlink(missing_ok=True); model_path.unlink(missing_ok=True); metrics_path.unlink(missing_ok=True)
