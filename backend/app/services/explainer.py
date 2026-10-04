"""Deterministic feature- and model-based prediction explanations."""
from __future__ import annotations

def explain(features, standardized, model, feature_names, quantiles):
    reasons=[]
    for name,value in features.items():
        q95=quantiles[name]["quantiles"]["0.95"]
        if value>q95 and value>0:
            reasons.append({"feature":name,"value":value,"reason":f"{name} is above the dataset 95th percentile ({q95:.2f}).","direction":"elevated indicator"})
    try:
        contributions=standardized*model.weights[1:]
        ranked=sorted(zip(feature_names,contributions),key=lambda pair:abs(float(pair[1])),reverse=True)[:5]
        for name,value in ranked:
            if abs(float(value))>=0.05:
                reasons.append({"feature":name,"value":features[name],"reason":f"The Bayesian logistic model's fitted coefficient contributes {float(value):+.3f} log-odds at this value.","direction":"phishing" if value>0 else "legitimate"})
    except (AttributeError,IndexError):
        pass
    if features["qty_questionmark_url"] and features["qty_equal_url"]:
        reasons.append({"feature":"qty_questionmark_url","value":features["qty_questionmark_url"],"reason":"The feature representation contains a query delimiter and equals sign.","direction":"observed structure"})
    return reasons[:8]
