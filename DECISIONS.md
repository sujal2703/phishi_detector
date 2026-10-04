# PHISHY Decisions

## 2026-10-04 — First-session scope
- **Decision:** Complete only setup and dataset analysis.
- **Reason:** The project brief explicitly limits the first session to Phase 0 and Phase 1.
- **Alternatives:** Begin feature extraction or model training.
- **Rejected:** Those steps exceed scope and depend on undocumented data semantics.

## 2026-10-04 — Target label verification
- **Decision:** `phishing=0` means legitimate and `phishing=1` means phishing; status is VERIFIED.
- **Evidence:** The upstream Grega Vrbančič dataset README describes the `dataset_small.csv` variant with 58,645 rows, 27,998 legitimate labeled 0, and 30,647 phishing labeled 1. The local dataset has the same row count and exact class counts.
- **Caveat:** Local file byte identity with the upstream file was not checked; retain the source citation in dataset documentation.

## 2026-10-04 — Duplicate policy
- **Finding:** 1,240 extra complete-record copies (1,090 class 0, 150 class 1); 1,653 rows are in repeated complete-record groups. Across predictors alone, 1,246 extra rows share a feature vector; six feature groups / 13 rows have conflicting labels.
- **Decision:** Keep the source untouched and retain rows. In later evaluation, group split by all predictor values so repeated feature vectors cannot cross train/test boundaries; report the contradictory-label groups.
- **Reason:** Row-random splitting can leak identical feature vectors and inflate estimates. Deleting duplicates would discard observations and would not resolve contradictory labels without an arbitrary policy.

## 2026-10-04 — Live feature scope
- **Decision:** The initial model input uses 41 existing, URL-only dataset columns as ordered in `backend/app/ml/feature_extractor.py`; no new feature names are created. Exclude `qty_space_url` because whitespace is rejected, `qty_tld_url` because exact public-suffix semantics are undefined, constant domain punctuation fields, and unavailable external/runtime fields.
- **Reason:** These selected features can be computed deterministically without visiting the URL and map to source column names.
- **Caveat:** Local CSV has no raw URL column. Same-name precomputed source columns can be selected through the shared ordered selector, but extraction parity is unverified until original URLs/source extractor rules are obtained.
- **Absent components:** Directory/file/query fields use observed `-1` when absent; present-but-empty components use 0 length/count. Explicit empty query (`?`) is treated as present with zero values.
- **Input policy:** Require absolute HTTP(S) URL; reject missing scheme rather than rewriting it, because rewriting changes full-string counts. Reject whitespace and URLs longer than 8,192 characters.

## 2026-10-04 — Evaluation and scaling
- **Decision:** Later use train-only scaling parameters and apply them unchanged to validation/test/live vectors. Group identical predictor vectors in one data split.
- **Reason:** Avoid preprocessing leakage and duplicate-feature leakage.
- **Caveat:** Do not fit a model until source-feature/extractor parity is resolved or explicitly limited to a documented experimental scope.

## 2026-10-04 — Phase 2.5 parity audit
- **Decision:** Keep the current 41 local feature formulas unchanged, but mark upstream parity **PARITY NOT VERIFIED** for all 41 because the available dataset documentation has no extractor implementation or raw URL fixtures.
- **Specific uncertainties:** URL canonicalization/length, hostname normalization and IDNs, path directory/file split and trailing slash treatment, query parameter counting, sentinel generation, and the exact `email_in_url` rule. The final non-trailing path component is assigned to `file` only as a provisional local rule; the upstream source does not establish that assumption.
- **Decision:** Do not train a model from these features yet. Same names and order do not prove value compatibility.
- **Regression suite:** Added 31 deterministic unittest methods; the final run passed all 31. The suite verifies the documented local contract, not upstream parity.
- **Validation adjustment:** Reject an explicitly empty port (`host:`) and ASCII control characters in addition to invalid numeric ports and malformed escapes. No feature formula changed.

