# Live URL Feature Contract — Final Option C

## Final training/live representation (2026-10-04)

The finalized `MODEL_FEATURES` input is the ordered 17-field subset listed below. `extract_url_features` computes this subset under the same scheme-stripped project convention used to describe the selected training columns. It also returns 24 additional reconstructed diagnostic fields for prior parser analysis; these are not model inputs. `select_model_vector` selects and orders only the 17 final fields.

**PROJECT CONVENTION**
- Accept absolute `http://` and `https://` input.
- Remove the leading scheme and following `://` delimiter before calculating project whole-URL features.
- Calculate `length_url` and the 16 punctuation counts on the remaining URL representation, including authority, path, query, and fragment text.
- Preserve the submitted URL unchanged for display; only the feature calculation uses the normalized representation.
- Whitespace remains rejected, so `qty_space_url` is excluded.

The 17 ordered fields are: `length_url`, `qty_dot_url`, `qty_hyphen_url`, `qty_underline_url`, `qty_slash_url`, `qty_questionmark_url`, `qty_equal_url`, `qty_at_url`, `qty_and_url`, `qty_exclamation_url`, `qty_tilde_url`, `qty_comma_url`, `qty_plus_url`, `qty_asterisk_url`, `qty_hashtag_url`, `qty_dollar_url`, `qty_percent_url`.

## Security scope and known blind spots

These 17 inputs are length and punctuation counts. They do not represent the actual hostname words, compare a hostname with a brand name, check domain ownership or age, consult a threat-intelligence/reputation service, inspect page content, or follow redirects. Consequently, a lookalike such as `paypa1.com` can receive a low warning score because its length and punctuation look ordinary. A low model score must never be presented or understood as a safe verdict.

As a local diagnostic (no target domains were contacted), the current model assigned the no-warning class to the individual strings `jabry.com`, `evil-hacker-site.ru`, `yahoo.com`, and `paypa1.com`, with scores between 0.10 and 0.14. This demonstrates the model's lexical blind spot; these scores are not reputation checks or ground-truth verdicts for those domains. Concatenating several addresses into one input is malformed; repeated schemes in the host are now rejected so the model cannot issue a result for that combined string. Check one complete HTTP(S) address at a time.

This project is an educational baseline, not a practical phishing defense. A future security-focused version would need a safely sourced and maintained reputation feed, robust brand-lookalike detection, broader URL features, and external/time-based validation before making stronger claims.

## Scheme investigation and evidence

The local source has no raw URLs or extractor implementation, so these observations cannot prove original source parity. The observed `qty_slash_url` minimum is 0 (17,507 rows), and `length_url` minimum is 4. Counting a complete absolute HTTP(S) input necessarily contributes two scheme slashes and seven or eight scheme characters. This strongly argues against the source values being counts of complete absolute HTTP(S) strings. It is consistent with scheme stripping or with source strings that were scheme-less; among the project options, explicit scheme stripping is the most defensible, reproducible convention. It remains an inference, not proof of upstream behavior.

The 17 fields are sparse except for dot, slash, and length. Selected distributions (all 58,645 rows):

| Feature | Min | Median | Mean | Max | Zero rows |
|---|---:|---:|---:|---:|---:|
| `length_url` | 4 | 29 | 44.9593 | 4,165 | 0 |
| `qty_dot_url` | 1 | 2 | 2.2843 | 24 | 0 |
| `qty_hyphen_url` | 0 | 0 | 0.4571 | 35 | 45,045 |
| `qty_underline_url` | 0 | 0 | 0.1713 | 21 | 53,357 |
| `qty_slash_url` | 0 | 1 | 1.9375 | 44 | 17,507 |
| `qty_questionmark_url` | 0 | 0 | 0.0141 | 9 | 57,896 |
| `qty_equal_url` | 0 | 0 | 0.3112 | 23 | 51,337 |
| `qty_at_url` | 0 | 0 | 0.0335 | 43 | 56,935 |
| `qty_and_url` | 0 | 0 | 0.2130 | 26 | 54,847 |
| `qty_exclamation_url` | 0 | 0 | 0.0045 | 10 | 58,452 |
| `qty_tilde_url` | 0 | 0 | 0.0049 | 5 | 58,428 |
| `qty_comma_url` | 0 | 0 | 0.0033 | 11 | 58,521 |
| `qty_plus_url` | 0 | 0 | 0.0042 | 19 | 58,516 |
| `qty_asterisk_url` | 0 | 0 | 0.0069 | 60 | 58,586 |
| `qty_hashtag_url` | 0 | 0 | 0.0008 | 13 | 58,634 |
| `qty_dollar_url` | 0 | 0 | 0.0029 | 10 | 58,591 |
| `qty_percent_url` | 0 | 0 | 0.1625 | 174 | 57,109 |

