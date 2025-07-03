"""Databricks SDK integration.

Databricks SDK credentials implementations which support interacting with Posit OAuth integrations on Connect.

Notes
-----
These APIs are provided as a convenience and are subject to breaking changes:
https://github.com/databricks/databricks-sdk-py#interface-stability
"""

from __future__ import annotations

import logging

from typing_extensions import TYPE_CHECKING, Dict, Optional

from .._utils import is_connect, is_workbench
from ..client import Client

try:
    from databricks.sdk.core import Config, DefaultCredentials
    from databricks.sdk.credentials_provider import (
        CredentialsProvider,
        CredentialsStrategy,
    )
except ImportError as e:
    raise ImportError("The 'databricks-sdk' package is required to use this module.") from e

if TYPE_CHECKING:
    from ..oauth import Credentials


POSIT_OAUTH_INTEGRATION_AUTH_TYPE = "posit-oauth-integration"

logger = logging.getLogger(__name__)


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


class _PositConnectContentCredentialsProvider:
    """`CredentialsProvider` implementation which initiates a credential exchange using a content-session-token.

    The content-session-token is provided by Connect through the environment variable `CONNECT_CONTENT_SESSION_TOKEN`.

    See Also
    --------
    * https://github.com/posit-dev/posit-sdk-py/blob/main/src/posit/connect/oauth/oauth.py
    """

    def __init__(
        self,
        client: Client,
        audience: Optional[str] = None,
    ):
        self._client = client
        self._audience = audience

    def __call__(self) -> Dict[str, str]:
        credentials = self._client.oauth.get_content_credentials(audience=self._audience)
        return _new_bearer_authorization_header(credentials)


class _PositConnectViewerCredentialsProvider:
    """`CredentialsProvider` implementation which initiates a credential exchange using a user-session-token.

    The user-session-token is provided by Connect through the HTTP session header
    `Posit-Connect-User-Session-Token`.

    See Also
    --------
    * https://github.com/posit-dev/posit-sdk-py/blob/main/src/posit/connect/oauth/oauth.py
    """

    def __init__(
        self,
        client: Client,
        user_session_token: str,
        audience: Optional[str] = None,
    ):
        self._client = client
        self._user_session_token = user_session_token
        self._audience = audience

    def __call__(self) -> Dict[str, str]:
        credentials = self._client.oauth.get_credentials(
            self._user_session_token,
            audience=self._audience,
        )
        return _new_bearer_authorization_header(credentials)


class ConnectStrategy(CredentialsStrategy):
    """A `CredentialsStrategy` implementation which supports content running on Posit Connect.

    This strategy can be used as a valid `credentials_strategy` when constructing a [](`databricks.sdk.core.Config`).

    It should be used when content running on a Posit Connect server needs to access a Databricks token
    that is managed by a Posit Connect OAuth integration. This strategy is _only_ valid when running
    on Posit Connect. If you need to author content that can run in multiple environments
    (local content, Posit Workbench, _and_ Posit Connect), consider using the `databricks_config()`
    helper method in this module.

    This strategy can be used for both Viewer authentication and Service Account authentication
    (sometimes referred to as Content credentials). When `user_session_token` is provided then
    Viewer authentication is used, otherwise the strategy attempts to fall back to Service Account
    authentication by reading the `CONNECT_CONTENT_SESSION_TOKEN` environment var.

    See Also
    --------
    * https://docs.posit.co/connect/admin/integrations/oauth-integrations/databricks/

    Examples
    --------
    This example shows how to do Viewer authentication with a Viewer Databricks OAuth integration.

    ```python
    import os

    from databricks.sdk.core import ApiClient, Config
    from databricks.sdk.service.iam import CurrentUserAPI
    from shiny import reactive
    from shiny.express import render, session

    from posit.connect.external.databricks import ConnectStrategy


    @reactive.calc
    def cfg():
        session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
        return Config(
            credentials_strategy=ConnectStrategy(user_session_token=session_token),
            host=os.getenv("DATABRICKS_HOST"),
        )


    @render.text
    def text():
        current_user_api = CurrentUserAPI(ApiClient(cfg()))
        databricks_user_info = current_user_api.me()
        return f"Hello, {databricks_user_info.display_name}!"
    ```

    This example shows how to do Service Account authentication with a Service Account Databricks OAuth integration.

    ```python
    import os

    from databricks.sdk.core import ApiClient, Config
    from databricks.sdk.service.iam import CurrentUserAPI
    from shiny import reactive
    from shiny.express import render

    from posit.connect.external.databricks import ConnectStrategy


    @reactive.calc
    def cfg():
        return Config(
            credentials_strategy=ConnectStrategy(),
            host=os.getenv("DATABRICKS_HOST"),
        )


    @render.text
    def text():
        current_user_api = CurrentUserAPI(ApiClient(cfg()))
        databricks_user_info = current_user_api.me()
        return f"Hello, {databricks_user_info.display_name}!"
    ```
    """

    def __init__(
        self,
        client: Optional[Client] = None,
        user_session_token: Optional[str] = None,
        audience: Optional[str] = None,
    ):
        self._cp: Optional[CredentialsProvider] = None
        self._client = client
        self._user_session_token = user_session_token
        self._audience = audience

    def auth_type(self) -> str:
        return POSIT_OAUTH_INTEGRATION_AUTH_TYPE

    def __call__(self, *args, **kwargs) -> CredentialsProvider:  # noqa: ARG002
        if not is_connect():
            raise ValueError(
                "ConnectStrategy is not supported for content running outside of Posit Connect"
            )

        if self._client is None:
            self._client = Client()

        if self._cp is None:
            if self._user_session_token:
                self._cp = _PositConnectViewerCredentialsProvider(
                    self._client,
                    self._user_session_token,
                    audience=self._audience,
                )
            else:
                logger.info(
                    "ConnectStrategy will attempt to use OAuth Service Account credentials because user_session_token is not set"
                )
                self._cp = _PositConnectContentCredentialsProvider(
                    self._client,
                    audience=self._audience,
                )
        return self._cp


