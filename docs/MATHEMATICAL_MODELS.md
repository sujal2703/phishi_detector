# Mathematical Models — Implemented

## Unit 1: moments, probability, Bayes rule

For values `x₁,…,xₙ`, mean is `μ̂ = Σxᵢ/n`; population variance is `Σ(xᵢ−μ̂)²/n`, sample variance is `Σ(xᵢ−μ̂)²/(n−1)`, and standard deviation is the square root of variance. Empirical probability is event frequency divided by the relevant count. The displayed Bayes example uses `F=phishing` and `E=(qty_dot_url >= 3)`:

`P(F|E) = P(E|F) P(F) / P(E)`

Each probability is calculated from the actual dataset; this one-feature illustration does not assume conditional independence or replace the classifier.

## Unit 2: logistic likelihood and Bayesian approximation

For augmented row `dᵢ=[1,xᵢ]`, `pᵢ=σ(dᵢᵀw)` and `σ(z)=1/(1+exp(−z))`. Bernoulli log-likelihood is `ℓ(w)=Σ[yᵢ log pᵢ +(1−yᵢ)log(1−pᵢ)]`. The Bayesian model uses a zero-mean Gaussian prior on coefficients with standard deviation `τ=2` and a weak intercept prior. It estimates the maximum a posteriori value by Newton updates on negative log posterior. With `Wᵢᵢ=pᵢ(1−pᵢ)`, negative log-posterior Hessian is `H=DᵀWD+Λ`, where `Λ` is prior precision. The Laplace approximation is `w|data ≈ Normal(w_MAP,H⁻¹)`. Prediction uses the sigmoid at the MAP; reported uncertainty is a covariance-derived parameter uncertainty proxy, not a calibrated probability interval.

Ordinary logistic regression uses the same sigmoid likelihood with L2 penalization but reports only a point estimate. The Linear SVM minimizes `λ||w||²/2 + mean(max(0,1−y(wᵀx+b)))` by full-batch subgradient descent (`λ=0.03`, 18 epochs). Its displayed sigmoid-transformed margin is not calibrated; ROC-AUC uses its native decision score.

All classifiers use a standardizer `zⱼ=(xⱼ−μⱼ)/sⱼ` fitted on training rows only. Threshold is `0.5`. The confusion matrix uses rows=actual `[legitimate, phishing]`, columns=predicted `[legitimate, phishing]`. Precision=`TP/(TP+FP)`, recall=`TP/(TP+FN)`, F1=`2PR/(P+R)`, accuracy=`(TP+TN)/N`.

## Split protocol

Group key is a stable hash over all 111 predictor columns. A deterministic seed-42 shuffle of complete groups assigns approximately 20% of rows to test; the actual run has 46,916 training and 11,729 test rows. The target is excluded from grouping. No group is split across partitions. This is one holdout experiment; it does not use cross-validation or external-time validation.

## Unit 3: PCA

After training-only standardization, PCA centers the selected matrix again, computes sample covariance `C=ZᵀZ/(n−1)`, and uses the symmetric eigendecomposition `Cvⱼ=λⱼvⱼ`. Components are sorted by descending eigenvalue. Explained variance ratio is `λⱼ/Σₖλₖ`; cumulative variance is its running sum. The 2D scatter uses a deterministic sample from training rows. PCA is unsupervised and is not used in prediction.

## Unit 4: observable-category Markov sequence

Characters map deterministically into `ALPHA`, `DIGIT`, `DOT`, `SLASH`, `QUERY`, `SPECIAL`, `OTHER`. For adjacent states, transition count is `Nᵢⱼ`; add-one-smoothed transition probability is `(Nᵢⱼ+1)/(Nᵢ·+K)`, with K equal to seven category values. Initial-state probability uses add-one smoothing over the seven categories; sequence probability multiplies that initial probability by all transition probabilities. Mean transition surprise is `−Σlog p(sₜ|sₜ₋₁)/(T−1)`. Counts/probabilities are estimated within the input sequence, not from a learned corpus baseline. **Unit 4 is demonstrated using a Markov sequential model over observable URL-token categories rather than a full Hidden Markov Model.** This score is descriptive and does not influence the primary classifier probability.

## Unit 5: CART and Random Forest

Binary Gini impurity is `G=1−Σₖpₖ²=2p(1−p)`. At each node, CART scans candidate feature thresholds and chooses the split maximizing parent impurity minus sample-weighted child impurity. It stops at depth 7, minimum leaf size 40, pure nodes, or no positive gain. Leaf phishing probability is the empirical positive fraction. Feature importance accumulates sample-weighted Gini reduction and is normalized. Random Forest draws 12 bootstrap samples, builds the same bounded CART with `sqrt(17)` sampled features per split, and averages probabilities. These are custom educational implementations, not scikit-learn estimators.
