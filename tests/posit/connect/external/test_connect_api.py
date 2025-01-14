from unittest.mock import patch

import responses

from posit.connect import Client
from posit.connect.external.connect_api import ViewerConnectClientProvider


def register_mocks():
    responses.post(
        "https://connect.example/__api__/v1/oauth/integrations/credentials",
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
            "access_token": "viewer-api-key",
            "issued_token_type": "urn:posit:connect:api-key",
            "token_type": "Key",
        },
    )


class TestConnectAPIKeyProvider:
    @responses.activate
    @patch.dict(
        "os.environ",
        {
            "RSTUDIO_PRODUCT": "CONNECT",
            "CONNECT_SERVER": "https://connect.example/",
            "CONNECT_API_KEY": "12345",
        },
    )
    def test_provider(self):
        register_mocks()

        provider = ViewerConnectClientProvider(
            user_session_token="cit",
        )
        provider._client._ctx.version = None
        viewer_client = provider.get_client()
        assert viewer_client is not None
        assert viewer_client.cfg.url == "https://connect.example/__api__"
        assert viewer_client.cfg.api_key == "viewer-api-key"

    @responses.activate
    @patch.dict(
        "os.environ",
        {
            "RSTUDIO_PRODUCT": "CONNECT",
            "CONNECT_SERVER": "https://connect.example/",
            "CONNECT_API_KEY": "12345",
        },
    )
    def test_provider_with_url_override(self):
        register_mocks()

        provider = ViewerConnectClientProvider(
            user_session_token="cit",
            url_override="https://connect2.example/",
        )
        provider._client._ctx.version = None
        viewer_client = provider.get_client()
        assert viewer_client is not None
        assert viewer_client.cfg.url == "https://connect2.example/__api__"
        assert viewer_client.cfg.api_key == "viewer-api-key"

    @responses.activate
    @patch.dict(
        "os.environ", {"RSTUDIO_PRODUCT": "CONNECT", "CONNECT_SERVER": "https://connect.example/"}
    )
    def test_provider_with_client_override(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        provider = ViewerConnectClientProvider(
            user_session_token="cit",
            client_override=client,
        )
        viewer_client = provider.get_client()
        assert viewer_client is not None
        assert viewer_client.cfg.url == "https://connect.example/__api__"
        assert viewer_client.cfg.api_key == "viewer-api-key"

    @patch.dict(
        "os.environ", {"CONNECT_SERVER": "https://connect.example/", "CONNECT_API_KEY": "12345"}
    )
    def test_provider_fallback(self):
        # default client is used when the content is running locally
        provider = ViewerConnectClientProvider(
            user_session_token="cit",
        )
        provider._client._ctx.version = None
        viewer_client = provider.get_client()
        assert viewer_client.cfg.url == "https://connect.example/__api__"
        assert viewer_client.cfg.api_key == "12345"

    def test_provider_fallback_with_client_override(self):
        # provided client is used when the content is running locally
        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        provider = ViewerConnectClientProvider(
            user_session_token="cit",
            client_override=client,
        )
        viewer_client = provider.get_client()
        assert viewer_client.cfg.url == "https://connect.example/__api__"
        assert viewer_client.cfg.api_key == "12345"
