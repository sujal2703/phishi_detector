"""Load persisted training artifacts and perform network-free inference."""
from __future__ import annotations
import json,pickle
from pathlib import Path
import numpy as np

from backend.app.ml.feature_extractor import MODEL_FEATURES,extract_url_features,select_model_vector,normalize_for_model
from backend.app.ml.unit4 import analyze as analyze_sequence
from .explainer import explain

ROOT=Path(__file__).resolve().parents[3]
MODEL_PATH=ROOT/'models'/'phishy_models.pkl'
SUMMARY_PATH=ROOT/'reports'/'dataset_summary.json'
COMPARISON_PATH=ROOT/'reports'/'model_comparison.json'

class Predictor:
    def __init__(self,model_path=MODEL_PATH):
        with Path(model_path).open('rb') as f:self.bundle=pickle.load(f)
        self.summary=json.loads(SUMMARY_PATH.read_text(encoding='utf-8'))
        self.comparison=json.loads(COMPARISON_PATH.read_text(encoding='utf-8'))
        self.features=self.bundle['features'];self.scaler=self.bundle['scaler']
        self.model=self.bundle['models'][self.bundle['primary_model']]

    def predict(self,url):
        features=extract_url_features(url)
        vector=np.asarray(select_model_vector(features),dtype=float).reshape(1,-1)
        standardized=self.scaler.transform(vector)[0]
        probability=float(self.model.predict_proba(standardized.reshape(1,-1))[0,1])
        threshold=float(self.bundle['threshold']);label=int(probability>=threshold)
        risk='high' if label else 'low'
        seq=normalize_for_model(url)
        markov=analyze_sequence(seq)
        uncertainty=float(self.model.uncertainty(standardized.reshape(1,-1))[0])
        return {'prediction':label,'prediction_label':'Phishing' if label else 'Legitimate','probability':probability,
          'risk_level':risk,'model':self.bundle['primary_model'],'threshold':threshold,
          'extracted_features':{name:features[name] for name in MODEL_FEATURES},
          'explanation':explain({name:features[name] for name in MODEL_FEATURES},standardized,self.model,MODEL_FEATURES,self.bundle['training_feature_stats']),
          'sequential_score':markov['mean_transition_surprise'],'sequential_analysis':markov,
          'bayesian_parameter_uncertainty':uncertainty,
          'caveat':'Experimental prediction on precomputed source features; exact upstream extractor parity and live predictive validity are unverified.'}

    def info(self):
        m=self.model
        return {'model':self.bundle['primary_model'],'type':'Bayesian logistic regression with Gaussian prior and Laplace posterior approximation','features':list(self.features),'threshold':self.bundle['threshold'],'split':self.bundle['split'],'prior_sd':float(m.prior_sd),'posterior_iterations':int(m.iterations),'risk_levels':{'low':'p(phishing) < 0.5','high':'p(phishing) >= 0.5'},'limitations':self.comparison['limitations']}
