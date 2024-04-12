from unittest import mock

from posit.connect import auth, config


class TestAuth:
    def test_auth_headers(self):
        c = config.Config()
        c.api_key = "12345"
        r = mock.Mock()
        r.headers = {}
        a = auth.Auth()
        a(r)
        assert r.headers == {"Authorization": f"Key {c.api_key}"}
