from unittest.mock import MagicMock, Mock, patch

from posit.connect.auth import Auth, BootstrapAuth


class TestAuth:
    @patch("posit.connect.auth.Config")
    def test_auth_headers(self, Config: MagicMock):
        config = Config.return_value
        config.api_key = "foobar"
        auth = Auth(config=config)
        r = Mock()
        r.headers = {}
        auth(r)
        assert r.headers == {"Authorization": f"Key {config.api_key}"}


class TestBootstrapAuth:
    def test_auth_headers(self):
        token = "my-bootstrap-jwt"
        auth = BootstrapAuth(token=token)
        r = Mock()
        r.headers = {}
        auth(r)
        assert r.headers == {"Authorization": f"Connect-Bootstrap {token}"}

    def test_repr_does_not_leak_token(self):
        auth = BootstrapAuth(token="SEKRET")
        assert "SEKRET" not in repr(auth)
        assert "SEKRET" not in str(auth)
        assert repr(auth) == "BootstrapAuth(token=***)"

    def test_repr_in_format_string_does_not_leak_token(self):
        auth = BootstrapAuth(token="SEKRET")
        assert "SEKRET" not in f"{auth}"
        assert "SEKRET" not in f"{auth!r}"
