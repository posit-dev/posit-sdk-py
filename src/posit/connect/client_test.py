from unittest.mock import MagicMock, patch
import pytest

from .client import Client


@pytest.fixture
def MockAuth():
    with patch("posit.connect.client.Auth") as mock:
        yield mock


@pytest.fixture
def MockConfig():
    with patch("posit.connect.client.Config") as mock:
        yield mock


@pytest.fixture
def MockSession():
    with patch("posit.connect.client.Session") as mock:
        yield mock


@pytest.fixture
def MockUsers():
    with patch("posit.connect.client.Users") as mock:
        yield mock


class TestClient:
    def test_init(
        self,
        MockAuth: MagicMock,
        MockConfig: MagicMock,
        MockSession: MagicMock,
        MockUsers: MagicMock,
    ):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        Client(api_key=api_key, url=url)
        MockAuth.assert_called_once_with(config=MockConfig.return_value)
        MockConfig.assert_called_once_with(api_key=api_key, url=url)
        MockSession.assert_called_once()

    def test_users(
        self,
        MockUsers: MagicMock,
    ):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        client.users
        MockUsers.assert_called_once_with(client=client)

    @patch("posit.connect.client.Session")
    @patch("posit.connect.client.User")
    def test_me(
        self,
        User: MagicMock,
        Session: MagicMock,
    ):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        User.assert_not_called()
        assert client._current_user is None
        client.me
        User.assert_called_once()

    def test__del__(self, MockAuth, MockConfig, MockSession, MockUsers):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        del client
        MockSession.return_value.close.assert_called_once()

    def test__enter__(self):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        with Client(api_key=api_key, url=url) as client:
            assert isinstance(client, Client)

    def test__exit__(self, MockSession):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        with Client(api_key=api_key, url=url) as client:
            assert isinstance(client, Client)
        MockSession.return_value.close.assert_called_once()

    def test_request(self, MockSession):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        client.request("GET", "/foo")
        MockSession.return_value.request.assert_called_once_with(
            "GET", "http://foo.bar/__api__/foo"
        )

    def test_get(self, MockSession):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        client.get("/foo")
        client.session.get.assert_called_once_with("http://foo.bar/__api__/foo")

    def test_post(self, MockSession):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        client.post("/foo")
        client.session.post.assert_called_once_with("http://foo.bar/__api__/foo")

    def test_put(self, MockSession):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        client.put("/foo")
        client.session.put.assert_called_once_with("http://foo.bar/__api__/foo")

    def test_patch(self, MockSession):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        client.patch("/foo")
        client.session.patch.assert_called_once_with("http://foo.bar/__api__/foo")

    def test_delete(self, MockSession):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)
        client.delete("/foo")
