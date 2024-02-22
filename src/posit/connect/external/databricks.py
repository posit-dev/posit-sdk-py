import abc
from typing import Callable, Dict, Optional

from ..oauth import OAuthIntegration


HeaderFactory = Callable[[], Dict[str, str]]

# https://github.com/databricks/databricks-sdk-py/blob/v0.20.0/databricks/sdk/credentials_provider.py
# https://github.com/databricks/databricks-sql-python/blob/v3.1.0/src/databricks/sql/auth/authenticators.py
# In order to keep compatibility with the Databricks SDK
class CredentialsProvider(abc.ABC):
    """ CredentialsProvider is the protocol (call-side interface)
     for authenticating requests to Databricks REST APIs"""

    @abc.abstractmethod
    def auth_type(self) -> str:
        ...

    @abc.abstractmethod
    def __call__(self, *args, **kwargs) -> HeaderFactory:
        ...


class PositOAuthIntegrationCredentialsProvider(CredentialsProvider):
    def __init__(self, posit_oauth: OAuthIntegration, content_identity: str):
        self.posit_oauth = posit_oauth
        self.content_identity = content_identity

    def auth_type(self) -> str:
        return "posit-oauth-integration"

    def __call__(self, *args, **kwargs) -> HeaderFactory:
        def inner() -> Dict[str, str]:
            access_token = self.posit_oauth.get_credentials(self.content_identity).json()['access_token']
            return {"Authorization": f"Bearer {access_token}"}
        return inner


def viewer_credentials_provider(posit_oauth: OAuthIntegration, content_identity: Optional[str]) -> Optional[CredentialsProvider]:

    # If the content is not running on Connect then viewer auth should
    # fall back to the locally configured credentials hierarchy
    if posit_oauth.client.is_local():
        return None

    # If the content-identity-token wasn't provided and we're running on Connect then we raise an exception.
    # content_identity is required to impersonate the viewer.
    if content_identity is None:
        raise Exception("The content-identity-token is required for viewer authentication.")

    return PositOAuthIntegrationCredentialsProvider(posit_oauth, content_identity)


def service_account_credentials_provider(posit_oauth: OAuthIntegration):
    raise NotImplemented
