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
        client = Client(api_key=api_key, endpoint=endpoint)
        config = Config.return_value
        Auth.assert_called_once_with(config=config)
        Config.assert_called_once_with(api_key=api_key, endpoint=endpoint)
        Session.assert_called_once()

        # API resources are lazy; assert that they aren't initialized until
        # they are referenced for the first time
        Users.assert_not_called()
        client.users
        Users.assert_called_once_with(client=client)


    @patch("posit.connect.client.Session")
    @patch("posit.connect.client.Auth")
    def test_del(self, Auth: MagicMock, Session: MagicMock):
        api_key = "foobar"
        endpoint = "http://foo.bar"
        client = Client(api_key=api_key, endpoint=endpoint)
        del client
        Session.return_value.close.assert_called_once()
