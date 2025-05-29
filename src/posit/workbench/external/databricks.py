"""Databricks SDK integration.

Databricks SDK credentials implementations which support interacting with Posit Workbench-managed Databricks credentials.

Notes
-----
These APIs are provided as a convenience and are subject to breaking changes:
https://github.com/databricks/databricks-sdk-py#interface-stability
"""

from __future__ import annotations

from typing_extensions import Optional

try:
    from databricks.sdk.core import Config
    from databricks.sdk.credentials_provider import (
        CredentialsProvider,
        CredentialsStrategy,
    )
except ImportError as e:
    raise ImportError("The 'databricks-sdk' package is required to use this module.") from e


POSIT_WORKBENCH_AUTH_TYPE = "posit-workbench"


class WorkbenchStrategy(CredentialsStrategy):
    """`CredentialsStrategy` implementation which uses a bearer token authentication provider for Workbench environments.

    This strategy can be used as a valid `credentials_strategy` when constructing a [](`databricks.sdk.core.Config`).

    It should be used when content running on a Posit Workbench server needs to access a Databricks token
    that is manged by Posit Workbench-managed Databricks Credentials. If you need to author content that can
    run in multiple environments (local content, Posit Workbench, _and_ Posit Connect), consider using the
    `posit.connect.external.databricks.databricks_config()` helper method.

    See Also
    --------
    * https://docs.posit.co/ide/server-pro/user/posit-workbench/guide/databricks.html#databricks-with-python

    Examples
    --------
    This example shows how authenticate to Databricks using Posit Workbench-managed Databricks Credentials.

    ```python
    import os

    from databricks.sdk.core import ApiClient, Config
    from databricks.sdk.service.iam import CurrentUserAPI
    from shiny import reactive
    from shiny.express import render

    from posit.workbench.external.databricks import WorkbenchStrategy


    @reactive.calc
    def cfg():
        return Config(
            credentials_strategy=WorkbenchStrategy(),
            host=os.getenv("DATABRICKS_HOST"),
        )


    @render.text
    def text():
        current_user_api = CurrentUserAPI(ApiClient(cfg()))
        databricks_user_info = current_user_api.me()
        return f"Hello, {databricks_user_info.display_name}!"
    ```
    """

    def __init__(self, config: Optional[Config] = None):
        self.__config = config

    def auth_type(self) -> str:
        return POSIT_WORKBENCH_AUTH_TYPE

    @property
    def _config(self) -> Config:
        """The Databricks SDK `Config` object used by this strategy.

        Returns
        -------
        Config
            The provided `Config` object, defaulting to a new `Config` with the profile set to "workbench" if not provided.
        """
        if self.__config is None:
            # Do not create this configuration object until it is needed.
            # This avoids failing if the 'workbench' profile is not defined in the user's
            # `~/.databrickscfg` file until this strategy is actually used.
            self.__config = Config(profile="workbench")

        return self.__config

    def __call__(self, *args, **kwargs) -> CredentialsProvider:  # noqa: ARG002
        if self._config.token is None:
            raise ValueError("Missing value for field 'token' in Config.")

        return lambda: {"Authorization": f"Bearer {self._config.token}"}
