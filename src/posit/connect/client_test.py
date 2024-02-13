from unittest.mock import MagicMock, patch

from .client import Client, create_client


class TestCreateClient:
    @patch("posit.connect.client.Client")
    def test(self, Client: MagicMock):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        with create_client(api_key=api_key, endpoint=endpoint) as client:
            assert client == Client.return_value


class TestClient:
    @patch("posit.connect.client.LazyUsers")
    @patch("posit.connect.client.Session")
    @patch("posit.connect.client.Config")
    @patch("posit.connect.client.Auth")
    def test_init(
        self,
        Auth: MagicMock,
        Config: MagicMock,
        Session: MagicMock,
        LazyUsers: MagicMock,
    ):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        Client(api_key=api_key, endpoint=endpoint)
        config = Config.return_value
        Auth.assert_called_once_with(config=config)
        Config.assert_called_once_with(api_key=api_key, endpoint=endpoint)
        Session.assert_called_once()
        LazyUsers.assert_called_once_with(config=config, session=Session.return_value)

    @patch("posit.connect.client.Session")
    @patch("posit.connect.client.Config")
    @patch("posit.connect.client.Auth")
    def test_del(self, Auth: MagicMock, Session: MagicMock):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        client = Client(api_key=api_key, endpoint=endpoint)
        del client
        Session.return_value.close.assert_called_once()
