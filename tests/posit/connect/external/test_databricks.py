from typing import Dict
from unittest.mock import patch

import responses

from posit.connect import Client
from posit.connect.external.databricks import (
    CredentialsProvider,
    CredentialsStrategy,
    PositCredentialsProvider,
    PositCredentialsStrategy,
)


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


class TestPositCredentialsHelpers:
    @responses.activate
    def test_posit_credentials_provider(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        cp = PositCredentialsProvider(client=client, user_session_token="cit")
        assert cp() == {"Authorization": "Bearer dynamic-viewer-access-token"}

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
