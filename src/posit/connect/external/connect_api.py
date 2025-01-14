"""Connect API integration.

Connect API key exchange implementation which supports interacting with Posit OAuth integrations on Connect.

Notes
-----
The APIs in this module are provided as a convenience and are subject to breaking changes.
"""

from typing_extensions import Optional

from ..client import Client
from ..oauth.oauth import API_KEY_TOKEN_TYPE
from .external import is_local


class ViewerConnectClientProvider:
    """Viewer client provider for Connect API integration.

    Provider handles exchanging Connect User Session Token for Connect API Key that acts on behalf of the user.
    This is an ephemeral API key that adheres to typical ephemeral API key clean up processes. The provider
    returns a `Client` that is scoped to the viewer's API key.

    Examples
    --------
    ```python
    from shiny import App, ui
    from posit.connect import Client
    from posit.connect.external.connect_api import ViewerConnectClientProvider

    app_ui = ui.page_fixed(
        ui.h1("My Shiny App"),
        # ...
    )


    def server(input, output, session):
        client = Client()
        user_session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
        viewer_client = ViewerConnectClientProvider(user_session_token).get_client()

        assert client.me() != viewer_client.me()

        # your app logic...


    app = App(app_ui, server)
    ```
    """

    def __init__(
        self,
        user_session_token: str,
        client_override: Optional[Client] = None,
        url_override: Optional[str] = None,
    ):
        if user_session_token == "":
            raise ValueError("Must provide valid user session token")

        self._user_session_token = user_session_token
        self._client = client_override if client_override else Client()
        self._url = url_override

    def get_client(self) -> Client:
        """A new Connect client that can act on behalf of the viewer based on the user session token.

        The viewer key is retrieved through an OAuth exchange process using the user session token.
        The issued API key is associated with the viewer of your app and can be used on their behalf
        to interact with the Connect API using this client.
        """
        # If running this locally, the viewer will be assumed to be the same as the publisher.
        if is_local():
            return self._client

        credentials = self._client.oauth.get_credentials(
            user_session_token=self._user_session_token,
            requested_token_type=API_KEY_TOKEN_TYPE,
        )

        return Client(url=self._url, api_key=credentials.get("access_token"))
