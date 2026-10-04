# PHISHY — A Student Link-Safety Project

PHISHY is a student project that looks for patterns in the text of a web address. It can offer a warning, but **it cannot tell you that a link is safe**. A low score is not a safety certificate.

## Before you use the link checker

- PHISHY reads the address text only. It does not open or visit the website, check its current contents, inspect downloads, or follow redirects.
- A harmful page may imitate a real sign-in page, steal passwords or payment details, prompt you to download harmful software, ask for device permissions, track your visit, or send you to another page. Opening a link is not automatically dangerous, but take care with unexpected links.
- Do not enter passwords, one-time codes, or payment information on a page you reached through an unexpected message. Visit the service through its official app or a bookmark instead.
- Checking a link sends its text to this app's API. In the local setup below, the API runs on your computer. If you host the app online, the server operator can receive submitted link text. Avoid private reset links, invite links, or addresses containing secret codes.
- This is an experimental educational tool, not a security product. Its model may miss harmful links or flag harmless ones. Do not rely on it as your only protection.

The app explains these limits in plain language on its **If you open it**, **How this works**, and **About this project** pages.

## For project reviewers

PHISHY is an educational phishing-detection project with an actual statistical analysis, five comparative classifiers, PCA visualization, observable-token Markov analysis, CART/Random Forest results, a FastAPI service, and a React + TypeScript + Vite interface.

## Dataset and feature limitation

The source is `data/phishing_dataset.csv`: 58,645 records, 111 numeric predictors, and target `phishing` (`1` phishing, `0` legitimate). It is preserved unchanged. The final model input is the ordered 17-feature whole-URL representation in [docs/LIVE_FEATURES.md](docs/LIVE_FEATURES.md); `qty_space_url` is excluded because whitespace is rejected.

**Parity limitation:**

> The original dataset contains precomputed URL features but does not contain raw URLs or the upstream feature-extraction implementation. Therefore exact numerical parity with the original extractor cannot be verified. This project uses a reconstructed deterministic 17-feature representation consistently for training and live prediction.

The live feature convention accepts HTTP(S), strips the leading scheme and `://` for feature calculation, and leaves the submitted URL unchanged in the UI. Training uses the same-named precomputed 17 columns. The raw historical URLs are unavailable, so that source-to-live correspondence is not verified; measured holdout performance does not establish live prediction validity.

## Measured model results

One grouped 80/20 holdout run (seed 42) produced these actual results:

| Model | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Bayesian Logistic Regression (Laplace) | 0.8207 | 0.8651 | 0.7826 | 0.8218 | 0.9122 |
| Logistic Regression | 0.8207 | 0.8651 | 0.7826 | 0.8218 | 0.9122 |
| Linear SVM | 0.7734 | 0.8798 | 0.6614 | 0.7551 | 0.8950 |
| CART Decision Tree | 0.8476 | 0.8473 | 0.8680 | 0.8575 | 0.9304 |
| Random Forest (12 trees) | 0.8375 | 0.8302 | 0.8704 | 0.8498 | 0.9225 |

Full confusion matrices, ROC points, split metadata, and limitations are in [docs/MODEL_COMPARISON.md](docs/MODEL_COMPARISON.md) and `reports/model_comparison.json`. This is a single holdout experiment, not external or live validation.

## Run locally (PowerShell)

Python 3.10+ and Node.js 20+ are recommended.

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend/requirements.txt
python backend/scripts/train.py
python -m uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open <http://127.0.0.1:5173>. The frontend expects the API at `http://127.0.0.1:8000`; override with `frontend/.env` containing `VITE_API_URL=http://127.0.0.1:8000` if needed. The training command creates the ignored local artifact `models/phishy_models.pkl` and refreshes the actual-data JSON outputs under `reports/`.

## API

- `GET /health`
- `POST /predict` with `{"url":"https://example.com"}`
- `GET /model-info`
- `GET /model-comparison`
- `GET /dataset-summary`
- `GET /unit1`
- `GET /unit3`
- `GET /unit4?url=https%3A%2F%2Fexample.com`
- `GET /unit5`
- `GET /course-mapping`

The API validates and analyzes the submitted address text. It does not contact the address: no DNS lookup, website request, TLS connection, command execution, or reputation-service lookup is performed. When the app is hosted, its API server receives the submitted text; avoid sending private or secret-bearing links.

## Units and documentation

- Unit 1: actual descriptive statistics, feature distributions, empirical probabilities, and a Bayes-rule example.
- Unit 2: educational Bayesian logistic regression using a Laplace posterior approximation; regular logistic and linear SVM comparisons.
- Unit 3: covariance PCA with explained variance and 2D training-partition projection.
- Unit 4: first-order Markov model over observable URL character categories, **not a full HMM**.
- Unit 5: Gini-split CART and a 12-tree bootstrap Random Forest.

See [docs/COURSE_MAPPING.md](docs/COURSE_MAPPING.md), [docs/MATHEMATICAL_MODELS.md](docs/MATHEMATICAL_MODELS.md), [docs/VIVA_NOTES.md](docs/VIVA_NOTES.md), [docs/REPORT_OUTLINE.md](docs/REPORT_OUTLINE.md), [docs/PROJECT_ARCHITECTURE.md](docs/PROJECT_ARCHITECTURE.md), and [PROJECT_STATE.md](PROJECT_STATE.md).

## Tests and frontend build

```powershell
python -m unittest discover -s backend/tests -v
cd frontend
npm run build
```

The API uses FastAPI. Install backend requirements before testing/importing the API module. Training uses only NumPy and pandas beyond Python's standard library. The frontend uses locally bundled fonts/system fallbacks and makes requests only to the configured API.
