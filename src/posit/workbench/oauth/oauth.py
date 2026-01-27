from __future__ import annotations

from datetime import datetime

from typing_extensions import TypedDict

from ..context import Context, requires
from ..resources import Resources
from .integrations import Integrations


class Credentials(TypedDict):
    """OAuth credentials response.

    Attributes
    ----------
    access_token : str
        The OAuth access token
    expiry : datetime
        Token expiration time
    integration_id : str
        The integration identifier
    """

    access_token: str
    expiry: datetime
    integration_id: str


class AzureToken(TypedDict):
    """Azure delegated token response.

    Attributes
    ----------
    access_token : str
        The OAuth2 access token
    token_type : str
        The token type (typically 'Bearer')
    expires_in : int
        Token lifetime in seconds
    scope : str
        Granted scopes (optional)
    ext_expires_in : int
        Extended expiration for Azure (optional)
    """

    access_token: str
    token_type: str
    expires_in: int
    scope: str  # optional
    ext_expires_in: int  # optional


class OAuth(Resources):
    """OAuth resource manager for Workbench.

    Provides access to OAuth credentials, integrations, and Azure delegated tokens.
    """

    def __init__(self, ctx: Context) -> None:
        super().__init__(ctx)

    @property
    def integrations(self) -> Integrations:
        """Access the OAuth integrations resource.

        Returns
        -------
        Integrations
            The integrations resource for finding and managing OAuth integrations.
        """
        return Integrations(self._ctx)

    @requires(version="2026.01.0")
    def get_credentials(self, audience: str) -> Credentials | None:
        """Retrieve OAuth credentials for a given integration ID.

        Parameters
        ----------
        audience : str
            The ID of the OAuth integration.

        Returns
        -------
        Credentials | None
            The OAuth credentials if found, otherwise None.
        """
        path = "/oauth_token"
        body = {
            "method": path,
            "kwparams": {
                "uuid": audience,
            },
        }
        response = self._ctx.client.get("/oauth_token", json=body)
        response.raise_for_status()
        response_json = response.json()
        if "error" in response_json:
            raise RuntimeError(f"Error retrieving OAuth credentials: {response_json['error']}")
        if "access_token" in response_json:
            # Handle 'Z' timezone suffix for Python 3.10 compatibility
            expiry_str = response_json["expiry"].replace("Z", "+00:00")
            return Credentials(
                access_token=response_json["access_token"],
                expiry=datetime.fromisoformat(expiry_str),
                integration_id=audience,
            )
        return None

    @requires(version="2024.12.0")
    def get_delegated_azure_token(self, resource: str) -> AzureToken:
        """Get an Azure delegated access token.

        Retrieves an OAuth2 access token from Azure Active Directory for the
        specified resource. This is used when Workbench is configured with
        Azure AD authentication and you need to access Azure resources on
        behalf of the authenticated user.

        Parameters
        ----------
        resource : str
            The resource URL for which to request the token. For example:
            - "https://management.azure.com/" for Azure Resource Manager
            - "https://storage.azure.com/" for Azure Storage
            - "https://graph.microsoft.com/" for Microsoft Graph
            Must be a non-empty string.

        Returns
        -------
        AzureToken
            A dictionary containing the access token and metadata including:
            - access_token: The OAuth2 bearer token
            - token_type: The token type (typically "Bearer")
            - expires_in: Token lifetime in seconds
            - scope: Granted scopes (optional)
            - ext_expires_in: Extended expiration for Azure (optional)

        Raises
        ------
        ValueError
            If resource is empty or not a string.
        RuntimeError
            If the backend returns an error response, which may occur if:
            - Workbench is not configured with Azure AD authentication
            - The resource URL is invalid or not authorized
            - The user lacks necessary permissions
        """
        if not resource or not isinstance(resource, str):
            raise ValueError("Invalid value for 'resource': Must be a non-empty string.")

        path = "/delegated_azure_token"
        body = {
            "method": path,
            "kwparams": {
                "resource": resource,
            },
        }
        response = self._ctx.client.get("/delegated_azure_token", json=body)
        response.raise_for_status()
        response_json = response.json()

        if "error" in response_json:
            raise RuntimeError(f"Error retrieving Azure delegated token: {response_json['error']}")

        # Validate required fields are present
        if "access_token" not in response_json or "token_type" not in response_json:
            raise RuntimeError("Invalid response from backend: missing required token fields")

        return response_json
