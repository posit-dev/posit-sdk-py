from unittest.mock import MagicMock, patch

from .client import Client


class TestClient:
    @patch("posit.connect.client.Users")
    @patch("posit.connect.client.Session")
    @patch("posit.connect.client.Config")
    @patch("posit.connect.client.Auth")
    def test_init(
        self,
        Auth: MagicMock,
        Config: MagicMock,
        Session: MagicMock,
        Users: MagicMock,
    ):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        Client(api_key=api_key, endpoint=endpoint)
        config = Config.return_value
        Auth.assert_called_once_with(config=config)
        Config.assert_called_once_with(api_key=api_key, endpoint=endpoint)
        Session.assert_called_once()
        Users.assert_called_once_with(config=config, session=Session.return_value)

    @patch("posit.connect.client.Session")
    @patch("posit.connect.client.Auth")
    def test_del(self, Auth: MagicMock, Session: MagicMock):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        client = Client(api_key=api_key, endpoint=endpoint)
        del client
        Session.return_value.close.assert_called_once()

    @patch("posit.connect.client.Session")
    @patch("posit.connect.client.Auth")
    def test_context_manager(self, Auth: MagicMock, Session: MagicMock):
        # What is this testing?
        api_key = "foobar"
        endpoint = "http://foo.bar"
        with Client(api_key=api_key, endpoint=endpoint) as client:
            assert isinstance(client, Client)
        Session.return_value.close.assert_called_once()
