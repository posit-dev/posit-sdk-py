from unittest.mock import MagicMock, Mock, patch

from posit.connect.auth import Auth


class TestAuth:
    @patch("posit.connect.auth.Config")
    def test_auth_headers(self, Config: MagicMock):
        api_key = "foobar"
        auth = Auth(api_key)
        r = Mock()
        r.headers = {}
        auth(r)
        assert r.headers == {"Authorization": f"Key {api_key}"}
