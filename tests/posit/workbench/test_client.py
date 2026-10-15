"""Tests for the in-session Client's launcher API resource properties."""

from unittest.mock import patch

import responses

from posit.workbench import Client

# Valid RPC cookie format: value|expiry_date
TEST_RPC_COOKIE = "test-cookie-value|Mon%2C%2001%20Jan%202030%2000%3A00%3A00%20GMT"

_ENV = {
    "POSIT_PRODUCT": "WORKBENCH",
    "RS_SERVER_ADDRESS": "https://workbench.example.com",
    "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
}


class TestLauncherApiProperties:
    """Tests that the existing Client exposes the shared launcher API resource managers."""

    @patch.dict("os.environ", _ENV)
    @responses.activate
    def test_users_manager_is_wired_to_the_client(self):
        """The launcher API resource managers actually route calls through this client."""
        responses.add(
            responses.POST,
            "https://workbench.example.com/api/get_users",
            json={"result": [{"username": "user1"}]},
            status=200,
        )
        # Hold a strong reference to the client -- Context only holds a weak one, so a
        # one-line `Client().users.list()` risks the client being garbage collected
        # mid-expression before the request is made.
        client = Client()
        users = client.users.list()
        assert users[0]["username"] == "user1"  # pyright: ignore[reportTypedDictNotRequiredAccess]
