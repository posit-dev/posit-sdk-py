import abc
import os
from typing import Callable, Dict, Optional

from ..client import Client
from ..oauth import OAuthIntegration

HeaderFactory = Callable[[], Dict[str, str]]


# https://github.com/databricks/databricks-sdk-py/blob/v0.20.0/databricks/sdk/credentials_provider.py
# https://github.com/databricks/databricks-sql-python/blob/v3.1.0/src/databricks/sql/auth/authenticators.py
# In order to keep compatibility with the Databricks SDK
class CredentialsProvider(abc.ABC):
    """CredentialsProvider is the protocol (call-side interface)
    for authenticating requests to Databricks REST APIs"""

    @abc.abstractmethod
    def auth_type(self) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> HeaderFactory:
        raise NotImplementedError


class PositOAuthIntegrationCredentialsProvider(CredentialsProvider):
    def __init__(self, posit_oauth: OAuthIntegration, user_session_token: str):
        self.posit_oauth = posit_oauth
        self.user_session_token = user_session_token

    def auth_type(self) -> str:
        return "posit-oauth-integration"

    def __call__(self, *args, **kwargs) -> HeaderFactory:
        def inner() -> Dict[str, str]:
            access_token = self.posit_oauth.get_credentials(self.user_session_token)[
                "access_token"
            ]
            return {"Authorization": f"Bearer {access_token}"}

        return inner


# Use this environment variable to determine if the
# client SDK was initialized from a piece of content running on a Connect server.
def is_local() -> bool:
    return not os.getenv("RSTUDIO_PRODUCT") == "CONNECT"


def viewer_credentials_provider(
    client: Optional[Client] = None, user_session_token: Optional[str] = None
) -> Optional[CredentialsProvider]:
    # If the content is not running on Connect then viewer auth should
    # fall back to the locally configured credentials hierarchy
    if is_local():
        return None

    if client is None:
        client = Client()

    # If the user-session-token wasn't provided and we're running on Connect then we raise an exception.
    # user_session_token is required to impersonate the viewer.
    if user_session_token is None:
        raise ValueError(
            "The user-session-token is required for viewer authentication."
        )

    return PositOAuthIntegrationCredentialsProvider(client.oauth, user_session_token)


def service_account_credentials_provider(client: Optional[Client] = None):
    raise NotImplementedError
