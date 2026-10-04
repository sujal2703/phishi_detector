"""Deterministic, network-free URL parsing for the PHISHY live feature subset.

This module intentionally returns only feature names already present in the
source CSV. It does not fetch, resolve, execute, or otherwise visit a URL.
"""

from __future__ import annotations

import ipaddress
import re
from collections.abc import Mapping
from urllib.parse import SplitResult, urlsplit


MAX_URL_LENGTH = 8_192

_CHAR_FEATURES = {
    "dot": ".",
    "hyphen": "-",
    "underline": "_",
    "slash": "/",
    "questionmark": "?",
    "equal": "=",
    "at": "@",
    "and": "&",
    "exclamation": "!",
    "space": " ",
    "tilde": "~",
    "comma": ",",
    "plus": "+",
    "asterisk": "*",
    "hashtag": "#",
    "dollar": "$",
    "percent": "%",
}

_URL_CHAR_FEATURES = tuple(
    f"qty_{name}_url" for name in _CHAR_FEATURES if name != "space"
)
_DOMAIN_CHAR_FEATURES = (
    "qty_dot_domain",
    "qty_hyphen_domain",
    "qty_underline_domain",
)
_COMPONENTS = {
    "directory": "directory_length",
    "file": "file_length",
    "params": "params_length",
}

# Final ordered training/live input schema. All names exist in the source CSV.
MODEL_FEATURES = (
    "length_url", "qty_dot_url", "qty_hyphen_url", "qty_underline_url",
    "qty_slash_url", "qty_questionmark_url", "qty_equal_url", "qty_at_url",
    "qty_and_url", "qty_exclamation_url", "qty_tilde_url", "qty_comma_url",
    "qty_plus_url", "qty_asterisk_url", "qty_hashtag_url", "qty_dollar_url",
    "qty_percent_url",
)

# Additional reconstructed diagnostic fields retained for existing analysis;
# these are not model inputs.
EXTRACTED_FEATURES = (
    *MODEL_FEATURES,
    "domain_length",
    *_DOMAIN_CHAR_FEATURES,
    "qty_vowels_domain",
    "domain_in_ip",
    "server_client_domain",
    "directory_length",
    "qty_dot_directory",
    "qty_hyphen_directory",
    "qty_underline_directory",
    "qty_slash_directory",
    "file_length",
    "qty_dot_file",
    "qty_hyphen_file",
    "qty_slash_file",
    "params_length",
    "qty_params",
    "qty_equal_params",
    "qty_and_params",
    "qty_at_params",
    "qty_percent_params",
    "qty_questionmark_params",
    "email_in_url",
)


class URLValidationError(ValueError):
    """Raised when input is not an acceptable absolute HTTP(S) URL."""


def _component_features(name: str, value: str | None) -> dict[str, int]:
    """Build a dataset-named path/query component vector.

    `None` denotes an absent URL component and maps to the dataset's observed
    -1 convention. An empty but explicitly present component maps to length 0
    and punctuation counts 0.
    """
    feature_suffix = name
    length_column = _COMPONENTS[name]
    if value is None:
        result = {f"qty_{kind}_{feature_suffix}": -1 for kind in _CHAR_FEATURES}
        result[length_column] = -1
        return result
    result = {
        f"qty_{kind}_{feature_suffix}": value.count(char)
        for kind, char in _CHAR_FEATURES.items()
    }
    result[length_column] = len(value)
    return result


def _path_parts(path: str) -> tuple[str | None, str | None]:
    """Return candidate (directory, file) components under a local rule.

    Directory retains the separating slash after its final directory segment.
    The final segment is assigned to the source's `file` feature only when the
    path does not end in `/`. This convention is provisional: upstream docs name
    directory/file features but do not define their segmentation. Absent parts
    are None and therefore receive -1 feature values.
    """
    if not path or path == "/":
        return None, None

    trailing_slash = path.endswith("/")
    body = path[1:] if path.startswith("/") else path
    segments = body.split("/")
    if trailing_slash:
        segments = segments[:-1]
    if not segments or all(segment == "" for segment in segments):
        return None, None

    if trailing_slash:
        directory = "/".join(segments) + "/"
        return directory or None, None

    file_part = segments[-1]
    directory_segments = segments[:-1]
    directory = "/".join(directory_segments) + "/" if directory_segments else None
    return directory, file_part if file_part != "" else None


