"""Tests for the in-session Client's launcher API resource properties."""

from unittest.mock import patch

import responses

from posit.workbench import Client
from posit.workbench.compute_envs import ComputeEnvs
from posit.workbench.jobs import Jobs
from posit.workbench.server import Server
from posit.workbench.sessions import Sessions
from posit.workbench.users import Users

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
    def test_sessions_property(self):
        """client.sessions returns a Sessions resource manager."""
        assert isinstance(Client().sessions, Sessions)

    @patch.dict("os.environ", _ENV)
    def test_jobs_property(self):
        """client.jobs returns a Jobs resource manager."""
        assert isinstance(Client().jobs, Jobs)

    @patch.dict("os.environ", _ENV)
    def test_compute_envs_property(self):
        """client.compute_envs returns a ComputeEnvs resource manager."""
        assert isinstance(Client().compute_envs, ComputeEnvs)

    @patch.dict("os.environ", _ENV)
    def test_users_property(self):
        """client.users returns a Users resource manager."""
        assert isinstance(Client().users, Users)

    @patch.dict("os.environ", _ENV)
    def test_server_property(self):
        """client.server returns a Server resource manager."""
        assert isinstance(Client().server, Server)

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
