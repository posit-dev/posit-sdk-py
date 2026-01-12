"""OAuth integration resources."""

from __future__ import annotations

from functools import partial

from typing_extensions import Optional

from ..context import requires
from ..resources import Resources, _matches_exact, _matches_pattern, _Resource


class Integration(_Resource):
    """OAuth integration resource.

    Represents a single OAuth integration configured in Workbench.

    Attributes
    ----------
    guid : str
        The unique identifier (GUID) of the integration.
    name : str
        The internal name of the integration.
    display_name : str
        The user-facing display name of the integration.
    type : str
        The OAuth provider type (e.g., "github", "azure", "custom", etc.).
    client_id : str
        The OAuth client ID for this integration.
    auth_url : str
        The authorization URL for the OAuth provider.
    token_url : str
        The token exchange URL for the OAuth provider.
    scopes : list[str]
        The OAuth scopes requested by this integration.
    issuer : str
        The issuer URL for the OAuth provider.
    authenticated : bool
        Whether the current user is authenticated with this integration.
    """

    # No additional methods needed for read-only resource


class Integrations(Resources):
    """OAuth integrations resource collection."""

    @requires(version="2026.01.0")
    def find(self) -> list[Integration]:
        """Find all OAuth integrations.

        Returns
        -------
        list[Integration]
            A list of all OAuth integrations configured in Workbench.

        Raises
        ------
        RuntimeError
            If the backend returns an error response.
        """
        path = "/oauth_integrations"
        body = {
            "method": path,
            "kwparams": {},
        }
        response = self._ctx.client.get("/oauth_integrations", json=body)
        response.raise_for_status()
        response_json = response.json()

        if "error" in response_json:
            raise RuntimeError(f"Error retrieving OAuth integrations: {response_json['error']}")

        # Backend returns {"providers": [...]} where each provider has an "integrations" array
        # We flatten the nested structure and rename "uid" to "guid" for consistency
        providers = response_json.get("providers", [])
        integrations = []

        for provider in providers:
            # Each provider can have multiple integrations
            provider_integrations = provider.get("integrations", [])
            for integration in provider_integrations:
                # Create a copy and rename uid to guid
                integration_data = dict(integration)
                if "uid" in integration_data:
                    integration_data["guid"] = integration_data.pop("uid")
                integrations.append(Integration(self._ctx, **integration_data))

        return integrations

    @requires(version="2026.01.0")
    def find_by(
        self,
        name: Optional[str] = None,
        display_name: Optional[str] = None,
        guid: Optional[str] = None,
        authenticated: Optional[bool] = None,
    ) -> Integration | None:
        """Find an OAuth integration by various criteria.

        Parameters
        ----------
        name : Optional[str]
            A regex pattern to match the integration name. For exact matches,
            use `^` and `$`. For example, `^github-main$` will match only "github-main".
        display_name : Optional[str]
            A regex pattern to match the integration display name. For exact matches,
            use `^` and `$`. For example, `^GitHub$` will match only "GitHub".
        guid : Optional[str]
            The unique identifier (GUID) of the integration.
        authenticated : Optional[bool]
            Whether the user is authenticated with this integration.

        Returns
        -------
        Integration | None
            The first matching integration, or None if no match is found.
        """
        filters = []
        if name is not None:
            filters.append(partial(_matches_pattern, key="name", pattern=name))
        if display_name is not None:
            filters.append(partial(_matches_pattern, key="display_name", pattern=display_name))
        if guid is not None:
            filters.append(partial(_matches_exact, key="guid", value=guid))
        if authenticated is not None:
            filters.append(partial(_matches_exact, key="authenticated", value=authenticated))

        for integration in self.find():
            if all(f(integration) for f in filters):
                return integration

        return None

    @requires(version="2026.01.0")
    def get(self, guid: str) -> Integration | None:
        """Get an OAuth integration by GUID.

        This is a convenience method that calls find_by(guid=guid).

        Parameters
        ----------
        guid : str
            The unique identifier (GUID) of the integration to retrieve.
            Must be a non-empty string.

        Returns
        -------
        Integration | None
            The integration if found, otherwise None.

        Raises
        ------
        ValueError
            If guid is empty or not a string.
        """
        if not guid or not isinstance(guid, str):
            raise ValueError("Invalid value for 'guid': Must be a non-empty string.")

        return self.find_by(guid=guid)
