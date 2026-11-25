"""Train and compare a logistic regression and random forest on prior-only features."""
import json
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from config import TRAINING_PATH, MODEL_PATH, METRICS_PATH, MODEL_DIR
from src.features.feature_engineering import FEATURE_COLUMNS
from src.data.data_generator import generate_training_data

def train_models(data=None, seed=42, model_path=MODEL_PATH, metrics_path=METRICS_PATH):
    if data is None:
        data=pd.read_csv(TRAINING_PATH) if TRAINING_PATH.exists() else generate_training_data()
    if 'student_id' not in data: data=data.copy(); data['student_id']='single_group'
    X=data[FEATURE_COLUMNS].replace([np.inf,-np.inf],np.nan).fillna(0); y=data['is_correct'].astype(int); groups=data['student_id']
    split=GroupShuffleSplit(n_splits=1,test_size=.22,random_state=seed); tr,te=next(split.split(X,y,groups))
    # Single-process fitting keeps local demos and restricted Windows environments reliable.
    candidates={'Logistic Regression':make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,class_weight='balanced',random_state=seed)), 'Random Forest':RandomForestClassifier(n_estimators=180,min_samples_leaf=3,class_weight='balanced_subsample',max_features='sqrt',random_state=seed,n_jobs=1)}
    metrics={}; fitted={}
    for name,model in candidates.items():
        model.fit(X.iloc[tr],y.iloc[tr]); fitted[name]=model
        prob=model.predict_proba(X.iloc[te])[:,1]; pred=(prob>=.5).astype(int)
        metrics[name]={'accuracy':float(accuracy_score(y.iloc[te],pred)),'precision':float(precision_score(y.iloc[te],pred,zero_division=0)),'recall':float(recall_score(y.iloc[te],pred,zero_division=0)),'f1':float(f1_score(y.iloc[te],pred,zero_division=0)),'roc_auc':float(roc_auc_score(y.iloc[te],prob)) if len(np.unique(y.iloc[te]))==2 else None,'confusion_matrix':confusion_matrix(y.iloc[te],pred).tolist()}
    chosen=max(metrics,key=lambda n:(metrics[n]['roc_auc'] or 0,metrics[n]['f1']))
    # Keep a true held-out evaluation, and a final all-data estimator for inference.
    final=candidates[chosen].fit(X,y)
    bundle={'model':final,'model_name':chosen,'feature_columns':FEATURE_COLUMNS,'metrics':metrics,'synthetic':True,'trained_rows':len(data)}
    model_path.parent.mkdir(parents=True,exist_ok=True); metrics_path.parent.mkdir(parents=True,exist_ok=True)
    dump(bundle,model_path)
    metrics_path.write_text(json.dumps({'selected_model':chosen,'models':metrics,'synthetic':True,'trained_rows':len(data)},indent=2),encoding='utf-8')
    return bundle

if __name__=='__main__':
    result=train_models(); print(f"Selected {result['model_name']}; held-out group metrics saved to {METRICS_PATH}")
