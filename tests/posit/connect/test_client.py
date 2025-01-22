# pyright: reportFunctionMemberAccess=false
from unittest.mock import MagicMock, patch

import pytest
import responses

from posit.connect import Client

from .api import load_mock


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


class TestClientInit:
    def test_no_arguments(
        self,
        MockAuth: MagicMock,
        MockConfig: MagicMock,
        MockSession: MagicMock,
    ):
        Client()
        MockConfig.assert_called_once_with(api_key=None, url=None)

    def test_one_argument(
        self,
        MockAuth: MagicMock,
        MockConfig: MagicMock,
        MockSession: MagicMock,
    ):
        url = "https://connect.example.com"
        Client(url)
        MockConfig.assert_called_once_with(api_key=None, url=url)

    def test_two_arguments(
        self,
        MockAuth: MagicMock,
        MockConfig: MagicMock,
        MockSession: MagicMock,
    ):
        url = "https://connect.example.com"
        api_key = "12345"
        Client(url, api_key)
        MockConfig.assert_called_once_with(api_key=api_key, url=url)

    def test_keyword_arguments(
        self,
        MockAuth: MagicMock,
        MockConfig: MagicMock,
        MockSession: MagicMock,
    ):
        url = "https://connect.example.com"
        api_key = "12345"
        Client(api_key=api_key, url=url)
        MockConfig.assert_called_once_with(api_key=api_key, url=url)


class TestClient:
    def test_init(
        self,
        MockAuth: MagicMock,
        MockConfig: MagicMock,
        MockSession: MagicMock,
    ):
        api_key = "12345"
        url = "https://connect.example.com"
        Client(api_key=api_key, url=url)
        MockAuth.assert_called_once_with(config=MockConfig.return_value)
        MockConfig.assert_called_once_with(api_key=api_key, url=url)
        MockSession.assert_called_once()

    @responses.activate
    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_with_user_session_token(self):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client._ctx.version = None

        responses.post(
            "https://connect.example.com/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:user-session-token",
                        "subject_token": "cit",
                        "requested_token_type": "urn:posit:connect:api-key",
                    },
                ),
            ],
            json={
                "access_token": "api-key",
                "issued_token_type": "urn:posit:connect:api-key",
                "token_type": "Key",
            },
        )

        visitor_client = client.with_user_session_token("cit")

        assert visitor_client.cfg.url == "https://connect.example.com/__api__"
        assert visitor_client.cfg.api_key == "api-key"

    @responses.activate
    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_with_user_session_token_bad_exchange_response_body(self):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client._ctx.version = None

        responses.post(
            "https://connect.example.com/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:user-session-token",
                        "subject_token": "cit",
                        "requested_token_type": "urn:posit:connect:api-key",
                    },
                ),
            ],
            json={},
        )

        with pytest.raises(ValueError) as err:
            client.with_user_session_token("cit")
        assert str(err.value) == "Unable to retrieve token."

    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_with_user_session_token_bad_token_deployed(self):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client._ctx.version = None

        with pytest.raises(ValueError) as err:
            client.with_user_session_token("")
        assert str(err.value) == "token must be set to non-empty string."

    def test_with_user_session_token_bad_token_local(self):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client._ctx.version = None

        with pytest.raises(ValueError) as e:
            client.with_user_session_token("")
        assert str(e.value) == "token must be set to non-empty string."

        with pytest.raises(ValueError) as e:
            client.with_user_session_token(None)  # type: ignore
        assert str(e.value) == "token must be set to non-empty string."

    def test__del__(
        self,
        MockAuth: MagicMock,
        MockConfig: MagicMock,
        MockSession: MagicMock,
    ):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        del client
        MockSession.return_value.close.assert_called_once()

    def test__enter__(self):
        api_key = "12345"
        url = "https://connect.example.com"
        with Client(api_key=api_key, url=url) as client:
            assert isinstance(client, Client)

    def test__exit__(self, MockSession):
        api_key = "12345"
        url = "https://connect.example.com"
        api_key = "12345"
        url = "https://connect.example.com"
        with Client(api_key=api_key, url=url) as client:
            assert isinstance(client, Client)
        MockSession.return_value.close.assert_called_once()

    @responses.activate
    def test_connect_version(self):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)

        # The actual server_settings response has a lot more attributes, but we
        # don't need to include them all here because we don't use them
        responses.get(
            "https://connect.example.com/__api__/server_settings",
            json={"version": "2024.01.0"},
        )
        assert client.version == "2024.01.0"

    @responses.activate
    def test_me_request(self):
        responses.get(
            "https://connect.example/__api__/v1/user",
            json=load_mock("v1/user.json"),
        )

        con = Client(api_key="12345", url="https://connect.example/")
        assert con.me["username"] == "carlos12"

    def test_request(self, MockSession):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client.request("GET", "/foo")
        MockSession.return_value.request.assert_called_once_with(
            "GET",
            "https://connect.example.com/__api__/foo",
        )

    def test_get(self, MockSession):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client.get("/foo")
        client.session.get.assert_called_once_with("https://connect.example.com/__api__/foo")

    def test_post(self, MockSession):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client.post("/foo")
        client.session.post.assert_called_once_with("https://connect.example.com/__api__/foo")

    def test_put(self, MockSession):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client.put("/foo")
        client.session.put.assert_called_once_with("https://connect.example.com/__api__/foo")

    def test_patch(self, MockSession):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client.patch("/foo")
        client.session.patch.assert_called_once_with("https://connect.example.com/__api__/foo")

    def test_delete(self, MockSession):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client.delete("/foo")
        client.session.delete.assert_called_once_with("https://connect.example.com/__api__/foo")


class TestClientOAuth:
    def test_required_version(self):
        api_key = "12345"
        url = "https://connect.example.com"
        client = Client(api_key=api_key, url=url)
        client._ctx.version = "2024.07.0"

        with pytest.raises(RuntimeError):
            client.oauth  # noqa: B018