## 2026-10-04 — Controlled training-readiness decision (at decision time; later superseded by user-authorized master execution)
- **Accepted limitation:** The 41 selected fields are based on published feature definitions; the upstream extraction implementation and original raw URLs are unavailable. The local extractor is reconstructed and deterministic. Exact numerical parity cannot be proven, and PHISHY will not claim exact upstream extractor reproduction. Do not spend more time seeking parity outside information already present locally.
- **Assessment of direct 41-column training:** Reject as a live deployment representation. Source component semantics are underspecified, and raw scheme handling likely differs. In the local CSV, `qty_slash_url` minimum is 0 and `length_url` minimum is 4; the current extractor counts an absolute scheme, adding two slashes and seven/eight length characters. This could materially shift live inputs.
- **Reconstruction assessment:** The CSV has no raw URLs; aggregate features are lossy. Selected columns can be copied, but cannot be regenerated consistently by the live extractor. Do not create a copied file and describe it as a derived project feature matrix.
- **Recommended candidate (Option C):** 17 whole-string fields: `length_url` plus the 16 selected `qty_*_url` punctuation counts, excluding `qty_space_url` because whitespace inputs are rejected. Before any training, define an explicit scheme-neutral project representation by stripping `http://` or `https://` before these counts. The source minima support this hypothesis but do not verify it. This reduces component-split mismatch; predictive utility and remaining source parity are unknown.
- **Current status:** No model training and no derived matrix. Option C is a candidate decision, not yet a training authorization; implement/test/accept its normalization before training.

## 2026-10-04 — Course mapping
- **Decision:** Retain Unit 1 statistics/Bayes, Unit 2 Bayesian logistic regression, Unit 3 PCA, Unit 4 Markov/sequential analysis, Unit 5 CART.
- **Reason:** Coherent for one phishing problem and aligned with course reviews.
- **Alternatives:** Mandatory SVM, full HMM algorithms, and ensembles.
- **Rejected:** Unrequired complexity at this stage.


## 2026-10-04 — Final Option C scheme convention and training feature set (decision-time status; later master execution authorized training)
- **Decision:** Finalize the 17 whole-URL fields listed in `backend/app/ml/feature_extractor.py`; exclude `qty_space_url` because the live validator rejects whitespace.
- **Project convention:** Accept absolute HTTP(S). Remove the leading scheme and `://` before computing whole-URL length and punctuation features. Preserve the submitted URL for display; only model feature calculations use the stripped representation.
- **Evidence:** In the local 58,645 rows, `qty_slash_url` minimum is 0 and 17,507 rows have zero slashes; `length_url` minimum is 4. Complete HTTP(S) URLs always include two scheme slashes and seven/eight scheme characters. This supports stripping relative to complete-URL counting, but cannot distinguish stripping from scheme-less source inputs and does not prove upstream parity.
- **Comparison:** `https://example.com/login?user=test` is 35 characters/3 slashes complete and 27/1 after stripping; the HTTP version is 34/3 complete and 27/1 stripped.
- **Parity limitation:** Historical names use published definitions; the source extractor is unavailable. The local implementation is reconstructed and deterministic. Exact parity cannot be proven and will not be claimed. The CSV has no URLs; no derived matrix can be regenerated consistently.
- **Training status:** The 17-field representation is ready for a later controlled training step using source columns of the same names, with material parity limitation disclosed. This decision does not authorize training in this phase; no models were trained.


## 2026-10-04 — Master execution and completed implementation
- **Decision:** Proceed autonomously through the remaining units using the finalized Option C inputs; retain the reconstruction limitation without reopening feature design.
- **Training/evaluation:** Train five classifiers on the 17 same-named precomputed source columns using a seed-42 grouped 80/20 holdout keyed by all 111 predictor columns; fit standardization only on train. Actual metrics and confusion matrices are in `reports/model_comparison.json`. These do not verify live predictive performance.
- **Models:** Educational Bayesian logistic MAP with Gaussian prior and Laplace covariance approximation is primary; regular logistic and linear SVM are benchmarks; custom Gini CART and 12-tree bootstrap Random Forest are implemented. SVM sigmoid margin is explicitly uncalibrated.
- **Units:** Actual-data descriptive/Bayes analysis; covariance PCA for visualization only; observable-category first-order Markov score, not a full HMM; CART/forest comparison.
- **Serving:** FastAPI validates inputs and uses saved scaler/model, deterministic explanations, and descriptive Markov output without visiting URLs. React/Vite pages show analysis and measured metrics. Risk threshold is 0.5 (low below, high at/above).
- **Verification:** 43 unittest tests pass, API routes respond, end-to-end browser prediction and all course pages render, Vite production build passes. Source CSV is read-only.
- **Caveat:** Training uses source precomputed fields because original URLs are unavailable. Exact upstream feature parity and live predictive validity remain unverified.
