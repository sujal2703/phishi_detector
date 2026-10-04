"""Small transparent NumPy implementations used for reproducible teaching."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np


def sigmoid(z):
    z = np.clip(z, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-z))


def _design(x):
    return np.column_stack([np.ones(len(x)), np.asarray(x, dtype=float)])


@dataclass
class BayesianLogistic:
    weights: np.ndarray
    covariance: np.ndarray
    prior_sd: float = 2.0
    iterations: int = 0

    @staticmethod
    def log_likelihood(x, y, weights):
        d=_design(x);y=np.asarray(y,dtype=float);p=np.clip(sigmoid(d@weights),1e-12,1-1e-12)
        return float(np.sum(y*np.log(p)+(1-y)*np.log(1-p)))

    @staticmethod
    def log_prior(weights, prior_sd=2.0):
        w=np.asarray(weights,dtype=float)
        return float(-0.5*np.sum((w[1:]/prior_sd)**2)-len(w[1:])*np.log(prior_sd*np.sqrt(2*np.pi)))

    @classmethod
    def log_posterior(cls,x,y,weights,prior_sd=2.0):
        return cls.log_likelihood(x,y,weights)+cls.log_prior(weights,prior_sd)

    @classmethod
    def fit(cls, x, y, prior_sd=2.0, max_iter=80):
        d = _design(x); y = np.asarray(y, dtype=float)
        precision = np.eye(d.shape[1]) / (prior_sd * prior_sd)
        precision[0, 0] = 1e-8  # weak intercept prior
        w = np.zeros(d.shape[1])
        for iteration in range(max_iter):
            p = sigmoid(d @ w)
            grad = d.T @ (p - y) + precision @ w
            curvature = p * (1 - p)
            hessian = (d.T * curvature) @ d + precision
            step = np.linalg.solve(hessian, grad)
            w -= step
            if np.linalg.norm(step) < 1e-7:
                break
        p = sigmoid(d @ w)
        hessian = (d.T * (p * (1 - p))) @ d + precision
        return cls(w, np.linalg.inv(hessian), prior_sd, iteration + 1)

    def predict_proba(self, x):
        p = sigmoid(_design(x) @ self.weights)
        return np.column_stack([1 - p, p])

    def uncertainty(self, x):
        d = _design(x)
        return np.sqrt(np.maximum(np.einsum("ij,jk,ik->i", d, self.covariance, d), 0))


@dataclass
class LogisticRegression:
    weights: np.ndarray
    iterations: int = 0

    @classmethod
    def fit(cls, x, y, l2=1.0, max_iter=80):
        d = _design(x); y = np.asarray(y, dtype=float)
        penalty = np.eye(d.shape[1]) * l2; penalty[0, 0] = 0
        w = np.zeros(d.shape[1])
        for iteration in range(max_iter):
            p = sigmoid(d @ w)
            grad = d.T @ (p - y) + penalty @ w
            h = (d.T * (p * (1 - p))) @ d + penalty + np.eye(d.shape[1]) * 1e-8
            step = np.linalg.solve(h, grad); w -= step
            if np.linalg.norm(step) < 1e-7: break
        return cls(w, iteration + 1)

    def predict_proba(self, x):
        p = sigmoid(_design(x) @ self.weights)
        return np.column_stack([1 - p, p])


@dataclass
class LinearSVM:
    weights: np.ndarray
    bias: float
    epochs: int = 0

    @classmethod
    def fit(cls, x, y, c=0.03, epochs=18, seed=42):
        x = np.asarray(x, dtype=float); y = 2 * np.asarray(y, dtype=float) - 1
        w = np.zeros(x.shape[1]); b = 0.0
        # Full-batch hinge-loss subgradient descent with a decaying step size.
        n = len(y)
        for epoch in range(epochs):
            margins = y * (x @ w + b)
            active = margins < 1.0
            eta = 0.08 / np.sqrt(epoch + 1)
            w -= eta * (c * w - (x[active].T @ y[active]) / n)
            if active.any(): b += eta * float(y[active].sum()) / n
        return cls(w, b, epochs)

    def decision_function(self, x): return np.asarray(x) @ self.weights + self.bias
    def predict_proba(self, x):
        p = sigmoid(self.decision_function(x))
        return np.column_stack([1 - p, p])


class CART:
    """Binary Gini CART with exhaustive one-dimensional threshold scans."""
    def __init__(self, max_depth=7, min_leaf=40, max_features=None, seed=42):
        self.max_depth=max_depth; self.min_leaf=min_leaf; self.max_features=max_features; self.seed=seed
        self.tree=None; self.feature_importances_=None

    def fit(self, x, y):
        self.x=np.asarray(x,dtype=float); self.y=np.asarray(y,dtype=int)
        self.importance=np.zeros(self.x.shape[1]); self.rng=np.random.default_rng(self.seed)
        self.tree=self._grow(np.arange(len(self.y)),0)
        if self.importance.sum(): self.importance/=self.importance.sum()
        self.feature_importances_=self.importance
        del self.x, self.y, self.importance, self.rng
        return self

    def _grow(self, idx, depth):
        labels=self.y[idx]; p=float(labels.mean()); node={"p":p,"n":len(idx)}
        if depth>=self.max_depth or len(idx)<2*self.min_leaf or p in (0.0,1.0): return node
        m=self.x.shape[1]; feats=np.arange(m)
        if self.max_features and self.max_features<m: feats=self.rng.choice(feats,self.max_features,replace=False)
        parent=2*p*(1-p); best_gain=0.0; best=None
        for j in feats:
            order=np.argsort(self.x[idx,j],kind="mergesort"); vals=self.x[idx[order],j]; yy=labels[order]
            if vals[0]==vals[-1]: continue
            cs=np.cumsum(yy); total=cs[-1]; n=len(yy)
            cuts=np.flatnonzero(vals[:-1]<vals[1:])+1
            cuts=cuts[(cuts>=self.min_leaf)&(n-cuts>=self.min_leaf)]
            if not len(cuts): continue
            lp=cs[cuts-1]/cuts; rp=(total-cs[cuts-1])/(n-cuts)
            gain=parent-(cuts/n*2*lp*(1-lp)+(n-cuts)/n*2*rp*(1-rp))
            k=int(np.argmax(gain))
            if gain[k]>best_gain:
                cut=cuts[k]; best_gain=float(gain[k]); best=(int(j),float((vals[cut-1]+vals[cut])/2),order,cut)
        if best is None:return node
        j,threshold,order,cut=best
        left=idx[order[:cut]];right=idx[order[cut:]]
        self.importance[j]+=best_gain*len(idx)
        node.update(feature=j,threshold=threshold,left=self._grow(left,depth+1),right=self._grow(right,depth+1))
        return node

    def predict_proba(self,x):
        x=np.asarray(x,dtype=float); out=np.empty(len(x))
        for i,row in enumerate(x):
            node=self.tree
            while "feature" in node: node=node["left"] if row[node["feature"]]<=node["threshold"] else node["right"]
            out[i]=node["p"]
        return np.column_stack([1-out,out])


class RandomForest:
    def __init__(self,n_trees=12,max_depth=7,min_leaf=40,seed=42):
        self.n_trees=n_trees;self.max_depth=max_depth;self.min_leaf=min_leaf;self.seed=seed;self.trees=[]
    def fit(self,x,y):
        x=np.asarray(x);y=np.asarray(y);rng=np.random.default_rng(self.seed);self.trees=[]
        for k in range(self.n_trees):
            ix=rng.integers(0,len(y),size=len(y))
            tree=CART(self.max_depth,self.min_leaf,max(1,int(np.sqrt(x.shape[1]))),self.seed+k)
            self.trees.append(tree.fit(x[ix],y[ix]))
        self.feature_importances_=np.mean([t.feature_importances_ for t in self.trees],axis=0)
        return self
    def predict_proba(self,x):return np.mean([t.predict_proba(x) for t in self.trees],axis=0)
