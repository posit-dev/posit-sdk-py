import responses

from unittest import mock

from posit.connect import Client

from .api import load_mock  # type: ignore


class TestClient:
    def test__del__(self):
        api_key = "12345"
        url = "https://connect.example/__api__"
        client = Client(api_key, url)
        session = mock.Mock()
        client.ctx.session = session
        del client
        session.close.assert_called_once

    def test__enter__(self):
        api_key = "12345"
        url = "https://connect.example/__api__"
        with Client(api_key, url) as client:
            assert isinstance(client, Client)

    def test__exit__(self):
        api_key = "12345"
        url = "https://connect.example/__api__"
        session = mock.Mock()
        with Client(api_key, url) as client:
            client.ctx.session = session
        session.close.assert_called_once()

    @responses.activate
    def test_connect_version(self):
        api_key = "12345"
        url = "https://connect.example/__api__"
        client = Client(api_key, url)

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

    @responses.activate
    def test_request(self):
        mock = responses.get("https://connect.example/__api__/foo")
        api_key = "12345"
        url = "https://connect.example/__api__"
        client = Client(api_key, url)
        client.request("GET", "/foo")
        assert mock.call_count == 1

    @responses.activate
    def test_get(self):
        mock = responses.get("https://connect.example/__api__/foo")
        api_key = "12345"
        url = "https://connect.example/__api__"
        client = Client(api_key, url)
        client.get("/foo")
        assert mock.call_count == 1

    @responses.activate
    def test_post(self):
        mock = responses.post("https://connect.example/__api__/foo")
        api_key = "12345"
        url = "https://connect.example/__api__"
        client = Client(api_key, url)
        client.post("/foo")
        assert mock.call_count == 1

    @responses.activate
    def test_put(self):
        mock = responses.put("https://connect.example/__api__/foo")
        api_key = "12345"
        url = "https://connect.example/__api__"
        client = Client(api_key, url)
        client.put("/foo")
        assert mock.call_count == 1

    @responses.activate
    def test_patch(self):
        mock = responses.patch("https://connect.example/__api__/foo")
        api_key = "12345"
        url = "https://connect.example/__api__"
        client = Client(api_key, url)
        client.patch("/foo")
        assert mock.call_count == 1

    @responses.activate
    def test_delete(self):
        mock = responses.delete("https://connect.example/__api__/foo")
        api_key = "12345"
        url = "https://connect.example/__api__"
        client = Client(api_key, url)
        client.delete("/foo")
        assert mock.call_count == 1
