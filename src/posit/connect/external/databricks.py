import abc
from typing import Callable, Dict, Optional

from ..client import Client
from ..oauth import Credentials
from .external import is_local

"""
NOTE: These APIs are provided as a convenience and are subject to breaking changes:
https://github.com/databricks/databricks-sdk-py#interface-stability
"""

POSIT_OAUTH_INTEGRATION_AUTH_TYPE = "posit-oauth-integration"

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

    The databricks-sdk client uses the configurated auth_type to create
    a user-agent string which is used for attribution. We should only
    overwrite the auth_type if we are using the PositCredentialsStrategy (non-local),
    otherwise, we should return the auth_type of the configured local_strategy instead
    to avoid breaking someone elses attribution.

    https://github.com/databricks/databricks-sdk-py/blob/v0.29.0/databricks/sdk/config.py#L261-L269

    NOTE: The databricks-sql client does not use auth_type to set the user-agent.
    https://github.com/databricks/databricks-sql-python/blob/v3.3.0/src/databricks/sql/client.py#L214-L219
    
    Returns
    -------
        str
    """
    if is_local():
        return local_auth_type

    return POSIT_OAUTH_INTEGRATION_AUTH_TYPE 



class PositContentCredentialsProvider:
    """CredentialsProvider implementation which initiates a credential exchange using a content-session-token."""

    def __init__(self, client: Client):
        self._client = client

    def __call__(self) -> Dict[str, str]:
        credentials = self._client.oauth.get_content_credentials()
        return _new_bearer_authorization_header(credentials)


class PositCredentialsProvider:
    """CredentialsProvider implementation which initiates a credential exchange using a user-session-token."""

    def __init__(self, client: Client, user_session_token: str):
        self._client = client
        self._user_session_token = user_session_token

    def __call__(self) -> Dict[str, str]:
        credentials = self._client.oauth.get_credentials(self._user_session_token)
        return _new_bearer_authorization_header(credentials)


class PositContentCredentialsStrategy(CredentialsStrategy):
    """CredentialsStrategy implementation which returns a PositContentCredentialsProvider when called."""

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
    """CredentialsStrategy implementation which returns a PositContentCredentialsProvider when called."""

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
