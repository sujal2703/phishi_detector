"""Leakage-safe deterministic preprocessing for the 17 project features."""
from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd

from .feature_extractor import MODEL_FEATURES


@dataclass
class Standardizer:
    mean: np.ndarray
    scale: np.ndarray

    @classmethod
    def fit(cls, x: np.ndarray) -> "Standardizer":
        mean = np.mean(x, axis=0)
        scale = np.std(x, axis=0)
        scale[scale == 0] = 1.0
        return cls(mean, scale)

    def transform(self, x: np.ndarray) -> np.ndarray:
        return (np.asarray(x, dtype=float) - self.mean) / self.scale

    def to_dict(self) -> dict:
        return {"mean": self.mean.tolist(), "scale": self.scale.tolist(), "features": list(MODEL_FEATURES)}


def matrix_from_frame(frame: pd.DataFrame) -> np.ndarray:
    missing = [name for name in MODEL_FEATURES if name not in frame.columns]
    if missing:
        raise ValueError(f"Dataset lacks required fields: {missing}")
    return frame.loc[:, list(MODEL_FEATURES)].to_numpy(dtype=float)


def grouped_split(frame: pd.DataFrame, test_fraction: float = 0.2, seed: int = 42):
    """Deterministically hold out complete predictor-vector groups."""
    predictors = [c for c in frame.columns if c != "phishing"]
    group_hashes = pd.util.hash_pandas_object(frame[predictors], index=False).to_numpy(dtype="uint64")
    unique = np.unique(group_hashes)
    rng = np.random.default_rng(seed)
    rng.shuffle(unique)
    target_test_rows = int(round(len(frame) * test_fraction))
    held, count = set(), 0
    sizes = pd.Series(group_hashes).value_counts()
    for key in unique:
        if count >= target_test_rows:
            break
        held.add(int(key))
        count += int(sizes.loc[key])
    is_test = np.isin(group_hashes, np.fromiter(held, dtype="uint64"))
    return np.flatnonzero(~is_test), np.flatnonzero(is_test)
