import base64
from unittest.mock import patch

import pytest
import responses
from typing_extensions import Dict

from posit.connect import Client
from posit.connect.external.databricks import (
    POSIT_OAUTH_INTEGRATION_AUTH_TYPE,
    CredentialsProvider,
    CredentialsStrategy,
    PositContentCredentialsProvider,
    PositContentCredentialsStrategy,
    PositCredentialsProvider,
    PositCredentialsStrategy,
    PositLocalContentCredentialsProvider,
    PositLocalContentCredentialsStrategy,
    _get_auth_type,
    _new_bearer_authorization_header,
)
from posit.connect.oauth import Credentials


class mock_strategy(CredentialsStrategy):
    def auth_type(self) -> str:
        return "local"

    def __call__(self) -> CredentialsProvider:
        def inner() -> Dict[str, str]:
            return {"Authorization": "Bearer static-pat-token"}

        return inner


def register_mocks():
    responses.post(
        "https://connect.example/__api__/v1/oauth/integrations/credentials",
        match=[
            responses.matchers.urlencoded_params_matcher(
                {
                    "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                    "subject_token_type": "urn:posit:connect:user-session-token",
                    "subject_token": "cit",
                },
            ),
        ],
        json={
            "access_token": "dynamic-viewer-access-token",
            "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "token_type": "Bearer",
        },
    )

    responses.post(
        "https://connect.example/__api__/v1/oauth/integrations/credentials",
        match=[
            responses.matchers.urlencoded_params_matcher(
                {
                    "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                    "subject_token_type": "urn:posit:connect:content-session-token",
                    "subject_token": "cit",
                },
            ),
        ],
        json={
            "access_token": "content-access-token",
            "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
            "token_type": "Bearer",
        },
    )


class TestPositCredentialsHelpers:
    def test_new_bearer_authorization_header(self):
        credential = Credentials()
        credential["token_type"] = "token_type"
        credential["issued_token_type"] = "issued_token_type"

        with pytest.raises(ValueError):
            _new_bearer_authorization_header(credential)

        credential["access_token"] = "access_token"
        result = _new_bearer_authorization_header(credential)
        assert result == {"Authorization": "Bearer access_token"}

    def test_get_auth_type_local(self):
        assert _get_auth_type("local-auth") == "local-auth"

    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_get_auth_type_connect(self):
        assert _get_auth_type("local-auth") == POSIT_OAUTH_INTEGRATION_AUTH_TYPE

    @responses.activate
    def test_local_content_credentials_provider(self):
        token_url = "https://my-token/url"
        client_id = "client_id"
        client_secret = "client_secret_123"
        basic_auth = f"{client_id}:{client_secret}"
        b64_basic_auth = base64.b64encode(basic_auth.encode("utf-8")).decode("utf-8")

        responses.post(
            token_url,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "client_credentials",
                        "scope": "all-apis",
                    },
                ),
                responses.matchers.header_matcher({"Authorization": f"Basic {b64_basic_auth}"}),
            ],
            json={
                "access_token": "oauth2-m2m-access-token",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        cp = PositLocalContentCredentialsProvider(token_url, client_id, client_secret)
        assert cp() == {"Authorization": "Bearer oauth2-m2m-access-token"}

    @patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN": "cit"})
    @responses.activate
    def test_posit_content_credentials_provider(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        cp = PositContentCredentialsProvider(client=client)
        assert cp() == {"Authorization": "Bearer content-access-token"}

    @responses.activate
    def test_posit_credentials_provider(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        cp = PositCredentialsProvider(client=client, user_session_token="cit")
        assert cp() == {"Authorization": "Bearer dynamic-viewer-access-token"}

    @responses.activate
    def test_local_content_credentials_strategy(self):
        token_url = "https://my-token/url"
        client_id = "client_id"
        client_secret = "client_secret_123"
        basic_auth = f"{client_id}:{client_secret}"
        b64_basic_auth = base64.b64encode(basic_auth.encode("utf-8")).decode("utf-8")

        responses.post(
            token_url,
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "client_credentials",
                        "scope": "all-apis",
                    },
                ),
                responses.matchers.header_matcher({"Authorization": f"Basic {b64_basic_auth}"}),
            ],
            json={
                "access_token": "oauth2-m2m-access-token",
                "token_type": "Bearer",
                "expires_in": 3600,
            },
        )

        cs = PositLocalContentCredentialsStrategy(
            token_url,
            client_id,
            client_secret,
        )
        cp = cs()
        assert cs.auth_type() == "posit-local-client-credentials"
        assert cp() == {"Authorization": "Bearer oauth2-m2m-access-token"}

    @patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN": "cit"})
    @responses.activate
    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_posit_content_credentials_strategy(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        cs = PositContentCredentialsStrategy(
            local_strategy=mock_strategy(),
            client=client,
        )
        cp = cs()
        assert cs.auth_type() == "posit-oauth-integration"
        assert cp() == {"Authorization": "Bearer content-access-token"}

    @responses.activate
    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_posit_credentials_strategy(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        cs = PositCredentialsStrategy(
            local_strategy=mock_strategy(),
            user_session_token="cit",
            client=client,
        )
        cp = cs()
        assert cs.auth_type() == "posit-oauth-integration"
        assert cp() == {"Authorization": "Bearer dynamic-viewer-access-token"}

    def test_posit_content_credentials_strategy_fallback(self):
        # local_strategy is used when the content is running locally
        client = Client(api_key="12345", url="https://connect.example/")
        cs = PositContentCredentialsStrategy(
            local_strategy=mock_strategy(),
            client=client,
        )
        cp = cs()
        assert cs.auth_type() == "local"
        assert cp() == {"Authorization": "Bearer static-pat-token"}

    def test_posit_credentials_strategy_fallback(self):
        # local_strategy is used when the content is running locally
        client = Client(api_key="12345", url="https://connect.example/")
        cs = PositCredentialsStrategy(
            local_strategy=mock_strategy(),
            user_session_token="cit",
            client=client,
        )
        cp = cs()
        assert cs.auth_type() == "local"
        assert cp() == {"Authorization": "Bearer static-pat-token"}
