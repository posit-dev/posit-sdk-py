"""Connect API integration.

Connect API key exchange implementation which supports interacting with Posit OAuth integrations on Connect.

Notes
-----
The APIs in this module are provided as a convenience and are subject to breaking changes.
"""

from typing_extensions import Optional

from ..oauth.oauth import API_KEY_TOKEN_TYPE

from ..client import Client
from .external import is_local


class ConnectAPIKeyProvider:
    """
    Provider for exchanging Connect User Session Token for Connect API Key that acts on behalf of the user.
    This is an ephemeral API key that adheres to typical ephemeral API key clean up processes.

    Examples
    --------
    ```python
    from shiny import App, render, ui, reactive, req
    from posit.connect import Client
    from posit.connect.external.connect_api import ConnectAPIKeyProvider

    client = Client()

    app_ui = ui.page_fixed(
        ui.h1("My Shiny App"),
        # ...
    )

    def server(input, output, session):
        user_session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
        provider = ConnectAPIKeyProvider(client, user_session_token)
        viewer_api_key = provider.viewer_key

        # your app logic...

    app = App(app_ui, server)
    ```
    """

    def __init__(
        self,
        client: Optional[Client] = None,
        user_session_token: Optional[str] = None,
    ):
        self._client = client
        self._user_session_token = user_session_token

    @property
    def viewer_key(self) -> Optional[str]:
        """
        The viewer key is retrieved through an OAuth exchange process using the user session token.
        The issued API key is associated with the viewer of your app and can be used on their behalf
        to interact with the Connect API.
        """
        if is_local():
            return None

        # If the user-session-token wasn't provided and we're running on Connect then we raise an exception.
        # user_session_token is required to impersonate the viewer.
        if self._user_session_token is None:
            raise ValueError("The user-session-token is required for viewer API key authorization.")

        if self._client is None:
            self._client = Client()

        credentials = self._client.oauth.get_credentials(
            user_session_token=self._user_session_token,
            requested_token_type=API_KEY_TOKEN_TYPE,
        )
        return credentials.get("access_token")
