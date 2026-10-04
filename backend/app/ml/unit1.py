"""Descriptive statistics and empirical Bayes demonstrations."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = ROOT / "data" / "phishing_dataset.csv"
FEATURES = (
    "length_url", "qty_dot_url", "qty_hyphen_url", "qty_underline_url",
    "qty_slash_url", "qty_questionmark_url", "qty_equal_url", "qty_at_url",
    "qty_and_url", "qty_exclamation_url", "qty_tilde_url", "qty_comma_url",
    "qty_plus_url", "qty_asterisk_url", "qty_hashtag_url", "qty_dollar_url",
    "qty_percent_url",
)


def load_data(path: Path = DATA_PATH) -> pd.DataFrame:
    return pd.read_csv(path)


def analyze(df: pd.DataFrame | None = None) -> dict[str, Any]:
    data = df if df is not None else load_data()
    y = data["phishing"].to_numpy(dtype=int)
    n = len(y)
    positives = int(y.sum())
    p_phish = positives / n
    p_legit = 1.0 - p_phish
    # Illustrative Bayes calculation for one transparent event: URL has >=3 dots.
    event = data["qty_dot_url"].to_numpy() >= 3
    p_e = float(event.mean())
    p_e_given_phish = float(event[y == 1].mean())
    p_e_given_legit = float(event[y == 0].mean())
    posterior = p_e_given_phish * p_phish / p_e if p_e else 0.0
    summaries = {}
    for name in FEATURES:
        values = data[name].to_numpy(dtype=float)
        summaries[name] = {
            "mean": float(values.mean()),
            "variance_population": float(values.var(ddof=0)),
            "variance_sample": float(values.var(ddof=1)),
            "std_population": float(values.std(ddof=0)),
            "median": float(np.median(values)),
            "min": float(values.min()),
            "max": float(values.max()),
            "quantiles": {str(q): float(np.quantile(values, q)) for q in (0.25, 0.5, 0.75, 0.95)},
        }
    hist = {}
    for name in ("length_url", "qty_dot_url", "qty_slash_url", "qty_percent_url"):
        hist[name] = {str(int(k)): int(v) for k, v in data[name].value_counts().sort_index().items()}
    return {
        "rows": n, "columns": len(data.columns), "predictor_count": len(data.columns) - 1,
        "class_distribution": {"legitimate": int((y == 0).sum()), "phishing": positives},
        "class_probability": {"legitimate": p_legit, "phishing": p_phish},
        "features": summaries,
        "selected_histograms": hist,
        "bayes_example": {
            "event": "qty_dot_url >= 3", "P(phishing)": p_phish,
            "P(event|phishing)": p_e_given_phish,
            "P(event|legitimate)": p_e_given_legit,
            "P(event)": p_e, "P(phishing|event)": posterior,
            "formula": "P(F|E)=P(E|F)P(F)/P(E)",
        },
    }
