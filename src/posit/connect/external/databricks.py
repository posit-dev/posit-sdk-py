from typing import Dict, Optional, TYPE_CHECKING

from ..oauth import OAuthIntegration

if TYPE_CHECKING:
    from databricks.sdk.core import Config, HeaderFactory, credentials_provider


def viewer_sql_credentials_provider(posit_oauth: OAuthIntegration, content_identity: Optional[str]):

    # If the content is not running on Connect then viewer auth should
    # fall back to the locally configured credentials hierarchy
    if posit_oauth.client.is_local():
        return None

    # If the content-identity-token wasn't provided and we're running on Connect then we raise an exception.
    # content_identity is required to impersonate the viewer.
    if content_identity is None:
        raise Exception("The content-identity-token is required for viewer authentication.")

    def custom_credentials_provider():
        def inner() -> Dict[str, str]:
            return {"Authorization": f"Bearer {posit_oauth.get_credentials(content_identity)}"}
        return inner
    return custom_credentials_provider


def viewer_sdk_credentials_provider(posit_oauth: OAuthIntegration, content_identity: Optional[str]):

    # If the content is not running on Connect then viewer auth should
    # fall back to the locally configured credentials hierarchy
    if posit_oauth.client.is_local():
        return None

    # If the content-identity-token wasn't provided and we're running on Connect then we raise an exception.
    # content_identity is required to impersonate the viewer.
    if content_identity is None:
        raise Exception("The content-identity-token is required for viewer authentication.")

    @credentials_provider("custom", ["host"])
    def custom_credentials_provider(cfg: Config) -> HeaderFactory:
        def inner() -> Dict[str, str]:
            return {"Authorization": f"Bearer {posit_oauth.get_credentials(content_identity)}"}
        return inner
    return custom_credentials_provider


def service_account_sql_credentials_provider(posit_oauth: OAuthIntegration):
    raise NotImplemented


def service_account_sdk_credentials_provider(posit_oauth: OAuthIntegration):
    raise NotImplemented