def sql_credentials(cfg: Config) -> CredentialsProvider:
    """A helper method for making a [](`databricks.sdk.core.Config`) object compatible with `databricks.sql.connect`.

    The SQL client's `ExternalAuthProvider` is not compatible w/ the SDK's implementation of
    `CredentialsProvider`, so create a no-arg lambda that wraps the args defined by the real caller.
    This way we can pass in a databricks `Config` object required by most of the SDK's `CredentialsProvider`
    implementations from where `sql.connect` is called.

    See Also
    --------
    * https://github.com/databricks/databricks-sql-python/issues/148#issuecomment-2271561365

    Examples
    --------
    ```python
    import os

    from databricks import sql
    from databricks.sdk.core import ApiClient, Config
    from databricks.sdk.service.iam import CurrentUserAPI

    from posit.connect.external.databricks import sql_credentials

    cfg = Config(
        host=os.getenv("DATABRICKS_HOST"),
        warehouse_id=os.getenv("DATABRICKS_WAREHOUSE_ID"),
    )

    with sql.connect(
        server_hostname=cfg.host,
        http_path=cfg.sql_http_path,
        credentials_provider=sql_credentials(cfg),
    ) as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM samples.nyctaxi.trips LIMIT 10;")
            print(cursor.fetchall())
    ```
    """
    return lambda: cfg._credentials_strategy(cfg)


