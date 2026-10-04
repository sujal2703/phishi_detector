# PHISHY Viva Notes

## Problem and data
- Binary task: estimate whether a phishing dataset record is labeled phishing (1) or legitimate (0).
- Local source has 58,645 rows, 111 numeric predictors plus the `phishing` target.
- The 17 selected URL-text features are existing whole-URL fields.
- The dataset has no original raw URLs or upstream extractor code. Exact parity is not proven; a reconstructed deterministic extractor is used for live URLs.

## Unit 1: statistics and Bayes
- Population variance uses denominator N; sample variance uses N-1. The UI shows both.
- Feature summaries are computed from actual CSV values.
- Example event: at least three URL dots. Bayes rule combines the observed class prior and class-conditional event frequencies. It is a one-event demonstration, not the classifier.

## Unit 2: classification
- Logistic model: `p(y=1|x)=sigmoid(wᵀx+b)`.
- Bayesian logistic uses a zero-centered Gaussian prior on coefficients and MAP estimation, then a Laplace Gaussian approximation around the MAP using the inverse Hessian. Reported parameter uncertainty is posterior standard-deviation proxy, not a calibrated prediction interval.
- Ordinary logistic is a separate L2-regularized point-estimate benchmark. Linear SVM is a hinge-loss margin model; its displayed sigmoid score is uncalibrated.
- All models share a grouped holdout split and a training-only standardizer.

## Unit 3: PCA
- Standardized training features are centered, covariance is formed, and `numpy.linalg.eigh` supplies eigenvalues and eigenvectors.
- Explained variance ratio is `λᵢ / Σⱼ λⱼ`; PCA is unsupervised and is not the production classifier.

## Unit 4: Markov sequence
- URL characters map to observable categories. Add-one-smoothed first-order transition probabilities produce a sequence probability and average transition surprise.
- This per-URL score has no corpus-trained anomaly baseline and is not used as a standalone detector.
- Unit 4 is demonstrated using a Markov sequential model over observable URL-token categories rather than a full Hidden Markov Model.

## Unit 5: trees
- CART greedily chooses a one-feature threshold that reduces binary Gini impurity. Random Forest averages bootstrap CART probabilities with random feature subsets.

## Evaluation and limitations
- Metrics are a single 80/20 grouped holdout, seed 42, threshold 0.5. Duplicate predictor vectors are grouped by all 111 source predictors.
- Source columns are precomputed and cannot be re-run through the live extractor. Metrics are dataset-column results, not verified live performance.
- Do not interpret the reported probabilities as calibrated on real-world traffic. No domain lookups or URL visits are made.
