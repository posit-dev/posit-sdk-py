"""Tests for Workbench URL handling."""

import pytest

from posit.workbench.urls import Url


class TestUrlCreation:
    """Tests for URL creation and validation."""

    def test_simple_url(self):
        """Test creation of a simple URL."""
        url = Url("https://workbench.example.com")
        assert str(url) == "https://workbench.example.com"

    def test_url_with_base_path(self):
        """Test creation of a URL with a base path."""
        url = Url("https://example.com/workbench")
        assert str(url) == "https://example.com/workbench"

    def test_trailing_slash_removed(self):
        """Test that trailing slashes are removed."""
        url = Url("https://example.com/")
        assert str(url) == "https://example.com"

        url = Url("https://example.com/workbench/")
        assert str(url) == "https://example.com/workbench"

    def test_missing_scheme_raises(self):
        """Test that URLs without a scheme raise ValueError."""
        with pytest.raises(ValueError, match="must specify a scheme"):
            Url("example.com")

    def test_missing_netloc_raises(self):
        """Test that relative URLs raise ValueError."""
        with pytest.raises(ValueError, match="must specify a scheme"):
            Url("/path/to/resource")


class TestUrlAppend:
    """Tests for URL path appending."""

    def test_append_to_simple_url(self):
        """Test appending a path to a simple URL."""
        url = Url("https://workbench.example.com")
        result = url.append("/oauth_token")
        assert str(result) == "https://workbench.example.com/oauth_token"

    def test_append_preserves_base_path(self):
        """Test that appending preserves base paths."""
        url = Url("https://example.com/workbench")
        result = url.append("/oauth_token")
        assert str(result) == "https://example.com/workbench/oauth_token"

    def test_append_strips_leading_slash(self):
        """Test that leading slashes in path are handled correctly."""
        url = Url("https://example.com")
        result1 = url.append("/oauth_token")
        result2 = url.append("oauth_token")
        assert str(result1) == str(result2) == "https://example.com/oauth_token"

    def test_append_strips_trailing_slash(self):
        """Test that trailing slashes in path are handled correctly."""
        url = Url("https://example.com")
        result1 = url.append("oauth_token/")
        result2 = url.append("oauth_token")
        assert str(result1) == str(result2) == "https://example.com/oauth_token"

    def test_add_operator(self):
        """Test that the + operator works for appending."""
        url = Url("https://example.com")
        result = url + "/oauth_token"
        assert str(result) == "https://example.com/oauth_token"

    def test_multiple_appends(self):
        """Test chaining multiple appends."""
        url = Url("https://example.com/api")
        result = url.append("v1").append("oauth").append("token")
        assert str(result) == "https://example.com/api/v1/oauth/token"

    def test_append_with_query_params(self):
        """Test that query parameters are preserved."""
        url = Url("https://example.com?param=value")
        result = url.append("/path")
        assert str(result) == "https://example.com/path?param=value"


class TestUrlEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_url_with_port(self):
        """Test URL with a port number."""
        url = Url("https://example.com:8080/workbench")
        result = url.append("/oauth_token")
        assert str(result) == "https://example.com:8080/workbench/oauth_token"

    def test_empty_path_append(self):
        """Test appending an empty path."""
        url = Url("https://example.com")
        result = url.append("")
        assert str(result) == "https://example.com"

    def test_url_is_string_subclass(self):
        """Test that Url is a string subclass."""
        url = Url("https://example.com")
        assert isinstance(url, str)


class TestTrailingSlashResistance:
    """Tests that URL handling is resistant to trailing slash variations in server URL.

    This is important because RS_SERVER_ADDRESS is user-defined and we want to be
    forgiving of whether users include trailing slashes or not.
    """

    def test_with_trailing_slash(self):
        """Test that server URL with trailing slash works correctly."""
        url = Url("https://workbench.example.com/")
        result = url.append("/oauth_token")
        assert str(result) == "https://workbench.example.com/oauth_token"

    def test_without_trailing_slash(self):
        """Test that server URL without trailing slash works correctly."""
        url = Url("https://workbench.example.com")
        result = url.append("/oauth_token")
        assert str(result) == "https://workbench.example.com/oauth_token"

    def test_both_produce_same_result(self):
        """Test that trailing slash presence doesn't affect the final URL."""
        url_with_slash = Url("https://workbench.example.com/")
        url_without_slash = Url("https://workbench.example.com")

        result_with = url_with_slash.append("/oauth_token")
        result_without = url_without_slash.append("/oauth_token")

        assert str(result_with) == str(result_without)

    def test_base_path_with_trailing_slash(self):
        """Test that base path with trailing slash works correctly."""
        url = Url("https://example.com/workbench/")
        result = url.append("/oauth_token")
        assert str(result) == "https://example.com/workbench/oauth_token"

    def test_base_path_without_trailing_slash(self):
        """Test that base path without trailing slash works correctly."""
        url = Url("https://example.com/workbench")
        result = url.append("/oauth_token")
        assert str(result) == "https://example.com/workbench/oauth_token"

    def test_base_path_both_produce_same_result(self):
        """Test that base path trailing slash doesn't affect the final URL."""
        url_with_slash = Url("https://example.com/workbench/")
        url_without_slash = Url("https://example.com/workbench")

        result_with = url_with_slash.append("/oauth_token")
        result_without = url_without_slash.append("/oauth_token")

        assert str(result_with) == str(result_without)
