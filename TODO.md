# PHISHY TODO

## Phase 0 — Setup
- [x] Confirm source dataset exists.
- [x] Create persistent state, README, decisions, and minimum docs structure.
- [x] Add a `.gitignore` for environments, caches, generated files, and secrets.

## Phase 1 — Dataset Analysis
- [x] Inspect shape, schema, target, data types, missingness, duplicates, sentinels, and feature groups.
- [x] Document reproducible versus externally dependent features.
- [x] Record course mapping and proposed architecture.

## Phase 2 — Feature Extraction
- [x] Verify target encoding from upstream dataset documentation.
- [x] Investigate exact duplicates, class breakdown, and conflicting labels.
- [x] List all columns by feature group and assess raw-URL feature availability.
- [x] Implement deterministic URL validation and lexical feature extraction.
- [x] Define absent directory, filename, and query representations.
- [x] Document the 41-column mapping and limitations.
- [x] Determine that the local CSV has no raw URLs and exact 41-feature regeneration is impossible.
- [x] Document that exact upstream parity is accepted as unavailable.

## Phase 2.5 — Feature Parity and Validation
- [x] Audit all 41 feature formulas, order, output types, sentinels, and `urllib.parse` behavior.
- [x] Add deterministic tests for representative URL, path, query, email, domain/IP, and invalid-input cases.
- [x] Confirm extractor has no target or external/network-derived inputs.
- [x] Mark uncertain definitions and test scope explicitly as PARITY NOT VERIFIED.
- [x] Accept that exact upstream parity cannot be established from local files; no further source hunt requested.
- [x] Assess direct 41-column training risk and whether a derived feature matrix can be regenerated.
- [x] Recommend Option C: 17 whole-string columns, excluding `qty_space_url`.
- [x] Investigate observed distributions and relationships for the 17 candidate columns.
- [x] Finalize and document scheme-stripped project convention and representative comparisons.
- [x] Update extractor/tests to use the exact 17-feature training/live vector.
- [x] Record that no derived matrix is possible without raw URLs and preserve parity limitation.
- [x] Train the approved Option C models under the user-authorized master execution; results and source-parity limitations are documented.

## Phase 3 — Unit 1: Statistical Analysis
- [x] Compute dimensions, class counts/probabilities, means, population/sample variances, standard deviations, quantiles, and feature distributions from actual data.
- [x] Implement empirical Bayes calculation for `qty_dot_url >= 3`.
- [x] Display dataset summary, distributions, and Bayes example in frontend.

## Phase 4 — Unit 2: Linear Models / Classification
- [x] Implement Bayesian logistic MAP with Gaussian prior and Laplace posterior approximation.
- [x] Implement regularized Logistic Regression and Linear SVM benchmark.
- [x] Use identical features, split, training-only preprocessing, and evaluation metrics.

## Phase 5 — Unit 3: PCA
- [x] Implement centered covariance PCA with symmetric eigendecomposition.
- [x] Report explained/cumulative variance and display training-split 2D scatter.

## Phase 6 — Unit 4: Sequential Analysis
- [x] Implement observable URL token categories, transition counts/probabilities, sequence probability, and surprise score.
- [x] Document this as a Markov model, not a full HMM or trained anomaly classifier.

## Phase 7 — Unit 5: CART / Ensemble
- [x] Implement bounded binary Gini CART.
- [x] Implement and evaluate a 12-tree bootstrap Random Forest.

## Phase 8 — Model Comparison
- [x] Use duplicate-grouped 80/20 holdout, deterministic seed 42, train-only scaling, and threshold 0.5.
- [x] Produce actual metrics, confusion matrices, ROC curves/AUC, and persisted comparison report.

## Phase 9 — Prediction + Explanations
- [x] Build one 17-feature prediction service with saved scaler and Bayesian model.
- [x] Return class, phishing probability, low/high threshold-based risk, extracted features, explanations, and Markov score.
- [x] Use training-partition 95th percentile and fitted linear contributions for deterministic explanations.

## Phase 10 — FastAPI Backend
- [x] Implement health, predict, model-info, comparison, dataset, Units 1/3/4/5, and course mapping routes.
- [x] Validate request URLs and avoid visiting/resolving user URLs.

## Phase 11 — React Frontend
- [x] Implement responsive React + TypeScript + Vite UI for analyzer, comparison, Units 1–5, course mapping, and methodology/about.

## Phase 12 — Integration
- [x] Verify browser URL submission reaches backend and renders real prediction/features/explanation.
- [x] Verify navigation pages fetch/render their API data.

## Phase 13 — Testing
- [x] Preserve all 32 original feature-extractor regression methods.
- [x] Add preprocessing, model loading, prediction, explanations, Markov, evaluation, CORS, and API endpoint tests.
- [x] Run the complete unittest suite; no failures.
- [x] Build Vite production assets.

## Phase 14 — Documentation + Viva
- [x] Update README, dataset/features, course mapping, architecture, math models, model comparison, decisions, viva notes, and report outline.
- [x] Keep project state and this TODO synchronized with measured implementation.

## Phase 15 — Cleanup
- [x] Add reproducible backend/frontend dependencies and local run instructions.
- [x] Exclude environments, dependencies, generated model bundle, and build output through `.gitignore`.
- [x] Use no external fonts/API keys/secrets and no absolute source-code workspace paths.
- [x] Confirm npm dependency audit reported zero vulnerabilities.
- [x] Keep source CSV read-only.

## Phase 16 — Final Verification
- [x] Run all backend tests and frontend production build.
- [x] Start backend and verify every API route.
- [x] Test representative predictions and invalid-scheme rejection.
- [x] Exercise frontend-backend flow in browser and inspect Unit 1–5/course pages.
- [x] Verify serialized models load and return structured output.
- [x] Document actual metrics and remaining parity/live-validation limitations.
