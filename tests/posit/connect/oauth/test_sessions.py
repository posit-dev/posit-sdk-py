import responses
from responses import matchers

from posit.connect.client import Client

from ..api import load_mock


class TestSessionDelete:
    @responses.activate
    def test(self):
        guid = "32c04dc6-0318-41b7-bc74-7e321b196f14"

        # behavior
        responses.get(
            f"https://connect.example/__api__/v1/oauth/sessions/{guid}",
            json=load_mock(f"v1/oauth/sessions/{guid}.json"),
        )

        mock_delete = responses.delete(f"https://connect.example/__api__/v1/oauth/sessions/{guid}")

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        session = c.oauth.sessions.get(guid)

        # invoke
        session.delete()

        # assert
        assert mock_delete.call_count == 1


class TestSessionsFind:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/oauth/sessions",
            json=load_mock("v1/oauth/sessions.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # invoke
        sessions = c.oauth.sessions.find()

        # assert
        assert mock_get.call_count == 1
        assert len(sessions) == 3
        assert sessions[0]["id"] == "54"
        assert sessions[1]["id"] == "55"
        assert sessions[2]["id"] == "56"

    @responses.activate
    def test_params_all(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/oauth/sessions",
            json=load_mock("v1/oauth/sessions.json"),
            match=[matchers.query_param_matcher({"all": True})],
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # invoke
        c.oauth.sessions.find(all=True)

        # assert
        assert mock_get.call_count == 1


class TestSessionsGet:
    @responses.activate
    def test(self):
        guid = "32c04dc6-0318-41b7-bc74-7e321b196f14"

        # behavior
        mock_get = responses.get(
            f"https://connect.example/__api__/v1/oauth/sessions/{guid}",
            json=load_mock(f"v1/oauth/sessions/{guid}.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # invoke
        session = c.oauth.sessions.get(guid=guid)

        # assert
        assert mock_get.call_count == 1
        assert session["guid"] == guid
