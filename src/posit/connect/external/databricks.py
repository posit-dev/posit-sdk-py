"""Databricks SDK integration.

Databricks SDK credentials implementations which support interacting with Posit OAuth integrations on Connect.

Notes
-----
These APIs are provided as a convenience and are subject to breaking changes:
https://github.com/databricks/databricks-sdk-py#interface-stability
"""

import abc

import requests
from typing_extensions import Callable, Dict, Optional

from .._utils import is_local
from ..client import Client
from ..oauth import Credentials

POSIT_OAUTH_INTEGRATION_AUTH_TYPE = "posit-oauth-integration"
POSIT_LOCAL_CLIENT_CREDENTIALS_AUTH_TYPE = "posit-local-client-credentials"

# The Databricks SDK CredentialsProvider == Databricks SQL HeaderFactory
CredentialsProvider = Callable[[], Dict[str, str]]


class CredentialsStrategy(abc.ABC):
    """Maintain compatibility with the Databricks SQL/SDK client libraries.

    See Also
    --------
    * https://github.com/databricks/databricks-sql-python/blob/v3.3.0/src/databricks/sql/auth/authenticators.py#L19-L33
    * https://github.com/databricks/databricks-sdk-py/blob/v0.29.0/databricks/sdk/credentials_provider.py#L44-L54
    """

    @abc.abstractmethod
    def auth_type(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> CredentialsProvider:
        raise NotImplementedError


def _new_bearer_authorization_header(credentials: Credentials) -> Dict[str, str]:
    """Helper to transform an Credentials object into the Bearer auth header consumed by databricks.

    Raises
    ------
        ValueError: If provided Credentials object does not contain an access token

    Returns
    -------
        Dict[str, str]
    """
    access_token = credentials.get("access_token")
    if access_token is None:
        raise ValueError("Missing value for field 'access_token' in credentials.")
    return {"Authorization": f"Bearer {access_token}"}


def _get_auth_type(local_auth_type: str) -> str:
    """Returns the auth type currently in use.

    The databricks-sdk client uses the configured auth_type to create
    a user-agent string which is used for attribution. We should only
    overwrite the auth_type if we are using the PositCredentialsStrategy (non-local),
    otherwise, we should return the auth_type of the configured local_strategy instead
    to avoid breaking someone elses attribution.

    NOTE: The databricks-sql client does not use auth_type to set the user-agent.
    https://github.com/databricks/databricks-sql-python/blob/v3.3.0/src/databricks/sql/client.py#L214-L219

    See Also
    --------
    * https://github.com/databricks/databricks-sdk-py/blob/v0.29.0/databricks/sdk/config.py#L261-L269

    Returns
    -------
        str
    """
    if is_local():
        return local_auth_type

    return POSIT_OAUTH_INTEGRATION_AUTH_TYPE


class PositLocalContentCredentialsProvider:
    """`CredentialsProvider` implementation which provides a fallback for local development using a client credentials flow.

    There is an open issue against the Databricks CLI which prevents it from returning service principal access tokens.
    https://github.com/databricks/cli/issues/1939

    Until the CLI issue is resolved, this CredentialsProvider implements the approach described in the Databricks documentation
    for manually generating a workspace-level access token using OAuth M2M authentication. Once it has acquired an access token,
    it returns it as a Bearer authorization header like other `CredentialsProvider` implementations.

    See Also
    --------
    * https://docs.databricks.com/en/dev-tools/auth/oauth-m2m.html#manually-generate-a-workspace-level-access-token
    """

    def __init__(self, token_endpoint_url: str, client_id: str, client_secret: str):
        self._token_endpoint_url = token_endpoint_url
        self._client_id = client_id
        self._client_secret = client_secret

    def __call__(self) -> Dict[str, str]:
        response = requests.post(
            self._token_endpoint_url,
            auth=(self._client_id, self._client_secret),
            data={
                "grant_type": "client_credentials",
                "scope": "all-apis",
            },
        )
        response.raise_for_status()

        credentials = Credentials(**response.json())
        return _new_bearer_authorization_header(credentials)


class PositContentCredentialsProvider:
    """`CredentialsProvider` implementation which initiates a credential exchange using a content-session-token.

    The content-session-token is provided by Connect through the environment variable `CONNECT_CONTENT_SESSION_TOKEN`.

    See Also
    --------
    * https://github.com/posit-dev/posit-sdk-py/blob/main/src/posit/connect/oauth/oauth.py

    """

    def __init__(self, client: Client):
        self._client = client

    def __call__(self) -> Dict[str, str]:
        credentials = self._client.oauth.get_content_credentials()
        return _new_bearer_authorization_header(credentials)


class PositCredentialsProvider:
    """`CredentialsProvider` implementation which initiates a credential exchange using a user-session-token.

    The user-session-token is provided by Connect through the HTTP session header
    `Posit-Connect-User-Session-Token`.

    See Also
    --------
    * https://github.com/posit-dev/posit-sdk-py/blob/main/src/posit/connect/oauth/oauth.py

    """

    def __init__(self, client: Client, user_session_token: str):
        self._client = client
        self._user_session_token = user_session_token

    def __call__(self) -> Dict[str, str]:
        credentials = self._client.oauth.get_credentials(self._user_session_token)
        return _new_bearer_authorization_header(credentials)


class PositLocalContentCredentialsStrategy(CredentialsStrategy):
    """`CredentialsStrategy` implementation which supports local development using OAuth M2M authentication against Databricks.

    There is an open issue against the Databricks CLI which prevents it from returning service principal access tokens.
    https://github.com/databricks/cli/issues/1939

    Until the CLI issue is resolved, this CredentialsStrategy provides a drop-in replacement as a local_strategy that can be used
    to develop applications which target Service Account OAuth integrations on Connect.

    Examples
    --------
    In the example below, the `PositContentCredentialsStrategy` can be initialized anywhere that
    the Python process can read environment variables.

    CLIENT_ID and CLIENT_SECRET are credentials associated with the Databricks service principal.

    ```python
    from posit.connect.external.databricks import (
        PositContentCredentialsStrategy,
        PositLocalContentCredentialsStrategy,
    )

    import pandas as pd
    from databricks import sql
    from databricks.sdk.core import ApiClient, Config
    from databricks.sdk.service.iam import CurrentUserAPI

    DATABRICKS_HOST = "<REDACTED>"
    DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
    SQL_HTTP_PATH = "<REDACTED>"
    TOKEN_ENDPOINT_URL = f"https://{DATABRICKS_HOST}/oidc/v1/token"

    CLIENT_ID = "<REDACTED>"
    CLIENT_SECRET = "<REDACTED>"

    # Rather than relying on the Databricks CLI as a local strategy, we use
    # PositLocalContentCredentialsStrategy as a drop-in replacement.
    # Can be replaced with the Databricks CLI implementation when
    # https://github.com/databricks/cli/issues/1939 is resolved.
    local_strategy = PositLocalContentCredentialsStrategy(
        token_endpoint_url=TOKEN_ENDPOINT_URL,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    posit_strategy = PositContentCredentialsStrategy(local_strategy=local_strategy)

    cfg = Config(host=DATABRICKS_HOST_URL, credentials_strategy=posit_strategy)

    databricks_user_info = CurrentUserAPI(ApiClient(cfg)).me()
    print(f"Hello, {databricks_user_info.display_name}!")

    query = "SELECT * FROM samples.nyctaxi.trips LIMIT 10;"
    with sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=SQL_HTTP_PATH,
        credentials_provider=posit_strategy.sql_credentials_provider(cfg),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            print(pd.DataFrame([row.asDict() for row in rows]))
    ```

    See Also
    --------
    * https://docs.databricks.com/en/dev-tools/auth/oauth-m2m.html#manually-generate-a-workspace-level-access-token
    """

    def __init__(self, token_endpoint_url: str, client_id: str, client_secret: str):
        self._token_endpoint_url = token_endpoint_url
        self._client_id = client_id
        self._client_secret = client_secret

    def sql_credentials_provider(self, *args, **kwargs):
        return lambda: self.__call__(*args, **kwargs)

    def auth_type(self) -> str:
        return POSIT_LOCAL_CLIENT_CREDENTIALS_AUTH_TYPE

    def __call__(self, *args, **kwargs) -> CredentialsProvider:  # noqa: ARG002
        return PositLocalContentCredentialsProvider(
            self._token_endpoint_url,
            self._client_id,
            self._client_secret,
        )


class PositContentCredentialsStrategy(CredentialsStrategy):
    """`CredentialsStrategy` implementation which supports interacting with Service Account OAuth integrations on Connect.

    This strategy callable class returns a `PositContentCredentialsProvider` when hosted on Connect, and
    its `local_strategy` strategy otherwise.

    Examples
    --------
    NOTE: in the example below, the `PositContentCredentialsStrategy` can be initialized anywhere that
    the Python process can read environment variables.

    ```python
    from posit.connect.external.databricks import PositContentCredentialsStrategy

    import pandas as pd
    from databricks import sql
    from databricks.sdk.core import ApiClient, Config, databricks_cli
    from databricks.sdk.service.iam import CurrentUserAPI

    DATABRICKS_HOST = "<REDACTED>"
    DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
    SQL_HTTP_PATH = "<REDACTED>"

    # NOTE: currently the databricks_cli local strategy only supports auth code OAuth flows.
    # https://github.com/databricks/cli/issues/1939
    #
    # This means that the databricks_cli supports local development using the developer's
    # databricks credentials, but not the credentials for a service principal.
    # To fallback to service principal credentials in local development, use
    # `PositLocalContentCredentialsStrategy` as a drop-in replacement.
    posit_strategy = PositContentCredentialsStrategy(local_strategy=databricks_cli)

    cfg = Config(host=DATABRICKS_HOST_URL, credentials_strategy=posit_strategy)

    databricks_user_info = CurrentUserAPI(ApiClient(cfg)).me()
    print(f"Hello, {databricks_user_info.display_name}!")

    query = "SELECT * FROM samples.nyctaxi.trips LIMIT 10;"
    with sql.connect(
        server_hostname=DATABRICKS_HOST,
        http_path=SQL_HTTP_PATH,
        credentials_provider=posit_strategy.sql_credentials_provider(cfg),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
            print(pd.DataFrame([row.asDict() for row in rows]))
    ```
    """

    def __init__(
        self,
        local_strategy: CredentialsStrategy,
        client: Optional[Client] = None,
    ):
        self._local_strategy = local_strategy
        self._client = client

    def sql_credentials_provider(self, *args, **kwargs):
        """The sql connector attempts to call the credentials provider w/o any args.

        The SQL client's `ExternalAuthProvider` is not compatible w/ the SDK's implementation of
        `CredentialsProvider`, so create a no-arg lambda that wraps the args defined by the real caller.
        This way we can pass in a databricks `Config` object required by most of the SDK's `CredentialsProvider`
        implementations from where `sql.connect` is called.

        https://github.com/databricks/databricks-sql-python/issues/148#issuecomment-2271561365
        """
        return lambda: self.__call__(*args, **kwargs)

    def auth_type(self) -> str:
        return _get_auth_type(self._local_strategy.auth_type())

    def __call__(self, *args, **kwargs) -> CredentialsProvider:
        # If the content is not running on Connect then fall back to local_strategy
        if is_local():
            return self._local_strategy(*args, **kwargs)

        if self._client is None:
            self._client = Client()

        return PositContentCredentialsProvider(self._client)


class PositCredentialsStrategy(CredentialsStrategy):
    """`CredentialsStrategy` implementation which supports interacting with Viewer OAuth integrations on Connect.

    This strategy callable class returns a `PositCredentialsProvider` when hosted on Connect, and
    its `local_strategy` strategy otherwise.

    Examples
    --------
    NOTE: In the example below, the PositCredentialsProvider *must* be initialized within the context of the
    shiny `server` function, which provides access to the HTTP session headers.

    ```python
    import os

    import pandas as pd
    from databricks import sql
    from databricks.sdk.core import ApiClient, Config, databricks_cli
    from databricks.sdk.service.iam import CurrentUserAPI
    from posit.connect.external.databricks import PositCredentialsStrategy
    from shiny import App, Inputs, Outputs, Session, render, ui

    DATABRICKS_HOST = "<REDACTED>"
    DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
    SQL_HTTP_PATH = "<REDACTED>"

    app_ui = ui.page_fluid(ui.output_text("text"), ui.output_data_frame("result"))


    def server(i: Inputs, o: Outputs, session: Session):
        # HTTP session headers are available in this context.
        session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
        posit_strategy = PositCredentialsStrategy(
            local_strategy=databricks_cli, user_session_token=session_token
        )
        cfg = Config(host=DATABRICKS_HOST_URL, credentials_strategy=posit_strategy)

        @render.data_frame
        def result():
            query = "SELECT * FROM samples.nyctaxi.trips LIMIT 10;"

            with sql.connect(
                server_hostname=DATABRICKS_HOST,
                http_path=SQL_HTTP_PATH,
                credentials_provider=posit_strategy.sql_credentials_provider(cfg),
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
                    return df

        @render.text
        def text():
            databricks_user_info = CurrentUserAPI(ApiClient(cfg)).me()
            return f"Hello, {databricks_user_info.display_name}!"


    app = App(app_ui, server)
    ```
    """

    def __init__(
        self,
        local_strategy: CredentialsStrategy,
        client: Optional[Client] = None,
        user_session_token: Optional[str] = None,
    ):
        self._local_strategy = local_strategy
        self._client = client
        self._user_session_token = user_session_token

    def sql_credentials_provider(self, *args, **kwargs):
        """The sql connector attempts to call the credentials provider w/o any args.

        The SQL client's `ExternalAuthProvider` is not compatible w/ the SDK's implementation of
        `CredentialsProvider`, so create a no-arg lambda that wraps the args defined by the real caller.
        This way we can pass in a databricks `Config` object required by most of the SDK's `CredentialsProvider`
        implementations from where `sql.connect` is called.

        See Also
        --------
        * https://github.com/databricks/databricks-sql-python/issues/148#issuecomment-2271561365
        """
        return lambda: self.__call__(*args, **kwargs)

    def auth_type(self) -> str:
        return _get_auth_type(self._local_strategy.auth_type())

    def __call__(self, *args, **kwargs) -> CredentialsProvider:
        # If the content is not running on Connect then fall back to local_strategy
        if is_local():
            return self._local_strategy(*args, **kwargs)

        # If the user-session-token wasn't provided and we're running on Connect then we raise an exception.
        # user_session_token is required to impersonate the viewer.
        if self._user_session_token is None:
            raise ValueError("The user-session-token is required for viewer authentication.")

        if self._client is None:
            self._client = Client()

        return PositCredentialsProvider(self._client, self._user_session_token)