def databricks_config(
    posit_default_strategy: Optional[CredentialsStrategy] = None,
    posit_workbench_strategy: Optional[CredentialsStrategy] = None,
    posit_connect_strategy: Optional[CredentialsStrategy] = None,
    **kwargs,
) -> Config:
    """A helper to aid with constructing a valid [](`databricks.sdk.core.Config`) object.

    The returned `Config` is configured with a credentials_strategy which should be compatible with the current
    execution environment. This is useful when authoring content that needs to run in multiple environments
    without changing code. This constructor allows you mix-and-match Databricks SDK credentials_strategies.
    For example, content executing on a developer laptop can use the `databricks_cli` strategy, while
    in Workbench the same content can use the `pat_auth` strategy, and in Connect the content uses
    the custom `ConnectStrategy()` with a Databricks OAuth integration.

    Parameters
    ----------
    posit_default_strategy : databricks.sdk.credentials_provider.CredentialsStrategy, optional
        The default credentials_strategy to use when neither Posit Connect nor Posit Workbench are detected
    posit_workbench_strategy : databricks.sdk.credentials_provider.CredentialsStrategy, optional
        The credentials_strategy to use when Posit Workbench is detected
    posit_connect_strategy : databricks.sdk.credentials_provider.CredentialsStrategy, optional
        The credentials_strategy to use when Posit Connect is detected
    kwargs : Dict[str, Any], optional
        Additional keyword arguments. kwargs is passed directly to the databricks.sdk.core.Config constructor.

    Returns
    -------
        databricks.sdk.core.Config

    See Also
    --------
    * https://docs.posit.co/connect/admin/integrations/oauth-integrations/databricks/

    Examples
    --------
    This example shows how to construct a databricks Config that is compatible with:
    - Databricks CLI authentication for local development
    - Workbench-managed Databricks Credentials in Posit Workbench
    - Viewer OAuth integration authentication in Posit Connect

    ```python
    import os

    from databricks.sdk.core import ApiClient, databricks_cli
    from databricks.sdk.service.iam import CurrentUserAPI
    from shiny import reactive
    from shiny.express import render, session

    from posit.connect.external.databricks import (
        ConnectStrategy,
        databricks_config,
    )
    from posit.workbench.external.databricks import WorkbenchStrategy


    @reactive.calc
    def cfg():
        session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
        return databricks_config(
            posit_default_strategy=databricks_cli,
            posit_workbench_strategy=WorkbenchStrategy(),
            posit_connect_strategy=ConnectStrategy(user_session_token=session_token),
            host=os.getenv("DATABRICKS_HOST"),
        )


    @render.text
    def text():
        current_user_api = CurrentUserAPI(ApiClient(cfg()))
        databricks_user_info = current_user_api.me()
        return f"Hello, {databricks_user_info.display_name}!"
    ```

    This example shows how to construct a databricks Config that is compatible with:
    - OAuth Service Principal (oauth-m2m) in Posit Workbench
    - Viewer OAuth integration authentication in Posit Connect

    This examples uses environment variables to load the correct configurations at runtime. Make sure to set
    the `DATABRICKS_CLIENT_ID` and `DATABRICKS_CLIENT_SECRET` as environment variables in Posit Workbench, but do
    not set them inside of Posit Connect.

    ```python
    import os

    from databricks.sdk.core import ApiClient, oauth_service_principal
    from databricks.sdk.service.iam import CurrentUserAPI
    from shiny import reactive
    from shiny.express import render, session

    from posit.connect.external.databricks import (
        ConnectStrategy,
        databricks_config,
    )


    @reactive.calc
    def cfg():
        session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
        return databricks_config(
            posit_workbench_strategy=oauth_service_principal,
            posit_connect_strategy=ConnectStrategy(user_session_token=session_token),
            host=os.getenv("DATABRICKS_HOST"),
            client_id=os.getenv("DATABRICKS_CLIENT_ID"),
            client_secret=os.getenv("DATABRICKS_CLIENT_SECRET"),
        )


    @render.text
    def text():
        current_user_api = CurrentUserAPI(ApiClient(cfg()))
        databricks_user_info = current_user_api.me()
        return f"Hello, {databricks_user_info.display_name}!"
    ```

    This example shows how to construct a databricks Config that is compatible with:
    - Azure Service Principal credentials in Posit Workbench
    - Service Account OAuth integration authentication in Posit Connect

    This examples uses environment variables to load the correct configurations at runtime. Make sure to set
    the `ARM_CLIENT_ID`, `ARM_CLIENT_SECRET`, and `ARM_TENANT_ID` as environment variables in Posit Workbench, but do
    not set them inside of Posit Connect.

    ```python
    import os

    from databricks.sdk.core import ApiClient, azure_service_principal
    from databricks.sdk.service.iam import CurrentUserAPI
    from shiny import reactive
    from shiny.express import render

    from posit.connect.external.databricks import (
        ConnectStrategy,
        databricks_config,
    )


    @reactive.calc
    def cfg():
        return databricks_config(
            posit_workbench_strategy=azure_service_principal,
            posit_connect_strategy=ConnectStrategy(),
            host=os.getenv("DATABRICKS_HOST"),
            azure_client_id=os.getenv("ARM_CLIENT_ID"),
            azure_client_secret=os.getenv("ARM_CLIENT_SECRET"),
            azure_tenant_id=os.getenv("ARM_TENANT_ID"),
        )


    @render.text
    def text():
        current_user_api = CurrentUserAPI(ApiClient(cfg()))
        databricks_user_info = current_user_api.me()
        return f"Hello, {databricks_user_info.display_name}!"
    ```
    """
    credentials_strategy = None
    if "credentials_strategy" in kwargs:
        del kwargs["credentials_strategy"]

    if is_connect():
        logger.info("Using Posit Connect credentials strategy")
        if posit_connect_strategy is not None:
            credentials_strategy = posit_connect_strategy
        else:
            credentials_strategy = ConnectStrategy()
    elif is_workbench():
        logger.info("Using Posit Workbench credentials strategy")
        if posit_workbench_strategy is not None:
            credentials_strategy = posit_workbench_strategy
        else:
            credentials_strategy = DefaultCredentials()
    else:
        logger.info(
            "Using default credentials strategy because neither Posit Connect nor Posit Workbench were detected"
        )
        if posit_default_strategy is not None:
            credentials_strategy = posit_default_strategy
        else:
            credentials_strategy = DefaultCredentials()

    return Config(credentials_strategy=credentials_strategy, **kwargs)  # pyright: ignore[reportArgumentType]
