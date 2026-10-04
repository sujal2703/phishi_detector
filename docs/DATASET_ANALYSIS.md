# Dataset Analysis

## Source, target, and scope

- Local source: `data/phishing_dataset.csv` (never modified)
- Shape: **58,645 rows × 112 columns**; 111 integer predictor columns and one integer target `phishing`
- Missing values: **0**; exact duplicate excess rows: **1,240**
- Class counts: `phishing=0`: **27,998**; `phishing=1`: **30,647**
- **Target meaning: VERIFIED** as `0 = legitimate`, `1 = phishing`.

Evidence: the upstream [Grega Vrbančič Phishing-Dataset README](https://github.com/GregaVrbancic/Phishing-Dataset) documents its `dataset_small.csv` as 58,645 records with 27,998 legitimate rows labeled 0 and 30,647 phishing rows labeled 1. Those dimensions and both exact class counts match the local file. The README also documents 111 features plus the target and feature definitions. The cited research dataset is Vrbančič, Fister Jr., and Podgorelec, *Datasets for Phishing Websites Detection*, Data in Brief 33 (2020), DOI 10.1016/j.dib.2020.106438. The local file's byte identity with the upstream CSV has not been verified.

## Duplicate-row investigation

Computed using all 111 predictor columns and `phishing`:

- **1,240** rows are duplicate occurrences beyond the first for complete records (predictors and label match exactly).
- **1,653** rows belong to complete-record groups that occur more than once.
- Duplicate excess rows by label: **1,090 label-0**, **150 label-1**.
- Ignoring the target, there are **1,246** repeated feature-vector occurrences beyond first. Six feature-vector groups (13 rows total) have conflicting labels. Thus 1,240 repeats are complete-record duplicates and six additional repeats are identical predictors with contradictory labels.
- No records have been deleted or altered.

**Decision:** retain every row in the canonical source. For later evaluation, split by a stable group key over all 111 predictors so identical feature vectors stay wholly in one partition. Do not use a row-random split, which could place duplicate inputs on both sides and inflate scores. Preserve the six contradictory-label groups and report the resulting label ambiguity; assess their effect separately if needed. Do not deduplicate before splitting because doing so discards examples and still requires a policy for contradictory labels.

## Complete feature schema and categories

All columns are numeric in the CSV. The schema below is complete and follows source order, grouped by meaning. The source README is the available feature-definition reference.

| Category | Columns |
|---|---|
| Whole URL string/structural | `qty_dot_url`, `qty_hyphen_url`, `qty_underline_url`, `qty_slash_url`, `qty_questionmark_url`, `qty_equal_url`, `qty_at_url`, `qty_and_url`, `qty_exclamation_url`, `qty_space_url`, `qty_tilde_url`, `qty_comma_url`, `qty_plus_url`, `qty_asterisk_url`, `qty_hashtag_url`, `qty_dollar_url`, `qty_percent_url`, `qty_tld_url`, `length_url`, `email_in_url` |
| Domain/host | `qty_dot_domain`, `qty_hyphen_domain`, `qty_underline_domain`, `qty_slash_domain`, `qty_questionmark_domain`, `qty_equal_domain`, `qty_at_domain`, `qty_and_domain`, `qty_exclamation_domain`, `qty_space_domain`, `qty_tilde_domain`, `qty_comma_domain`, `qty_plus_domain`, `qty_asterisk_domain`, `qty_hashtag_domain`, `qty_dollar_domain`, `qty_percent_domain`, `qty_vowels_domain`, `domain_length`, `domain_in_ip`, `server_client_domain` |
| Directory/path | `qty_dot_directory`, `qty_hyphen_directory`, `qty_underline_directory`, `qty_slash_directory`, `qty_questionmark_directory`, `qty_equal_directory`, `qty_at_directory`, `qty_and_directory`, `qty_exclamation_directory`, `qty_space_directory`, `qty_tilde_directory`, `qty_comma_directory`, `qty_plus_directory`, `qty_asterisk_directory`, `qty_hashtag_directory`, `qty_dollar_directory`, `qty_percent_directory`, `directory_length` |
| File/path leaf | `qty_dot_file`, `qty_hyphen_file`, `qty_underline_file`, `qty_slash_file`, `qty_questionmark_file`, `qty_equal_file`, `qty_at_file`, `qty_and_file`, `qty_exclamation_file`, `qty_space_file`, `qty_tilde_file`, `qty_comma_file`, `qty_plus_file`, `qty_asterisk_file`, `qty_hashtag_file`, `qty_dollar_file`, `qty_percent_file`, `file_length` |
| Query/parameters | `qty_dot_params`, `qty_hyphen_params`, `qty_underline_params`, `qty_slash_params`, `qty_questionmark_params`, `qty_equal_params`, `qty_at_params`, `qty_and_params`, `qty_exclamation_params`, `qty_space_params`, `qty_tilde_params`, `qty_comma_params`, `qty_plus_params`, `qty_asterisk_params`, `qty_hashtag_params`, `qty_dollar_params`, `qty_percent_params`, `params_length`, `tld_present_params`, `qty_params` |
| Runtime/network/domain infrastructure | `time_response`, `domain_spf`, `asn_ip`, `qty_ip_resolved`, `qty_nameservers`, `qty_mx_servers`, `ttl_hostname`, `qty_redirects` |
| WHOIS/domain age | `time_domain_activation`, `time_domain_expiration` |
| TLS/security | `tls_ssl_certificate` |
| Search/index/external | `url_google_index`, `domain_google_index`, `url_shortened` |
| Target label | `phishing` |

The categories sum to 111 predictors plus one target. `time_response` requires runtime/network observation. Although placed after URL lexical columns in the CSV, it is not a raw-string-only feature.

## Which features are URL-only?

Whole-URL length and punctuation counts, hostname length/character counts/vowels, host-as-IP, `server_client_domain`, directory/file/query lengths and counts, parameter count, and an email-like URL marker are computable from text alone in principle. Exact parity depends on matching source parsing rules. `qty_tld_url`, `tld_present_params`, `email_in_url`, and path segmentation need precise rules; the upstream README gives only brief names/descriptions, so those require documented local conventions and compatibility caveats.

The following require external or runtime observations and will not be synthesized: `time_response`, `domain_spf`, `asn_ip`, `time_domain_activation`, `time_domain_expiration`, `qty_ip_resolved`, `qty_nameservers`, `qty_mx_servers`, `ttl_hostname`, `tls_ssl_certificate`, `qty_redirects`, `url_google_index`, and `domain_google_index`. `url_shortened` usually requires a shortening-service list; excluded from the live subset until a fixed list policy is justified.

## Data quality and sentinel observations

- 13 domain character-count features are constant zero: `qty_slash_domain`, `qty_questionmark_domain`, `qty_equal_domain`, `qty_and_domain`, `qty_exclamation_domain`, `qty_space_domain`, `qty_tilde_domain`, `qty_comma_domain`, `qty_plus_domain`, `qty_asterisk_domain`, `qty_hashtag_domain`, `qty_dollar_domain`, `qty_percent_domain`.
- Directory and file columns use `-1` in 17,507 rows; parameter columns use `-1` in 51,223 rows. These values align with absent URL components and must not be changed to zero without an explicit policy.
- Other external features also contain `-1`; their individual counts vary. There are no nulls, but `-1` represents unavailable/not-applicable states in the stored feature data.
- Selected descriptive values: `length_url` mean 44.96, median 29, range 4–4,165; `domain_length` mean 18.07, median 17, range 4–231; `qty_dot_url` mean 2.28, range 1–24.

## Pipeline compatibility limitation

The local CSV has engineered columns but no raw URL column. Therefore we cannot rerun one raw-URL parser over historical training examples or prove exact extractor parity against their original URLs. The live extractor and training selector use the same final 17-feature names/order, and live inference reuses the saved training-only scaler. Training selects precomputed values; the original URLs are absent, so numerical extraction equivalence remains unverified.

## Training-readiness decision (historical 41-feature assessment)

**PARITY NOT VERIFIED.** The local CSV contains engineered columns but no raw URL column. Existing aggregates are lossy and cannot recreate the source strings or consistently reproduce all extracted values. The direct 41-feature live pipeline was therefore rejected due to source parsing ambiguity. The final Option C scheme investigation and project convention are recorded below. No synthetic URL reconstruction or derived matrix is permitted.


## Final Option C scheme convention (2026-10-04)

Final training/live inputs are the 17 whole-URL fields documented in `docs/LIVE_FEATURES.md`; `qty_space_url` is omitted because live validation rejects whitespace. Dataset evidence favors stripping an HTTP(S) scheme before counting: `qty_slash_url` has minimum 0, with 17,507 zero values, and `length_url` has minimum 4. Any complete absolute `http://` or `https://` input contributes two slashes and at least seven characters. This argues against complete-absolute-string counting. It cannot distinguish a source-side scheme strip from originally scheme-less strings, and it is not proof of source parity. The project convention is therefore explicit: accept HTTP(S), remove the leading scheme plus `://` only from the feature representation, and retain the original URL unchanged for display.

The observed distributions and strongest correlations are recorded in `docs/LIVE_FEATURES.md`: punctuation counts are highly sparse; equal-sign and ampersand counts correlate at r=0.892, and length relates to equal count (r=0.645), ampersand count (r=0.580), and slash count (r=0.526). These are descriptive, not source-code evidence.

The local dataset contains no raw URLs. Therefore the 17 source columns cannot be regenerated from raw inputs using the project extractor, and a derived training matrix consistent with the live transform is not possible. No URLs were fabricated or reconstructed from lossy aggregates. Option C uses the available same-named precomputed 17 columns as a controlled training representation with the parity limitation disclosed. The actual single grouped holdout metrics are in `docs/MODEL_COMPARISON.md`; these are dataset-column results, not verified live-URL results.


## Execution note

The original dataset contains precomputed URL features but does not contain raw URLs or the upstream feature-extraction implementation. Therefore exact numerical parity with the original extractor cannot be verified. This project uses a reconstructed deterministic 17-feature representation consistently for training and live prediction. “Consistently” refers to the selected names/order and explicit project convention; it cannot imply value-by-value parity with the unavailable historical extractor.