Observed strongest pairwise relationships include `qty_equal_url`/`qty_and_url` (Pearson r=0.892), `length_url`/`qty_equal_url` (r=0.645), `length_url`/`qty_and_url` (r=0.580), and `length_url`/`qty_slash_url` (r=0.526). These are descriptive associations and do not establish feature-generation rules.

## Representative comparison

Counts below use Python character length and literal punctuation counts. Scheme-stripped values are the project feature values; complete values illustrate what inclusion would do. Other selected punctuation counts are identical in these examples because the scheme contains none of them.

| Input | Counting convention | `length_url` | `qty_slash_url` | `qty_dot_url` | `qty_questionmark_url` | `qty_equal_url` |
|---|---|---:|---:|---:|---:|---:|
| `https://example.com/login?user=test` | Complete input | 35 | 3 | 1 | 1 | 1 |
| same | Strip `https://` | 27 | 1 | 1 | 1 | 1 |
| `http://example.com/login?user=test` | Complete input | 34 | 3 | 1 | 1 | 1 |
| same | Strip `http://` | 27 | 1 | 1 | 1 | 1 |
| `https://example.com/` | Complete input | 20 | 3 | 1 | 0 | 0 |
| same | Strip `https://` | 12 | 1 | 1 | 0 | 0 |

## Source parity and readiness boundary

The selected feature names are based on published dataset definitions; the original feature-extraction implementation is unavailable. The local extractor is a reconstructed, deterministic implementation. Exact numerical parity with upstream precomputed values cannot be proven, and this project does not claim exact upstream extractor reproduction. The local CSV contains no raw URLs, so its 17 precomputed values cannot be transformed or checked URL-by-URL under this convention. Training uses those same-named columns while live inference applies the deterministic extractor, scaler, and feature order. Source parity remains unverified, so measured performance does not establish live accuracy.


## Historical parser audit and auxiliary fields

Target encoding is **VERIFIED**: `0 = legitimate`, `1 = phishing`. The upstream dataset README documents those meanings and exact counts matching the local file. The local CSV itself contains no raw URLs, so the original feature extraction cannot be replayed and exact parity is not proven.

The deterministic implementation is `backend/app/ml/feature_extractor.py`. `extract_url_features(raw_url)` validates and extracts values without network access. `MODEL_FEATURES` is the ordered, 17-column schema; `select_model_vector(mapping)` orders both live values and precomputed dataset rows identically. It does not scale values or predict. Future preprocessing/scaling must be fitted on training data only and reused unchanged at inference.

> **PARITY NOT VERIFIED:** This status applies to the selected feature values as generated by the upstream dataset pipeline. The upstream README gives feature names and short meanings but no implementation or raw URL examples. Local tests verify this extractor against the explicit local contract below, not against upstream-generated values. Straight character counts are conceptually supported by the source descriptions; their exact input normalization remains unknown. Path/file/query split rules, email detection, domain normalization, IDN behavior, and sentinels must not be presented as upstream-confirmed.

The historical 41 candidate features are based on published dataset feature definitions. The original upstream feature-extraction implementation is unavailable. Therefore exact numerical parity with upstream precomputed feature values cannot be proven. The local extractor is a reconstructed, deterministic implementation; we will not claim it reproduces the upstream extractor exactly.

## Training-readiness decision (final)

The old 41-feature live candidate is rejected due to uncertain component definitions and the likely scheme convention mismatch. Option C is now finalized and implemented as a 17-field scheme-stripped representation. The dataset has no raw URLs, so those historical values cannot be regenerated or verified URL-by-URL. Training uses the same-named precomputed columns as an explicitly limited project experiment; source parity and expected live performance remain uncertain. The current measured results are documented in `docs/MODEL_COMPARISON.md`.

## Feature mapping

Observed source ranges below are computed from all 58,645 dataset records; they are not guaranteed live input limits. “Sentinel” describes source CSV usage. Example values are produced by the documented Phase 2 extractor for the sample URL above.

