from typing import TypedDict
from datetime import datetime

from ..resources import Resources
from ..context import Context

class Credentials(TypedDict):
    access_token: str
    expiry: datetime
    integration_id: str

class OAuth(Resources):
    def __init__(self, ctx: Context) -> None:
        super().__init__(ctx)

    def get_credentials(self, integration_id: str) -> Credentials | None:
        """Retrieve OAuth credentials for a given integration ID.

        Parameters
        ----------
        integration_id : str
            The ID of the OAuth integration.

        Returns
        -------
            str | None: The OAuth credentials if found, otherwise None.
        """
        path = "/oauth_token"
        body = {
            "method": path,
            "kwparams": {
                "uuid": integration_id,
            },
        }
        response = self._ctx.client.get("/oauth_token", json=body)
        response.raise_for_status()
        response_json = response.json()
        if "error" in response_json:
            raise RuntimeError(f"Error retrieving OAuth credentials: {response_json['error']}")
        if "access_token" in response_json:
            return Credentials(
                access_token=response_json["access_token"],
                expiry=datetime.fromisoformat(response_json["expiry"]),
                integration_id=integration_id,
            )
        return None
