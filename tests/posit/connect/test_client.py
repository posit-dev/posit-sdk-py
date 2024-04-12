import pytest
import responses

from unittest.mock import MagicMock, patch

from posit.connect import Client

from .api import load_mock  # type: ignore


@pytest.fixture
def MockAuth():
    with patch("posit.connect.client.Auth") as mock:
        yield mock


@pytest.fixture
def MockConfig():
    with patch("posit.connect.client.config.Config") as mock:
        yield mock


@pytest.fixture
def MockSession():
    with patch("posit.connect.client.Session") as mock:
        yield mock


class TestClient:
    def test__del__(self, MockAuth, MockConfig, MockSession):
        client = Client()
        del client
        MockSession.return_value.close.assert_called_once()

    def test__enter__(self):
        with Client() as client:
            assert isinstance(client, Client)

    def test__exit__(self, MockSession):
        with Client() as client:
            assert isinstance(client, Client)
        MockSession.return_value.close.assert_called_once()

    @responses.activate
    def test_connect_version(self):
        client = Client()

        # The actual server_settings response has a lot more attributes, but we
        # don't need to include them all here because we don't use them
        responses.get(
            "https://connect.example/__api__/server_settings",
            json={"version": "2024.01.0"},
        )
        assert client.connect_version == "2024.01.0"

    @responses.activate
    def test_me_request(self):
        responses.get(
            "https://connect.example/__api__/v1/user",
            json=load_mock("v1/user.json"),
        )

        con = Client(api_key="12345", url="https://connect.example/")
        assert con.me.username == "carlos12"

    def test_request(self, MockSession):
        client = Client()
        client.request("GET", "/foo")
        MockSession.return_value.request.assert_called_once_with(
            "GET", "https://connect.example/__api__/foo"
        )

    def test_get(self, MockSession):
        client = Client()
        client.get("/foo")
        client.session.get.assert_called_once_with(
            "https://connect.example/__api__/foo"
        )

    def test_post(self, MockSession):
        client = Client()
        client.post("/foo")
        client.session.post.assert_called_once_with(
            "https://connect.example/__api__/foo"
        )

    def test_put(self, MockSession):
        client = Client()
        client.put("/foo")
        client.session.put.assert_called_once_with(
            "https://connect.example/__api__/foo"
        )

    def test_patch(self, MockSession):
        client = Client()
        client.patch("/foo")
        client.session.patch.assert_called_once_with(
            "https://connect.example/__api__/foo"
        )

    def test_delete(self, MockSession):
        client = Client()
        client.delete("/foo")