| Dataset feature | Meaning and raw URL calculation | Example | Observed source range | `-1` sentinel? | Assumption / limitation |
|---|---|---:|---:|---|---|
| `length_url` | Python character length after removing leading HTTP(S) scheme | 27 | 4–4,165 | No | Scheme and delimiter are stripped only for model calculations. Unicode counts as Python code points. |
| `qty_dot_url` | Number of `.` characters in scheme-stripped URL representation | 1 | 1–24 | No | Includes any URL component and fragment. |
| `qty_hyphen_url` | Count `-` in scheme-stripped URL representation | 0 | 0–35 | No | Literal character count. |
| `qty_underline_url` | Count `_` in scheme-stripped URL representation | 0 | 0–21 | No | Literal character count. |
| `qty_slash_url` | Count `/` in scheme-stripped URL representation | 1 | 0–44 | No | Scheme delimiter is removed before counting. |
| `qty_questionmark_url` | Count `?` in scheme-stripped URL representation | 1 | 0–9 | No | Includes query delimiter and any later literal `?`. |
| `qty_equal_url` | Count `=` in scheme-stripped URL representation | 1 | 0–23 | No | Literal character count. |
| `qty_at_url` | Count `@` in scheme-stripped URL representation | 0 | 0–43 | No | Includes user-info if present; user-info is not separately used. |
| `qty_and_url` | Count `&` in scheme-stripped URL representation | 0 | 0–26 | No | Literal character count. |
| `qty_exclamation_url` | Count `!` in scheme-stripped URL representation | 0 | 0–10 | No | Literal character count. |
| `qty_tilde_url` | Count `~` in scheme-stripped URL representation | 0 | 0–5 | No | Literal character count. |
| `qty_comma_url` | Count `,` in scheme-stripped URL representation | 0 | 0–11 | No | Literal character count. |
| `qty_plus_url` | Count `+` in scheme-stripped URL representation | 0 | 0–19 | No | Literal character count; no query decoding. |
| `qty_asterisk_url` | Count `*` in scheme-stripped URL representation | 0 | 0–60 | No | Literal character count. |
| `qty_hashtag_url` | Count `#` in scheme-stripped URL representation | 0 | 0–13 | No | Counts fragment delimiter too. |
| `qty_dollar_url` | Count `$` in scheme-stripped URL representation | 0 | 0–10 | No | Literal character count. |
| `qty_percent_url` | Count `%` in scheme-stripped URL representation | 0 | 0–174 | No | Counts percent-encoding markers without decoding. |
| `domain_length` | Character length of parsed hostname, excluding user-info, port, and brackets around an IPv6 literal | 11 | 4–231 | No | `urllib.parse` hostname; IDN is not converted to ASCII/punycode. |
| `qty_dot_domain` | Number of dots in parsed hostname | 1 | 0–21 | No | A subdomain-structure proxy only; no public-suffix database is used. |
| `qty_hyphen_domain` | Count `-` in hostname | 0 | 0–11 | No | Hostname only, excluding port. |
| `qty_underline_domain` | Count `_` in hostname | 0 | 0–2 | No | Some host syntax validators may reject this; current parser accepts URL hostname text. |
| `qty_vowels_domain` | Count ASCII `a,e,i,o,u` in hostname, case-insensitive | 4 | 0–61 | No | Y is not counted; Unicode vowels are not counted. |
| `domain_in_ip` | 1 if hostname parses as IPv4/IPv6 literal, else 0 | 0 | 0–1 | No | No DNS lookup; brackets stripped only for IPv6 parsing. |
| `server_client_domain` | 1 if lowercased hostname contains `server` or `client`, else 0 | 0 | 0–1 | No | Follows the upstream README's brief description. |
| `directory_length` | Length of path prefix preceding final non-empty segment; separator after directory is retained | -1 | -1–1,286 | Yes, source uses `-1` for absent directory | Candidate segmentation rule; exact upstream rule unavailable. |
| `qty_dot_directory` | Count `.` in the directory string above | -1 | -1–19 | Yes | Same candidate directory rule. |
| `qty_hyphen_directory` | Count `-` in the directory string | -1 | -1–23 | Yes | Same candidate directory rule. |
| `qty_underline_directory` | Count `_` in the directory string | -1 | -1–17 | Yes | Same candidate directory rule. |
| `qty_slash_directory` | Count `/` in the directory string | -1 | -1–22 | Yes | Separator slash is retained by this local rule. |
| `file_length` | Length of final non-empty path segment when path does not end in `/` | 5 | -1–1,232 | Yes, source uses `-1` when absent | File means final URL path segment, not a verified filesystem file. |
| `qty_dot_file` | Count `.` in final path segment | 0 | -1–12 | Yes | Raw, percent-encoded path segment. |
| `qty_hyphen_file` | Count `-` in final path segment | 0 | -1–21 | Yes | Raw, percent-encoded path segment. |
| `qty_slash_file` | Count `/` in final path segment | 0 | -1–0 | Yes | By construction a path segment contains no slash. |
| `params_length` | Character length of raw query after `?`, excluding `?` | 9 | -1–4,094 | Yes, source uses `-1` when absent | Query is not percent-decoded. An explicit empty `?` is present length 0. |
| `qty_params` | Count non-empty `&`-separated query parts | 1 | -1–23 | Yes | Empty query parts are ignored; source's exact counting rule is not documented. |
| `qty_equal_params` | Count `=` in raw query | 1 | -1–23 | Yes | Query delimiter excluded; later `?` characters remain ordinary query characters. |
| `qty_and_params` | Count `&` in raw query | 0 | -1–22 | Yes | Raw query count. |
| `qty_at_params` | Count `@` in raw query | 0 | -1–10 | Yes | Raw query count. |
| `qty_percent_params` | Count `%` in raw query | 0 | -1–65 | Yes | Encoded characters are counted as written, not decoded. |
| `qty_questionmark_params` | Count `?` in raw query | 0 | -1–9 | Yes | First `?` is the URL query delimiter and excluded. |
| `email_in_url` | 1 if raw URL contains a substring matching `[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}` case-insensitively; else 0 | 0 | 0–1 | No | Local rule requires a dotted domain and ASCII TLD of at least two letters; no boundary check. Upstream only says “email present.” **PARITY NOT VERIFIED.** |

