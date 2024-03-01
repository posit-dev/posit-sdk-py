import pytest
import responses

from unittest.mock import MagicMock, patch

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


class TestClient:
    def test_init(
        self,
        MockAuth: MagicMock,
        MockConfig: MagicMock,
        MockSession: MagicMock,
    ):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        Client(api_key=api_key, url=url)
        MockAuth.assert_called_once_with(config=MockConfig.return_value)
        MockConfig.assert_called_once_with(api_key=api_key, url=url)
        MockSession.assert_called_once()

    def test__del__(self, MockAuth, MockConfig, MockSession):
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

    @responses.activate
    def test_connect_version(self):
        api_key = "foobar"
        url = "http://foo.bar/__api__"
        client = Client(api_key=api_key, url=url)

        # The actual server_settings response has a lot more attributes, but we
        # don't need to include them all here because we don't use them
        responses.get(
            "http://foo.bar/__api__/server_settings",
            json={"version": "2024.01.0"},
        )
        assert client.connect_version == "2024.01.0"

    @responses.activate
    def test_me_request(self):
        responses.get(
            "https://connect.example/__api__/v1/user",
            json={
                "email": "carlos@connect.example",
                "username": "carlos12",
                "first_name": "Carlos",
                "last_name": "User",
                "user_role": "publisher",
                "created_time": "2019-09-09T15:24:32Z",
                "updated_time": "2022-03-02T20:25:06Z",
                "active_time": "2020-05-11T16:58:45Z",
                "confirmed": True,
                "locked": False,
                "guid": "20a79ce3-6e87-4522-9faf-be24228800a4",
            },
        )

        con = Client(api_key="12345", url="https://connect.example/")
        assert con.me["username"] == "carlos12"

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
