"""PCA via centered covariance and symmetric eigen-decomposition."""
from __future__ import annotations
import numpy as np

class PCA:
    def __init__(self,n_components=2):self.n_components=n_components
    def fit(self,x):
        x=np.asarray(x,dtype=float);self.mean_=x.mean(axis=0);z=x-self.mean_
        cov=z.T@z/(len(z)-1);values,vectors=np.linalg.eigh(cov)
        order=np.argsort(values)[::-1];self.eigenvalues_=values[order];self.components_=vectors[:,order[:self.n_components]].T
        self.explained_variance_ratio_=self.eigenvalues_/self.eigenvalues_.sum()
        return self
    def transform(self,x):return (np.asarray(x,dtype=float)-self.mean_)@self.components_.T
    def to_dict(self):return {"n_components":int(self.n_components),"eigenvalues":self.eigenvalues_.tolist(),"explained_variance_ratio":self.explained_variance_ratio_.tolist(),"cumulative_explained_variance":np.cumsum(self.explained_variance_ratio_).tolist(),"components":self.components_.tolist(),"mean":self.mean_.tolist()}