The subset intentionally excludes `qty_space_url`: submitted whitespace is rejected, so it would be constant zero at live inference. Domain punctuation fields that were constant zero in the source are also omitted.

## `urllib.parse` behavior and local validation

- `urlsplit` separates scheme, authority, path, query, and fragment; it does not fetch or resolve anything.
- `parts.hostname` lowercases the hostname and removes user-info, port, and IPv6 brackets. ASCII hostname length is unchanged by case folding. The exact upstream treatment of these components and Unicode/IDN hosts is unknown (**PARITY NOT VERIFIED**).
- Path and query text remain percent-encoded; this extractor does not decode `%2F` into `/`. The fragment is separated from the query, while raw URL length and whole-string counts still include it.
- The input is checked for whitespace and ASCII control characters before `urlsplit`, because Python versions of `urlsplit` may strip some control whitespace. The validator requires HTTP(S), a host, valid numeric port syntax, non-empty port if a colon is supplied, valid `%HH` escapes, and at most 8,192 characters. This is a project input policy, not a claim that `urllib.parse` performs complete browser-grade URL validation.
- `urlsplit` accepts some unusual hostname text (for example underscores) and has version-specific parsing rules. IDNA conversion, canonicalization, and browser equivalence are not attempted.

## Important requested signals that are not model features

- **HTTPS:** no HTTPS indicator column exists in this dataset; do not invent one for the current model. Scheme text is removed before project whole-URL counts; no HTTPS indicator is added.
- **Digit count:** no digit-count feature exists; do not invent it.
- **Subdomain count:** no dedicated column exists. `qty_dot_domain` counts hostname dots but is only a rough structural proxy, not a public-suffix-aware subdomain count.
- **Aggregate path length:** no `path_length` column exists. Use source columns `directory_length` and `file_length` under the explicit local split rule.

## Absent-component and parsing rules

| Input condition | Phase 2 representation |
|---|---|
| No path or root path `/` | `directory_* = -1`, `file_* = -1` |
| Path has one segment, e.g. `/login` | directory `-1`; file is `login` |
| Nested path `/account/login` | directory `account/`; file `login` |
| Path ends in `/`, e.g. `/account/` | directory `account/`; file `-1` |
| No query delimiter | every selected query feature = `-1` |
| Explicit empty query `?` | query length and character counts 0; `qty_params=0` |
| No fragment | no dedicated value; no fragment feature exists |
| Fragment present | remains in `length_url` and whole-URL counts; excluded from parsed path/query |
| No subdomain | no special sentinel; hostname counts are computed normally |
| No port | no port feature; domain features use hostname and raw URL counts include input text |
| Port present | validated; excluded from hostname/domain counts but included in raw URL length/counts |
| No scheme | reject; do not auto-prepend one because it would alter raw-string features |
| Malformed `%` escape | reject unless `%` is followed by two hexadecimal characters |

