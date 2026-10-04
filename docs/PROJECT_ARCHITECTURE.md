# Project Architecture — Implemented

```text
React + TypeScript + Vite (frontend/)
        | HTTP JSON (localhost only in development)
FastAPI (backend/app/main.py)
        |-- predictor: validation -> shared 17 features -> stored scaler -> Bayesian logistic
        |-- deterministic explanations and per-URL Markov score
        |-- Unit 1 statistics / Unit 3 PCA / Unit 5 importance endpoints
        |-- saved comparison and dataset reports
NumPy/pandas training script (backend/scripts/train.py)
        |-- immutable data/phishing_dataset.csv
        |-- ignored model artifact models/phishy_models.pkl
        |-- reports/*.json
```

## Main components

- `backend/app/ml/feature_extractor.py`: URL validation, scheme-stripped project text fields, and canonical 17-feature model ordering. It also computes prior diagnostic fields that are not model inputs.
- `backend/app/ml/preprocessing.py`: selects the ordered source fields, groups duplicate predictor vectors, and fits a reusable training-only standardizer.
- `backend/app/ml/models.py`: Bayesian logistic/Laplace approximation, ordinary regularized logistic, linear SVM, Gini CART, and bootstrap Random Forest.
- `backend/app/ml/evaluation.py`: accuracy, precision, recall, F1, confusion matrix, tie-aware ROC-AUC, and ROC points.
- `backend/app/ml/unit1.py`, `unit3.py`, `unit4.py`: empirical analysis, covariance PCA, and observable-category Markov model.
- `backend/app/services/`: prediction orchestration and deterministic explanation construction.
- `backend/scripts/train.py`: reproducible grouped holdout, training, reports, and model serialization.
- `frontend/src/App.tsx`: URL analyzer and Unit 1–5, comparison, course mapping, and methodology pages.

## Data flow and safeguards

The input URL is validated as absolute HTTP(S), with whitespace/control characters, malformed percent escapes, invalid host/port, and lengths over 8,192 rejected. The original URL remains in the input/display field. Only `http(s)://` is stripped for model whole-URL values. Neither the frontend nor backend opens a submitted URL, resolves its host, invokes a shell, or makes external lookups. JSON reports are local.

The CSV contains precomputed same-named feature columns but no source URLs. Training selects those columns and uses training-partition scaling; live inference extracts them from submitted URLs and reuses the same scaler and order. The inferred scheme convention is documented but cannot be verified against historical URL strings or original source code. Consequently source holdout scores are not proof of live validity.

The classifier threshold is 0.5. Risk is `low` below that boundary and `high` at/above it. There is no separate medium band. Bayesian model parameter uncertainty is available as an approximate covariance-derived score. SVM sigmoid scores are uncalibrated and SVM is benchmark-only.

## Run sequence

Install `backend/requirements.txt`, run `python backend/scripts/train.py`, then launch `python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000`. In another shell, `cd frontend`, `npm install`, `npm run dev`. The API uses CORS for local Vite origins only.
