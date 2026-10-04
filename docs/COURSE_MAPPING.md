# Course Mapping — Implemented

| Unit | Concept / mathematical component | Code | Project usage | UI demonstration |
|---|---|---|---|---|
| 1 — Introduction to Probability | Actual-data means, population/sample variance and standard deviation, empirical probability, Bayes rule | `backend/app/ml/unit1.py` | Describe target and 17 selected feature distributions; posterior for event `qty_dot_url >= 3` | Statistics page: counts, distributions, moments, Bayes example |
| 2 — Linear Models for Regression | Logistic sigmoid and likelihood; Bayesian logistic MAP plus Laplace posterior; logistic and linear SVM comparisons | `backend/app/ml/models.py` | Primary phishing probability is Bayesian logistic; three linear classifier comparisons | Classification methodology and metrics |
| 3 — Mixture Models and EM | PCA is used as an educational unsupervised projection, not EM or a classifier | `backend/app/ml/unit3.py` | Centered covariance eigen-decomposition and training-data projection | Explained variance and 2D scatterplot |
| 4 — Hidden Markov Models | First-order Markov transitions among observable token categories | `backend/app/ml/unit4.py` | Within-URL transition counts, smoothed likelihood and mean surprise | URL Analyzer sequential score and Unit 4 transition table |
| 5 — Combining Models | CART tree splits and bootstrap Random Forest | `backend/app/ml/models.py` | Tree/forest benchmarking and impurity feature importance | Metrics, confusion matrices, feature-importance charts |

## Accuracy of course claims

Unit 3 is explicitly a PCA demonstration; the course title's EM/mixture-model algorithms are not implemented. Unit 4 does not infer hidden states or emissions. **Unit 4 is demonstrated using a Markov sequential model over observable URL-token categories rather than a full Hidden Markov Model.** The code has no class-conditional Markov corpus, so its score is descriptive for the submitted sequence and not a learned phishing anomaly probability. Unit 5 ensemble learning is represented by a 12-tree bootstrap Random Forest; it is compared with CART rather than presented as a guaranteed improvement.

Further details and the machine-readable mapping are in `reports/course_mapping.json`.
