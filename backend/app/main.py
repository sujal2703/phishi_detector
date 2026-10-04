"""FastAPI entry point for PHISHY. Submitted URLs are parsed locally only."""
from __future__ import annotations
import json
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,Field

from backend.app.ml.feature_extractor import URLValidationError
from backend.app.ml.unit1 import analyze as unit1_analyze
from backend.app.ml.unit4 import analyze as unit4_analyze
from backend.app.services.predictor import Predictor,ROOT

app=FastAPI(title='PHISHY API',version='1.0.0',description='Educational phishing URL analysis. Submitted URLs are never fetched.')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],
    # Vite picks the next port when its default is already occupied.
    allow_origin_regex=r'^https?://(localhost|127\.0\.0\.1):51(?:7[3-9]|[89]\d)$',
    allow_methods=['GET','POST'],
    allow_headers=['*'],
)
class PredictionRequest(BaseModel):
    url:str=Field(min_length=1,max_length=8192)

predictor=None
@app.on_event('startup')
def load_predictor():
    global predictor
    try:predictor=Predictor()
    except FileNotFoundError:predictor=None

@app.get('/health')
def health():return {'status':'ok','model_loaded':predictor is not None}

@app.post('/predict')
def predict(request:PredictionRequest):
    if predictor is None:raise HTTPException(status_code=503,detail='Model artifact unavailable. Run `python backend/scripts/train.py` first.')
    try:return predictor.predict(request.url)
    except URLValidationError as e:raise HTTPException(status_code=422,detail=str(e)) from e

@app.get('/model-info')
def model_info():
    if predictor is None:raise HTTPException(status_code=503,detail='Model artifact unavailable.')
    return predictor.info()

@app.get('/model-comparison')
def model_comparison():return json.loads((ROOT/'reports'/'model_comparison.json').read_text(encoding='utf-8'))

@app.get('/dataset-summary')
def dataset_summary():return json.loads((ROOT/'reports'/'dataset_summary.json').read_text(encoding='utf-8'))

@app.get('/unit1')
def unit1():return unit1_analyze()

@app.get('/unit3')
def unit3():return json.loads((ROOT/'reports'/'pca.json').read_text(encoding='utf-8'))

@app.get('/unit4')
def unit4(url:str):
    from backend.app.ml.feature_extractor import normalize_for_model
    try:return unit4_analyze(normalize_for_model(url))
    except URLValidationError as e:raise HTTPException(status_code=422,detail=str(e)) from e

@app.get('/unit5')
def unit5():
    if predictor is None:raise HTTPException(status_code=503,detail='Model artifact unavailable.')
    models=predictor.bundle['models'];names=list(predictor.features)
    def top(m):
        imp=getattr(m,'feature_importances_',None)
        if imp is None and hasattr(m,'weights'):imp=abs(m.weights[1:])
        if imp is None:return []
        return [{'feature':names[i],'importance':float(imp[i])} for i in sorted(range(len(imp)),key=lambda j:float(imp[j]),reverse=True)[:10]]
    return {'cart_splitting':'Binary Gini impurity reduction; greedy one-feature threshold splits.','cart':top(models['CART Decision Tree']),'random_forest':top(models['Random Forest']),'forest_trees':len(models['Random Forest'].trees)}

@app.get('/course-mapping')
def course_mapping():return json.loads((ROOT/'reports'/'course_mapping.json').read_text(encoding='utf-8'))
