from unittest.mock import Mock

from .auth import Auth


class TestAuth:
    def test_auth_headers(self):
        key = "foobar"
        auth = Auth(key=key)
        r = Mock()
        r.headers = {}
        auth(r)
        assert r.headers == {"Authorization": f"Key {key}"}