For present components, empty strings have length/count 0. For absent components, use `-1`, matching observed source sentinels. The local candidate `qty_params` rule counts non-empty pieces after splitting the raw query on `&`; repeated/leading/trailing separators therefore do not count empty pieces. The explicit empty query `?` yields 0. These diagnostic component conventions are provisional and are not used by the final 17-input model. The implementation rejects URLs over 8,192 characters; this covers the source's observed maximum URL length of 4,165, although accepted URLs above that source maximum would be out-of-range inputs. Exact agreement with original feature generation remains unverified.

The path rule for `/a/b/login.php` yields directory `a/b/` (length 4, two slashes) and leaf `login.php` (length 9, one dot). `/a/` yields directory `a/` and absent file; `/a/b/` yields directory `a/b/` and absent file. The source docs do not specify whether the final non-trailing segment is the `file` component, whether the directory keeps its final slash, or how extensionless paths are treated. These values are a local provisional rule only: **PARITY NOT VERIFIED**. These auxiliary component fields are excluded from the finalized 17 model inputs.

## Regression tests

`backend/tests/test_feature_extractor.py` contains **32 deterministic unittest methods** (with additional URL subcases). It covers exact names/order and integer types; the exact 17-value model vector; HTTPS and HTTP; no/root/single/nested/trailing-slash/file paths including all five requested path examples; single/multiple/empty query and email parameter; fragment; port; IPv4; subdomain; user-info `@`; email-like path/query and non-matches; special characters; percent encoding; absent sentinels; invalid and scheme-less inputs; vector ordering; and no target/network-derived outputs. It does not load the phishing dataset. Current final run: **32 passed, 0 failed**.

## Canonical pipeline

```text
original URL -> validate_url -> scheme-strip whole-URL text -> extract_url_features -> select 17 fields
                                                         -> saved train-only scaler -> Bayesian logistic model
```

`extract_url_features` is the one live parser; `select_model_vector` applies the identical named feature order to live dictionaries and source rows. The source rows already contain precomputed features and no URLs, so the original 58,645 training inputs cannot be re-extracted by this parser. The shared selector gives schema/order consistency, not proof of equal historical parsing. **PARITY NOT VERIFIED.** This parity limitation remains in effect for the trained dataset model; do not present it as validated on live URLs.

The production scaling parameters are fitted using training rows only and serialized/reused unchanged for test and live inputs. Never fit scaling or PCA on all rows before splitting. Keep all rows with the same 111-feature key in one split to prevent duplicate leakage.

## Excluded features

| Columns | Reason excluded from raw-URL inference |
|---|---|
| `time_response` | Requires network/runtime measurement. |
| `domain_spf`, `asn_ip`, `qty_ip_resolved`, `qty_nameservers`, `qty_mx_servers`, `ttl_hostname` | DNS, IP resolution, or ASN infrastructure data. |
| `time_domain_activation`, `time_domain_expiration` | WHOIS/registration history. |
| `tls_ssl_certificate` | Requires TLS connection/certificate inspection. |
| `qty_redirects` | Requires visiting/following the URL. |
| `url_google_index`, `domain_google_index` | Search-engine index/reputation query. |
| `url_shortened` | Requires a defined shortening-provider list or external metadata. |
| `qty_tld_url`, `tld_present_params` | Exact source public-suffix/TLD rule is unspecified; avoid a guessed rule. |
| `qty_space_url` | Input whitespace is rejected, causing constant zero at live inference. |
| 13 constant domain punctuation fields | No variation in this source; not informative and often impossible in a valid hostname. |

No request URL is opened, resolved, or executed. These parity limitations apply to the actual holdout metrics as well as live inference.


## Measured training and inference status

The grouped 80/20 holdout has been trained and evaluated; see `docs/MODEL_COMPARISON.md`. The source has no raw URL column, so the shared live extractor cannot literally be replayed on training rows. The project uses the same 17 feature names and inferred scheme-stripped convention, but corresponding source numerical semantics remain unverified. The predictor does apply the saved training-only standardizer and the exact `MODEL_FEATURES` order to extracted live values.

The original dataset contains precomputed URL features but does not contain raw URLs or the upstream feature-extraction implementation. Therefore exact numerical parity with the original extractor cannot be verified. This project uses a reconstructed deterministic 17-feature representation consistently for training and live prediction.
