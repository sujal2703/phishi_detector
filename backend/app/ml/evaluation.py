"""Metrics and ROC data implemented without evaluation-set dependencies."""
from __future__ import annotations
import numpy as np


def auc_score(y, score):
    y=np.asarray(y,dtype=int);score=np.asarray(score,dtype=float)
    order=np.argsort(score,kind="mergesort"); ranks=np.empty(len(order),float)
    sorted_s=score[order]; i=0
    while i<len(order):
        j=i+1
        while j<len(order) and sorted_s[j]==sorted_s[i]:j+=1
        ranks[order[i:j]]=(i+1+j)/2.0
        i=j
    n1=int(y.sum());n0=len(y)-n1
    if not n1 or not n0:return None
    return float((ranks[y==1].sum()-n1*(n1+1)/2)/(n1*n0))


def evaluate(y, probability, score=None, threshold=0.5):
    y=np.asarray(y,dtype=int);p=np.asarray(probability,dtype=float)
    pred=(p>=threshold).astype(int)
    tp=int(np.sum((y==1)&(pred==1)));tn=int(np.sum((y==0)&(pred==0)))
    fp=int(np.sum((y==0)&(pred==1)));fn=int(np.sum((y==1)&(pred==0)))
    precision=tp/(tp+fp) if tp+fp else 0.0;recall=tp/(tp+fn) if tp+fn else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    auc=auc_score(y, p if score is None else score)
    values=p if score is None else score
    order=np.argsort(values,kind="mergesort")[::-1]
    pos=int(y.sum());neg=len(y)-pos;tpv=fpv=0;roc=[[0.0,0.0]];i=0
    while i<len(order):
        j=i+1
        while j<len(order) and values[order[j]]==values[order[i]]:j+=1
        group=y[order[i:j]];tpv+=int(group.sum());fpv+=int(len(group)-group.sum())
        roc.append([fpv/neg if neg else 0.0,tpv/pos if pos else 0.0])
        i=j
    if len(roc)>201:
        ix=np.linspace(0,len(roc)-1,201).astype(int);roc=[roc[k] for k in ix]
    return {"accuracy":float((tp+tn)/len(y)),"precision":precision,"recall":recall,"f1":f1,
            "roc_auc":auc,"threshold":threshold,"confusion_matrix":{"labels":["legitimate","phishing"],"matrix":[[tn,fp],[fn,tp]]},"roc_curve":roc}
