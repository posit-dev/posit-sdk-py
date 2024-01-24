from unittest.mock import MagicMock, Mock, patch

from .client import Client


class TestClient:
    @patch("posit.client.Session")
    @patch("posit.client.ConfigBuilder")
    @patch("posit.client.Auth")
    def test_init(self, Auth: MagicMock, ConfigBuilder: MagicMock, Session: MagicMock):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        config = Mock()
        config.api_key = api_key
        builder = ConfigBuilder.return_value
        builder.set_api_key = Mock()
        builder.set_endpoint = Mock()
        builder.build = Mock(return_value=config)
        client = Client(api_key=api_key, endpoint=endpoint)
        ConfigBuilder.assert_called_once()
        builder.set_api_key.assert_called_once_with(api_key)
        builder.set_endpoint.assert_called_once_with(endpoint)
        builder.build.assert_called_once()
        Session.assert_called_once()
        Auth.assert_called_once_with(api_key)
        assert client._config == config
