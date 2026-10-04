"""Regression tests for the network-free PHISHY URL feature contract."""

from __future__ import annotations

import socket
import unittest
from unittest.mock import patch

from backend.app.ml.feature_extractor import (
    MODEL_FEATURES,
    URLValidationError,
    extract_url_features,
    select_model_vector,
    validate_url,
)


EXPECTED_EXTRACTED_FEATURES = (
    "length_url",
    "qty_dot_url",
    "qty_hyphen_url",
    "qty_underline_url",
    "qty_slash_url",
    "qty_questionmark_url",
    "qty_equal_url",
    "qty_at_url",
    "qty_and_url",
    "qty_exclamation_url",
    "qty_tilde_url",
    "qty_comma_url",
    "qty_plus_url",
    "qty_asterisk_url",
    "qty_hashtag_url",
    "qty_dollar_url",
    "qty_percent_url",
    "domain_length",
    "qty_dot_domain",
    "qty_hyphen_domain",
    "qty_underline_domain",
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
EXPECTED_FEATURES = EXPECTED_EXTRACTED_FEATURES[:17]


class FeatureExtractorTests(unittest.TestCase):
    def features(self, url: str) -> dict[str, int]:
        return extract_url_features(url)

    def test_schema_names_and_order_are_exact(self) -> None:
        self.assertEqual(MODEL_FEATURES, EXPECTED_FEATURES)
        features = self.features("https://example.com/login?user=test")
        self.assertEqual(tuple(features), EXPECTED_EXTRACTED_FEATURES)
        self.assertTrue(all(type(value) is int for value in features.values()))

    def test_shared_vector_selector_uses_canonical_order(self) -> None:
        features = self.features("https://example.com/login?user=test")
        reversed_features = dict(reversed(list(features.items())))
        self.assertEqual(select_model_vector(reversed_features), [features[name] for name in MODEL_FEATURES])

    def test_a_normal_https_url(self) -> None:
        f = self.features("https://example.com/login?user=test")
        self.assertEqual((f["length_url"], f["qty_slash_url"], f["qty_questionmark_url"]), (27, 1, 1))
        self.assertEqual((f["domain_length"], f["qty_dot_domain"], f["file_length"]), (11, 1, 5))
        self.assertEqual((f["params_length"], f["qty_params"], f["qty_equal_params"]), (9, 1, 1))

    def test_sample_url_has_exact_expected_17_value_vector(self) -> None:
        f = self.features("https://example.com/login?user=test")
        expected = (
            27, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
        )
        self.assertEqual(select_model_vector(f), list(expected))

    def test_b_http_url(self) -> None:
        f = self.features("http://example.com/login")
        self.assertEqual((f["length_url"], f["qty_slash_url"]), (17, 1))
        self.assertEqual(f["domain_length"], 11)
        self.assertEqual(f["file_length"], 5)

    def test_http_and_https_share_scheme_stripped_model_values(self) -> None:
        http_url = "http://example.com/login?user=test"
        https_url = "https://example.com/login?user=test"
        original = https_url
        http_features = self.features(http_url)
        https_features = self.features(https_url)
        self.assertEqual(select_model_vector(http_features), select_model_vector(https_features))
        self.assertEqual((http_features["length_url"], http_features["qty_slash_url"]), (27, 1))
        self.assertEqual((https_features["length_url"], https_features["qty_slash_url"]), (27, 1))
        self.assertEqual(https_url, original)

    def test_c_no_path_and_root_path_have_no_directory_or_file(self) -> None:
        for url in ("https://example.com", "https://example.com/"):
            with self.subTest(url=url):
                f = self.features(url)
                self.assertEqual(f["directory_length"], -1)
                self.assertEqual(f["file_length"], -1)
                self.assertEqual(f["params_length"], -1)

    def test_d_single_path_segment_uses_provisional_file_rule(self) -> None:
        f = self.features("https://example.com/login")
        self.assertEqual((f["directory_length"], f["file_length"]), (-1, 5))

    def test_e_nested_path_separates_directory_and_leaf(self) -> None:
        f = self.features("https://example.com/a/b/login.php?user=test")
        self.assertEqual((f["directory_length"], f["qty_slash_directory"]), (4, 2))
        self.assertEqual((f["file_length"], f["qty_dot_file"]), (9, 1))

    def test_f_filename_with_extension(self) -> None:
        f = self.features("https://example.com/login.php")
        self.assertEqual((f["file_length"], f["qty_dot_file"]), (9, 1))
        self.assertEqual(f["directory_length"], -1)

    def test_trailing_slash_a_is_directory_without_file(self) -> None:
        f = self.features("https://example.com/a/")
        self.assertEqual((f["directory_length"], f["qty_slash_directory"]), (2, 1))
        self.assertEqual(f["file_length"], -1)

    def test_trailing_slash_a_b_is_directory_without_file(self) -> None:
        f = self.features("https://example.com/a/b/")
        self.assertEqual((f["directory_length"], f["qty_slash_directory"]), (4, 2))
        self.assertEqual(f["file_length"], -1)

    def test_path_a_b_login_php(self) -> None:
        f = self.features("https://example.com/a/b/login.php")
        self.assertEqual((f["directory_length"], f["file_length"]), (4, 9))

    def test_g_single_query_parameter(self) -> None:
        f = self.features("https://example.com/?a=1")
        self.assertEqual((f["params_length"], f["qty_params"]), (3, 1))
        self.assertEqual((f["qty_equal_params"], f["qty_and_params"]), (1, 0))

    def test_h_multiple_query_parameters(self) -> None:
        f = self.features("https://example.com/?a=1&b=2")
        self.assertEqual((f["params_length"], f["qty_params"]), (7, 2))
        self.assertEqual((f["qty_equal_params"], f["qty_and_params"]), (2, 1))

    def test_i_explicit_empty_query_is_present_zero_not_sentinel(self) -> None:
        f = self.features("https://example.com/?")
        self.assertEqual((f["params_length"], f["qty_params"]), (0, 0))
        self.assertEqual(f["qty_equal_params"], 0)

    def test_j_fragment_is_in_whole_url_but_not_query(self) -> None:
        f = self.features("https://example.com/path#frag?x=1")
        self.assertEqual(f["qty_hashtag_url"], 1)
        self.assertEqual(f["params_length"], -1)
        self.assertEqual(f["qty_questionmark_params"], -1)

    def test_k_port_does_not_enter_domain_features(self) -> None:
        without_port = self.features("https://example.com/a")
        with_port = self.features("https://example.com:8443/a")
        for name in ("domain_length", "qty_dot_domain", "qty_vowels_domain"):
            self.assertEqual(with_port[name], without_port[name])
        self.assertGreater(with_port["length_url"], without_port["length_url"])

    def test_l_ipv4_literal_detection(self) -> None:
        f = self.features("https://192.168.1.1/login")
        self.assertEqual((f["domain_length"], f["qty_dot_domain"]), (11, 3))
        self.assertEqual((f["domain_in_ip"], f["qty_vowels_domain"]), (1, 0))

    def test_m_subdomain_counts_host_dots(self) -> None:
        f = self.features("https://sub.example.com")
        self.assertEqual((f["domain_length"], f["qty_dot_domain"]), (15, 2))
        self.assertEqual(f["domain_in_ip"], 0)

    def test_urllib_hostname_is_lowercased_without_changing_ascii_length(self) -> None:
        f = self.features("https://ExAmPlE.CoM")
        self.assertEqual((f["domain_length"], f["qty_dot_domain"]), (11, 1))
        self.assertEqual(f["qty_vowels_domain"], 4)

    def test_server_client_domain_keyword_marker(self) -> None:
        self.assertEqual(self.features("https://my-server.example.com")["server_client_domain"], 1)
        self.assertEqual(self.features("https://example.com")["server_client_domain"], 0)

    def test_n_at_sign_in_userinfo_is_whole_url_only(self) -> None:
        f = self.features("https://user@example.com/path")
        self.assertEqual(f["qty_at_url"], 1)
        self.assertEqual(f["qty_at_params"], -1)
        self.assertEqual(f["domain_length"], 11)

    def test_o_email_marker_path_and_query(self) -> None:
        self.assertEqual(self.features("https://example.com/test@example.com")["email_in_url"], 1)
        f = self.features("https://example.com/?email=test@example.com")
        self.assertEqual(f["email_in_url"], 1)
        self.assertEqual(f["qty_at_params"], 1)

    def test_email_marker_rejects_non_email_lookalikes(self) -> None:
        self.assertEqual(self.features("https://example.com/mail")["email_in_url"], 0)
        self.assertEqual(self.features("https://example.com/@user")["email_in_url"], 0)

    def test_p_special_characters_are_literal_counts(self) -> None:
        url = "https://example.com/a-b_c~d,e+f*g$h%25?x=!&y=$#frag!"
        f = self.features(url)
        self.assertEqual(f["qty_hyphen_url"], 1)
        self.assertEqual(f["qty_underline_url"], 1)
        self.assertEqual(f["qty_tilde_url"], 1)
        self.assertEqual(f["qty_comma_url"], 1)
        self.assertEqual(f["qty_plus_url"], 1)
        self.assertEqual(f["qty_asterisk_url"], 1)
        self.assertEqual(f["qty_dollar_url"], 2)
        self.assertEqual(f["qty_percent_url"], 1)
        self.assertEqual(f["qty_hashtag_url"], 1)
        self.assertEqual(f["qty_exclamation_url"], 2)

    def test_q_percent_encoding_is_counted_without_decoding(self) -> None:
        f = self.features("https://example.com/p%2Fq?x=%40")
        self.assertEqual((f["file_length"], f["qty_slash_file"]), (5, 0))
        self.assertEqual((f["params_length"], f["qty_percent_params"]), (5, 1))
        self.assertEqual(f["qty_percent_url"], 2)

    def test_r_absent_path_file_and_query_use_minus_one(self) -> None:
        f = self.features("https://example.com")
        absent = (
            "directory_length", "qty_dot_directory", "qty_hyphen_directory",
            "qty_underline_directory", "qty_slash_directory", "file_length",
            "qty_dot_file", "qty_hyphen_file", "qty_slash_file", "params_length",
            "qty_params", "qty_equal_params", "qty_and_params", "qty_at_params",
            "qty_percent_params", "qty_questionmark_params",
        )
        self.assertTrue(all(f[name] == -1 for name in absent))

    def test_s_invalid_urls_are_rejected(self) -> None:
        invalid = (
            "", "https://", "https:///host", "ftp://example.com", "https://example.com:bad/",
            "https://example.com:99999/", "https://example.com:/", "https://example.com/a b",
            "https://example.com/%ZZ", "https://[not-ip]/", "https://exa\x00mple.com/",
        )
        for url in invalid:
            with self.subTest(url=url):
                with self.assertRaises(URLValidationError):
                    validate_url(url)

    def test_t_scheme_less_url_is_rejected(self) -> None:
        with self.assertRaises(URLValidationError):
            validate_url("example.com/login")

    def test_non_string_input_is_rejected(self) -> None:
        with self.assertRaises(URLValidationError):
            validate_url(None)  # type: ignore[arg-type]

    def test_extractor_does_not_use_network_or_target_features(self) -> None:
        with patch.object(socket, "gethostbyname", side_effect=AssertionError("DNS used")), patch.object(
            socket, "create_connection", side_effect=AssertionError("network used")
        ):
            f = self.features("https://example.com/login")
        self.assertNotIn("phishing", f)
        self.assertNotIn("time_response", f)
        self.assertNotIn("asn_ip", f)
        self.assertNotIn("tls_ssl_certificate", f)
        self.assertEqual(len(f), 41)


if __name__ == "__main__":
    unittest.main()
