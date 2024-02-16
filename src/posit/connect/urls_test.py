import pytest
import unittest

from .urls import Url


class TestUrl(unittest.TestCase):
    def test_init_with_valid_url(self):
        url = Url("http://foo.bar")
        self.assertEqual(url.url, "http://foo.bar/__api__")

    def test_init_with_api_url(self):
        url = Url("http://foo.bar/__api__")
        self.assertEqual(url.url, "http://foo.bar/__api__")

    def test_init_with_invalid_url(self):
        with pytest.raises(ValueError):
            Url("foobar")

    def test_append_with_valid_url(self):
        url = Url("http://foo.bar")
        self.assertEqual(url.append("path"), "http://foo.bar/__api__/path")

    def test_append_with_api_url(self):
        url = Url("http://foo.bar/__api__")
        self.assertEqual(url.append("path"), "http://foo.bar/__api__/path")

    def test_append_with_empty_path(self):
        url = Url("http://foo.bar")
        self.assertEqual(url.append(""), "http://foo.bar/__api__")

    def test_append_with_invalid_url(self):
        url = Url("http://foo.bar")
        with pytest.raises(ValueError):
            url.append("http://foo.bar")
