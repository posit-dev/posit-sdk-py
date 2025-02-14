from __future__ import annotations

from unittest.mock import patch

import pytest
import responses
from typing_extensions import Dict

from posit.connect import Client
from posit.connect.external.databricks import (
    POSIT_OAUTH_INTEGRATION_AUTH_TYPE,
    ConnectStrategy,
    _new_bearer_authorization_header,
    _PositConnectContentCredentialsProvider,
    _PositConnectViewerCredentialsProvider,
    databricks_config,
)
from posit.connect.oauth import Credentials

try:
    from databricks.sdk.core import Config, DefaultCredentials
    from databricks.sdk.credentials_provider import (
        CredentialsProvider,
        CredentialsStrategy,
    )

    # construct a DefaultCredentials CredentialsStrategy
    # weirdly, you have to call `__call__()` at least once in order to initialize `auth_type()`
    # This is the expected credentials strategy when none is provided to our databricks_config() helper
    expected_credentials = DefaultCredentials()  # pyright: ignore[reportPossiblyUnboundVariable]
    expected_credentials(Config(auth_type="pat", token="asdf", host="https://databricks.com/"))  # pyright: ignore[reportPossiblyUnboundVariable]

except ImportError:
    pytestmark = pytest.mark.skipif(True, reason="requires the Databricks SDK")


class mock_strategy(CredentialsStrategy):  # pyright: ignore[reportPossiblyUnboundVariable]
    def __init__(self, name: str):
        self.name = name

    def auth_type(self) -> str:
        return self.name

    def __call__(self, *args, **kwargs) -> CredentialsProvider:
        def inner() -> Dict[str, str]:
            return {"Authorization": f"Bearer {self.name}"}

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

    @patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN": "cit"})
    @responses.activate
    def test_posit_content_credentials_provider(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        cp = _PositConnectContentCredentialsProvider(client=client)
        assert cp() == {"Authorization": "Bearer content-access-token"}

    @responses.activate
    def test_posit_credentials_provider(self):
        register_mocks()

        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None
        cp = _PositConnectViewerCredentialsProvider(client=client, user_session_token="cit")
        assert cp() == {"Authorization": "Bearer dynamic-viewer-access-token"}

    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    @patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN": "cit"})
    @responses.activate
    def test_connect_strategy(self):
        register_mocks()
        client = Client(api_key="12345", url="https://connect.example/")
        client._ctx.version = None

        # the default implementation uses Service Account authentication
        cs = ConnectStrategy(client=client)
        assert cs.auth_type() == POSIT_OAUTH_INTEGRATION_AUTH_TYPE
        cp = cs()
        assert cp() == {"Authorization": "Bearer content-access-token"}

        # if a session token is provided then Viewer auth is used
        cs = ConnectStrategy(client=client, user_session_token="cit")
        cp = cs()
        assert cp() == {"Authorization": "Bearer dynamic-viewer-access-token"}

    def test_databricks_config(self):
        # credentials_strategy is removed if it is provided
        cfg = databricks_config(
            credentials_strategy=mock_strategy("mock"),
            auth_type="pat",
            token="asdf",
            host="https://databricks.com/",
        )
        assert cfg._credentials_strategy.auth_type() == expected_credentials.auth_type()

        # kwargs are passed through to the Config() constructor
        cfg = databricks_config(
            host="https://databricks.com",
            cluster_id="cluster_id",
            warehouse_id="warehouse_id",
            token="token",
        )
        assert cfg.host == "https://databricks.com"
        assert cfg.cluster_id == "cluster_id"
        assert cfg.warehouse_id == "warehouse_id"
        assert cfg.token == "token"

    def test_databricks_config_default(self):
        cfg = databricks_config(
            posit_default_strategy=mock_strategy("default"),
            posit_workbench_strategy=mock_strategy("workbench"),
            posit_connect_strategy=mock_strategy("connect"),
        )
        assert cfg._credentials_strategy.auth_type() == "default"

        # default fallback defaults to DefaultCredentials() when none is provided
        cfg = databricks_config(auth_type="pat", token="asdf", host="https://databricks.com/")
        assert cfg._credentials_strategy.auth_type() == expected_credentials.auth_type()

    @patch.dict("os.environ", {"RS_SERVER_ADDRESS": "https://workbench.posit.co/"})
    def test_databricks_config_workbench(self):
        cfg = databricks_config(
            posit_default_strategy=mock_strategy("default"),
            posit_workbench_strategy=mock_strategy("workbench"),
            posit_connect_strategy=mock_strategy("connect"),
        )
        assert cfg._credentials_strategy.auth_type() == "workbench"

        # workbench defaults to DefaultCredentials() when none is provided
        cfg = databricks_config(auth_type="pat", token="asdf", host="https://databricks.com/")
        assert cfg._credentials_strategy.auth_type() == expected_credentials.auth_type()

    @patch.dict("os.environ", {"CONNECT_API_KEY": "API_KEY"})
    @patch.dict("os.environ", {"CONNECT_SERVER": "https://connect.posit.co/"})
    @patch.dict("os.environ", {"RSTUDIO_PRODUCT": "CONNECT"})
    def test_databricks_config_connect(self):
        cfg = databricks_config(
            posit_default_strategy=mock_strategy("default"),
            posit_workbench_strategy=mock_strategy("workbench"),
            posit_connect_strategy=mock_strategy("connect"),
        )
        assert cfg._credentials_strategy.auth_type() == "connect"

        # connect defaults to ConnectStrategy() when none is provided
        cfg = databricks_config()
        assert cfg._credentials_strategy.auth_type() == ConnectStrategy().auth_type()
