from __future__ import annotations

import os
import re
from enum import Enum

from typing_extensions import TYPE_CHECKING, Optional, TypedDict

from posit.connect.oauth.associations import ContentItemAssociations

from ..resources import Resources
from .integrations import Integrations
from .sessions import Sessions

if TYPE_CHECKING:
    from posit.connect.external import aws

    from ..context import Context

GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"


class OAuthTokenType(str, Enum):
    ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"
    AWS_CREDENTIALS = "urn:ietf:params:aws:token-type:credentials"
    API_KEY = "urn:posit:connect:api-key"
    CONTENT_SESSION_TOKEN = "urn:posit:connect:content-session-token"
    USER_SESSION_TOKEN = "urn:posit:connect:user-session-token"


class OAuthIntegrationAuthType(str, Enum):
    """OAuth integration authentication type."""

    VIEWER = "Viewer"
    SERVICE_ACCOUNT = "Service Account"
    VISITOR_API_KEY = "Visitor API Key"


class OAuthIntegrationType(str, Enum):
    """OAuth integration type."""

    AWS = "aws"
    AZURE = "azure"
    CONNECT = "connect"
    SNOWFLAKE = "snowflake"
    CUSTOM = "custom"
    # TODO add the rest


def _get_content_session_token() -> str:
    """Return the content session token.

    Reads the environment variable 'CONNECT_CONTENT_SESSION_TOKEN'.

    Raises
    ------
        ValueError: If CONNECT_CONTENT_SESSION_TOKEN is not set or invalid

    Returns
    -------
        str
    """
    value = os.environ.get("CONNECT_CONTENT_SESSION_TOKEN")
    if not value:
        raise ValueError(
            "Invalid value for 'CONNECT_CONTENT_SESSION_TOKEN': Must be a non-empty string."
        )
    return value


class OAuth(Resources):
    def __init__(self, ctx: Context, api_key: str) -> None:
        super().__init__(ctx)
        self.api_key = api_key
        self._path = "v1/oauth/integrations/credentials"

    @property
    def integrations(self):
        return Integrations(self._ctx)

    @property
    def sessions(self):
        return Sessions(self._ctx)

    def get_credentials(
        self,
        user_session_token: Optional[str] = None,
        requested_token_type: Optional[str | OAuthTokenType] = None,
        audience: Optional[str] = None,
    ) -> Credentials:
        """Perform an oauth credential exchange with a user-session-token."""
        # craft a credential exchange request
        data = {}
        data["grant_type"] = GRANT_TYPE
        data["subject_token_type"] = OAuthTokenType.USER_SESSION_TOKEN
        if user_session_token:
            data["subject_token"] = user_session_token
        if requested_token_type:
            data["requested_token_type"] = requested_token_type
        if audience:
            data["audience"] = audience

        response = self._ctx.client.post(self._path, data=data)
        return Credentials(**response.json())

    def get_content_credentials(
        self,
        content_session_token: Optional[str] = None,
        requested_token_type: Optional[str | OAuthTokenType] = None,
        audience: Optional[str] = None,
    ) -> Credentials:
        """Perform an oauth credential exchange with a content-session-token."""
        # craft a credential exchange request
        data = {}
        data["grant_type"] = GRANT_TYPE
        data["subject_token_type"] = OAuthTokenType.CONTENT_SESSION_TOKEN
        data["subject_token"] = content_session_token or _get_content_session_token()
        if requested_token_type:
            data["requested_token_type"] = requested_token_type
        if audience:
            data["audience"] = audience

        response = self._ctx.client.post(self._path, data=data)
        return Credentials(**response.json())

    def get_credentials_by(
        self,
        user_session_token: str,
        content_session_token: Optional[str] = None,
        integration_type: Optional[OAuthIntegrationType] = None,
        auth_type: Optional[OAuthIntegrationAuthType] = None,
        name: Optional[str | re.Pattern] = None,
        guid: Optional[str] = None,
    ) -> Credentials | aws.Credentials:
        """Perform an oauth credential exchange for all integrations associated with the current content item."""
        content_guid = os.getenv("CONNECT_CONTENT_GUID")
        if not content_guid:
            raise ValueError("CONNECT_CONTENT_GUID environment variable is required.")
        content_associations = ContentItemAssociations(self._ctx, content_guid=content_guid).find()
        # associations format: [{
        #     content_guid: uuid
        #     app_guid: uuid
        #     oauth_integration_guid: uuid
        #     oauth_integration_name: string
        #     oauth_integration_description: string┃null
        #     oauth_integration_template: string
        #     oauth_integration_auth_type: string
        #     created_time: date-time
        # }]
        for association in content_associations:
            match = True

            if (
                integration_type is not None
                and association.get("oauth_integration_template") != integration_type
            ):
                match = False

            if (
                auth_type is not None
                and association.get("oauth_integration_auth_type") != auth_type
            ):
                match = False

            if name is not None:
                integration_name = association.get("oauth_integration_name", "")
                if isinstance(name, re.Pattern):
                    if not name.search(integration_name):
                        match = False
                else:
                    if integration_name != name:
                        match = False

            if guid is not None and association.get("oauth_integration_guid") != guid:
                match = False

            if match:
                # Use the first matching association to get credentials
                if association.get("oauth_integration_auth_type") in [
                    OAuthIntegrationAuthType.VIEWER,
                    OAuthIntegrationAuthType.VISITOR_API_KEY,
                ]:
                    return self.get_credentials(
                        user_session_token=user_session_token,
                        audience=association.get("oauth_integration_guid"),
                    )
                return self.get_content_credentials(
                    content_session_token=content_session_token,
                    audience=association.get("oauth_integration_guid"),
                )

        raise ValueError("No matching OAuth integration found for the specified criteria.")


class Credentials(TypedDict, total=False):
    access_token: str
    issued_token_type: str
    token_type: str
