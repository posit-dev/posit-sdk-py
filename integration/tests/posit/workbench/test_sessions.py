# The SDK's response TypedDicts are total=False; these tests index keys a live server returns.
# pyright: reportTypedDictNotRequiredAccess=false

from __future__ import annotations

import time

from posit.workbench import admin

from . import CLUSTER, RESOURCE_PROFILE


def _session_ids(client) -> set[str]:
    return {session["id"] for session in client.sessions.get().get("sessions") or []}


def _activity_state(client, session_id: str) -> str | None:
    for session in client.sessions.get(session_id).get("sessions") or []:
        return session.get("activity_state")
    return None


class TestSessions:
    @classmethod
    def setup_class(cls):
        cls.client = client = admin.Client()
        cls.existing = _session_ids(client)
        cls.session = client.sessions.launch(
            "RStudio",
            name="it-session",
            launch_parameters={
                "name": "it-session",
                "cluster": CLUSTER,
                "resource_profile": RESOURCE_PROFILE,  # pyright: ignore[reportArgumentType]
            },
        )

    @classmethod
    def teardown_class(cls):
        leftover = _session_ids(cls.client) - cls.existing
        if leftover:
            cls.client.sessions.stop(list(leftover), force_quit=True)

    def test_launch(self):
        assert self.session["id"]
        assert self.session["url"]

    def test_get(self):
        sessions = self.client.sessions.get(self.session["id"])["sessions"]
        assert [s["id"] for s in sessions] == [self.session["id"]]
        assert sessions[0]["workbench"] == "RStudio"

    def test_connection_url(self):
        url = self.client.sessions.connection_url(self.session)
        assert url.startswith(str(self.client.server_url))

    def test_get_historical(self):
        historical = self.client.sessions.get_historical(include_jobs=True)
        assert isinstance(historical.get("sessions", []), list)

    def test_stop(self):
        session = self.client.sessions.launch(
            "RStudio",
            name="it-session-stop",
            launch_parameters={
                "name": "it-session-stop",
                "cluster": CLUSTER,
                "resource_profile": RESOURCE_PROFILE,  # pyright: ignore[reportArgumentType]
            },
        )
        # A stop sent while the session is still pending/starting has no effect.
        deadline = time.monotonic() + 120
        while _activity_state(self.client, session["id"]) != "running":
            assert time.monotonic() < deadline, "Session did not start within 120s"
            time.sleep(1)

        self.client.sessions.stop(session["id"], force_quit=True)

        deadline = time.monotonic() + 60
        while session["id"] in _session_ids(self.client) and time.monotonic() < deadline:
            time.sleep(1)
        assert session["id"] not in _session_ids(self.client)
