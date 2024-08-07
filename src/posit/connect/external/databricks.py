import abc
import os
from typing import Callable, Dict, Optional

from ..client import Client
from ..oauth import OAuthIntegration

"""
NOTE: These APIs are provided as a convenience and are subject to breaking changes:
https://github.com/databricks/databricks-sdk-py#interface-stability
"""

# The Databricks SDK CredentialsProvider == Databricks SQL HeaderFactory
CredentialsProvider = Callable[[], Dict[str, str]]

class CredentialsStrategy(abc.ABC):
    """Maintain compatibility with the Databricks SQL/SDK client libraries.

    https://github.com/databricks/databricks-sql-python/blob/v3.3.0/src/databricks/sql/auth/authenticators.py#L19-L33
    https://github.com/databricks/databricks-sdk-py/blob/v0.29.0/databricks/sdk/credentials_provider.py#L44-L54
    """

    @abc.abstractmethod
    def auth_type(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> CredentialsProvider:
        raise NotImplementedError


def _is_local() -> bool:
    """Returns true if called from a piece of content running on a Connect server.

    The connect server will always set the environment variable `RSTUDIO_PRODUCT=CONNECT`.
    We can use this environment variable to determine if the content is running locally
    or on a Connect server.
    """
    return not os.getenv("RSTUDIO_PRODUCT") == "CONNECT"


class PositCredentialsProvider:
    def __init__(self, posit_oauth: OAuthIntegration, user_session_token: str):
        self.posit_oauth = posit_oauth
        self.user_session_token = user_session_token

    def __call__(self) -> Dict[str, str]:
        access_token = self.posit_oauth.get_credentials(
            self.user_session_token
        )["access_token"]
        return {"Authorization": f"Bearer {access_token}"}


class PositCredentialsStrategy(CredentialsStrategy):

    def __init__(self,
        local_strategy: CredentialsStrategy,
        user_session_token: Optional[str] = None,
        client: Optional[Client] = None
    ):
        self.user_session_token = user_session_token
        self.local_strategy = local_strategy
        self.client = client

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
        """Returns the auth type currently in use.

        The databricks-sdk client uses the configurated auth_type to create
        a user-agent string which is used for attribution. We should only
        overwrite the auth_type if we are using the PositCredentialsStrategy (non-local),
        otherwise, we should return the auth_type of the configured local_strategy instead
        to avoid breaking someone elses attribution.

        https://github.com/databricks/databricks-sdk-py/blob/v0.29.0/databricks/sdk/config.py#L261-L269

        NOTE: The databricks-sql client does not use auth_type to set the user-agent.
        https://github.com/databricks/databricks-sql-python/blob/v3.3.0/src/databricks/sql/client.py#L214-L219
        """
        if _is_local():
            return self.local_strategy.auth_type()
        else:
            return "posit-oauth-integration"

    def __call__(self, *args, **kwargs) -> CredentialsProvider:
        # If the content is not running on Connect then fall back to local_strategy
        if _is_local():
            return self.local_strategy(*args, **kwargs)

        # If the user-session-token wasn't provided and we're running on Connect then we raise an exception.
        # user_session_token is required to impersonate the viewer.
        if self.user_session_token is None:
            raise ValueError(
                "The user-session-token is required for viewer authentication."
            )

        if self.client is None:
            self.client = Client()

        return PositCredentialsProvider(
            self.client.oauth, self.user_session_token
        )
