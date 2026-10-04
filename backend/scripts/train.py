"""Fit and evaluate PHISHY's five comparative classifiers on the fixed split."""
from __future__ import annotations
import json,pickle,sys
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from backend.app.ml.unit1 import load_data, analyze
from backend.app.ml.feature_extractor import MODEL_FEATURES
from backend.app.ml.preprocessing import Standardizer,matrix_from_frame,grouped_split
from backend.app.ml.models import BayesianLogistic,LogisticRegression,LinearSVM,CART,RandomForest
from backend.app.ml.evaluation import evaluate
from backend.app.ml.unit3 import PCA

OUT=ROOT/'models';REPORTS=ROOT/'reports'

def main():
    OUT.mkdir(exist_ok=True);REPORTS.mkdir(exist_ok=True)
    df=load_data(); y=df['phishing'].to_numpy(dtype=int); x=matrix_from_frame(df)
    train_idx,test_idx=grouped_split(df,0.2,42)
    scaler=Standardizer.fit(x[train_idx]);xtr=scaler.transform(x[train_idx]);xte=scaler.transform(x[test_idx])
    ytr,yte=y[train_idx],y[test_idx]
    models={
      'Bayesian Logistic Regression (Laplace)':BayesianLogistic.fit(xtr,ytr,prior_sd=2.0),
      'Logistic Regression':LogisticRegression.fit(xtr,ytr,l2=1.0),
      'Linear SVM':LinearSVM.fit(xtr,ytr,c=0.03,epochs=18,seed=42),
      'CART Decision Tree':CART(max_depth=7,min_leaf=40,seed=42).fit(xtr,ytr),
      'Random Forest':RandomForest(n_trees=12,max_depth=7,min_leaf=40,seed=42).fit(xtr,ytr),
    }
    comparison={};predictions={}
    for name,model in models.items():
        probability=model.predict_proba(xte)[:,1]
        if isinstance(model,LinearSVM): score=model.decision_function(xte)
        elif hasattr(model,'decision_function'):score=model.decision_function(xte)
        else:score=probability
        result=evaluate(yte,probability,score,0.5)
        result['model']=name
        comparison[name]=result;predictions[name]=probability
    training_stats={name:{'quantiles':{'0.95':float(np.quantile(x[train_idx,j],0.95))}} for j,name in enumerate(MODEL_FEATURES)}
    artifacts={'models':models,'scaler':scaler,'features':MODEL_FEATURES,'primary_model':'Bayesian Logistic Regression (Laplace)','threshold':0.5,'training_feature_stats':training_stats,
      'split':{'seed':42,'test_fraction_requested':0.2,'train_rows':len(train_idx),'test_rows':len(test_idx),'grouped_by_all_111_predictors':True},
      'training_summary':{'rows':len(train_idx),'class_counts':{'legitimate':int((ytr==0).sum()),'phishing':int((ytr==1).sum())}}}
    with (OUT/'phishy_models.pkl').open('wb') as f:pickle.dump(artifacts,f,pickle.HIGHEST_PROTOCOL)
    public={'status':'trained','target':'phishing=1','feature_names':list(MODEL_FEATURES),'split':artifacts['split'],'preprocessing':{'standardization':'mean/std fitted on train partition only','test_partition_used_for_fit':False},'threshold':0.5,'models':comparison,
      'limitations':['Training uses same-named precomputed dataset columns; historical raw URLs are unavailable, so exact parity with the reconstructed live extractor cannot be verified.','Linear SVM probability values are sigmoid-transformed decision scores and are not calibrated probabilities.','Evaluation is a single grouped holdout split; it is not an external validation study.']}
    (REPORTS/'model_comparison.json').write_text(json.dumps(public,indent=2),encoding='utf-8')
    (REPORTS/'dataset_summary.json').write_text(json.dumps(analyze(df),indent=2),encoding='utf-8')
    pca=PCA(2).fit(xtr);coords=pca.transform(xtr)
    rng=np.random.default_rng(42);take=np.sort(rng.choice(len(coords),min(2500,len(coords)),replace=False))
    pca_data={'method':'centered covariance matrix and symmetric eigen-decomposition','fit_partition':'training only','explained_variance_ratio':pca.explained_variance_ratio_.tolist(),'cumulative_explained_variance':np.cumsum(pca.explained_variance_ratio_).tolist(),'coordinates':coords[take].tolist(),'labels':ytr[take].tolist()}
    (REPORTS/'pca.json').write_text(json.dumps(pca_data),encoding='utf-8')
    print(f"Saved model bundle; split train={len(train_idx)} test={len(test_idx)}")
    for name,result in comparison.items():print(name, {k:round(result[k],4) if isinstance(result[k],float) else result[k] for k in ('accuracy','precision','recall','f1','roc_auc')})

if __name__=='__main__':main()
