# PHISHY Project State

## Current State

Master execution through implementation and final verification is complete. Dataset analysis, Option C foundation, Units 1–5, model comparison, saved inference pipeline, FastAPI backend, React frontend, tests, and documentation are present. Five classifiers were trained and evaluated on one grouped holdout split. This result set is educational; live predictive validity is not established.

## Completed Work

- Preserved and read the original `data/phishing_dataset.csv`; no source data rows were edited.
- Finalized the exact ordered 17-feature Option C contract and scheme-stripped HTTP(S) project convention. Original submitted URL text remains displayed. `qty_space_url` is excluded.
- Disclosed that original raw URLs and upstream extractor implementation are unavailable; exact numerical parity is unverified and not claimed.
- Unit 1 computes actual dataset dimensions, class distribution, feature mean, sample/population variance, standard deviation, quantiles, distributions, empirical probabilities, and Bayes example.
- Unit 2 implements Bayesian logistic MAP with Gaussian prior and Laplace covariance approximation, regularized logistic regression, and linear SVM.
- Unit 3 implements covariance eigendecomposition PCA with explained variance and 2D visualization; PCA is not in the production predictor.
- Unit 4 implements first-order Markov transitions among observable URL categories, add-one probabilities, sequence probability, and within-sequence transition surprise. It is explicitly not a full HMM and has no corpus-trained anomaly baseline.
- Unit 5 implements custom binary Gini CART and a 12-tree bootstrap Random Forest.
- Used identical feature columns, training-only scaler, seed-42 grouped 80/20 holdout by all 111 predictors, and threshold 0.5 for model evaluation. Actual metrics/confusion matrices/ROC data saved in `reports/model_comparison.json`.
- Persisted model bundle is generated at `models/phishy_models.pkl` (ignored; reproduce using training command).
- FastAPI routes: health, predict, model-info, model-comparison, dataset-summary, unit1, unit3, unit4, unit5, course-mapping. No submitted URL is visited or resolved.
- React/Vite frontend includes URL Analyzer, Model Comparison, Unit 1–5, Course Mapping, and Methodology/About.
- Updated README and requested project/method documentation, including Viva notes, report outline, and measured comparison.

## Actual Holdout Metrics

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Bayesian Logistic Regression (Laplace) | 0.8207 | 0.8651 | 0.7826 | 0.8218 | 0.9122 |
| Logistic Regression | 0.8207 | 0.8651 | 0.7826 | 0.8218 | 0.9122 |
| Linear SVM | 0.7734 | 0.8798 | 0.6614 | 0.7551 | 0.8950 |
| CART Decision Tree | 0.8476 | 0.8473 | 0.8680 | 0.8575 | 0.9304 |
| Random Forest (12 trees) | 0.8375 | 0.8302 | 0.8704 | 0.8498 | 0.9225 |

Train rows: 46,916; test rows: 11,729. See `docs/MODEL_COMPARISON.md` for evaluation protocol and caveats. Do not treat these scores as live-URL accuracy.

## Verification

- `python -m unittest discover -s backend/tests -v`: **46 passed, 0 failed**.
- `npm run build`: Vite production build passed.
- Live API: every requested GET route returned 200; three representative URL predictions returned 200; invalid FTP URL returned 422.
- Browser E2E: submitted URL from React Analyzer to FastAPI, saw prediction/features/explanations; navigated model comparison and all Unit/course pages.
- `npm install` audit reported zero vulnerabilities.
- Dataset is treated as read-only.

## Known Limitations and Remaining Submission Work

- No raw historical URLs/source extractor means no exact feature parity validation; measured scores cannot validate live performance. State this in presentation and report.
- Evaluation is one grouped holdout; independent raw-URL and temporal validation are future work. SVM display scores are uncalibrated sigmoid-transformed margins.
- The per-URL Markov score is descriptive and not trained as a phishing anomaly score.
- Dataset license/collection metadata for the exact local copy remains unverified.
- Workspace has no Git repository, so no commit/diff audit was available.
- College submission should include limitations, actual run instructions, explain the Bayesian approximation and non-HMM Markov model, and capture the running interface/results.

## Run Commands (PowerShell)

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python backend/scripts/train.py
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
# second terminal
cd frontend
npm install
npm run dev
```

## Next State

No implementation task is outstanding for the defined master scope. Remaining work is external validation of upstream feature parity, legally reviewed dataset provenance, and repeated/independent model evaluation if required by the course.