def _is_ip_literal(host: str) -> int:
    candidate = host[1:-1] if host.startswith("[") and host.endswith("]") else host
    try:
        ipaddress.ip_address(candidate)
        return 1
    except ValueError:
        return 0


def _contains_email(text: str) -> int:
    # A deterministic lexical marker only; this does not verify an address.
    return int(bool(re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE)))


def validate_url(url: str) -> tuple[str, SplitResult]:
    """Validate an absolute HTTP(S) URL and return its raw text and parsed parts.

    Scheme-less input is rejected rather than silently rewritten, because
    rewriting would change `length_url` and other whole-string counts.
    """
    if not isinstance(url, str):
        raise URLValidationError("URL must be text.")
    if not url:
        raise URLValidationError("URL is empty.")
    if url != url.strip() or any(character.isspace() for character in url):
        raise URLValidationError("URL must not contain whitespace.")
    if any(ord(character) < 0x20 or ord(character) == 0x7F for character in url):
        raise URLValidationError("URL must not contain ASCII control characters.")
    if len(url) > MAX_URL_LENGTH:
        raise URLValidationError(f"URL exceeds the {MAX_URL_LENGTH}-character limit.")
    if re.search(r"%(?![0-9A-Fa-f]{2})", url):
        raise URLValidationError("URL contains an invalid percent-encoding escape.")

    try:
        parts = urlsplit(url)
        if parts.scheme.lower() not in {"http", "https"}:
            raise URLValidationError("URL must use http:// or https://.")
        if not parts.netloc or not parts.hostname:
            raise URLValidationError("URL must include a host.")
        if re.search(r"https?://", parts.netloc, re.IGNORECASE):
            raise URLValidationError("Enter one web address only. Remove the extra http:// or https:// links.")
        if parts.netloc.endswith(":"):
            raise URLValidationError("URL port cannot be empty.")
        # Accessing .port validates malformed and out-of-range port syntax.
        _ = parts.port
    except ValueError as error:
        if isinstance(error, URLValidationError):
            raise
        raise URLValidationError("URL has invalid host or port syntax.") from error
    return url, parts


def normalize_for_model(url: str) -> str:
    """Return the validated representation used by project whole-URL fields."""
    raw, parts = validate_url(url)
    return raw[len(parts.scheme) + 3:]


def extract_url_features(url: str) -> dict[str, int]:
    """Extract the reconstructed feature dictionary, without network access.

    Returned keys are existing dataset columns only. PARITY NOT VERIFIED:
    the local CSV has no raw URLs or authoritative extractor, so source values
    cannot be compared with this implementation.
    """
    raw, parts = validate_url(url)
    # Keep raw intact for parsing/display and auxiliary rules.
    project_url = normalize_for_model(raw)
    host = parts.hostname or ""
    host_for_rules = host.lower()

    features: dict[str, int] = {"length_url": len(project_url)}
    features.update({column: project_url.count(_CHAR_FEATURES[column[4:-4]]) for column in _URL_CHAR_FEATURES})

    features["domain_length"] = len(host)
    features.update({column: host.count(_CHAR_FEATURES[column[4:-7]]) for column in _DOMAIN_CHAR_FEATURES})
    features["qty_vowels_domain"] = sum(char in "aeiou" for char in host_for_rules)
    features["domain_in_ip"] = _is_ip_literal(host)
    features["server_client_domain"] = int("server" in host_for_rules or "client" in host_for_rules)

    directory, file_part = _path_parts(parts.path)
    features.update(_component_features("directory", directory))
    features.update(_component_features("file", file_part))

    # Preserve whether a question-mark delimiter was present, including `?`.
    question_mark_present = "?" in raw.split("#", 1)[0]
    query = parts.query if question_mark_present else None
    features.update(_component_features("params", query))
    if query is None or query == "":
        features["qty_params"] = 0 if query == "" else -1
    else:
        features["qty_params"] = sum(bool(part) for part in query.split("&"))

    features["email_in_url"] = _contains_email(raw)
    return {name: features[name] for name in EXTRACTED_FEATURES}


def select_model_vector(features: Mapping[str, int]) -> list[int]:
    """Order a feature mapping identically for dataset rows and live URLs."""
    missing = [name for name in MODEL_FEATURES if name not in features]
    if missing:
        raise ValueError(f"Missing model features: {', '.join(missing)}")
    return [int(features[name]) for name in MODEL_FEATURES]
