from unittest import mock

import responses
from responses import matchers

from posit.connect.client import Client
from posit.connect.oauth.sessions import Session

from ..api import load_mock  # type: ignore


class TestOAuthSessionAttributes:
    @classmethod
    def setup_class(cls):
        guid = "32c04dc6-0318-41b7-bc74-7e321b196f14"
        fake_item = load_mock(f"v1/oauth/sessions/{guid}.json")
        cls.item = Session(mock.Mock(), **fake_item)

    def test_id(self):
        assert self.item.id == "54"

    def test_guid(self):
        assert self.item.guid == "32c04dc6-0318-41b7-bc74-7e321b196f14"

    def test_user_guid(self):
        assert self.item.user_guid == "217be1f2-6a32-46b9-af78-e3f4b89f2e74"

    def test_oauth_integration_guid(self):
        assert self.item.oauth_integration_guid == "967f0ad3-3e3b-4491-8539-1a193b35a415"

    def test_has_refresh_token(self):
        assert self.item.has_refresh_token

    def test_created_time(self):
        assert self.item.created_time == "2024-07-24T15:59:51Z"

    def test_updated_time(self):
        assert self.item.updated_time == "2024-07-24T16:59:51Z"


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
        client = Client("https://connect.example", "12345")

        # invoke
        sessions = client.oauth.sessions.find()

        # assert
        assert mock_get.call_count == 1
        assert len(sessions) == 3
        assert sessions[0].id == "54"
        assert sessions[1].id == "55"
        assert sessions[2].id == "56"

    @responses.activate
    def test_params_all(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/oauth/sessions",
            json=load_mock("v1/oauth/sessions.json"),
            match=[matchers.query_param_matcher({"all": True})],
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        client.oauth.sessions.find(all=True)

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
        client = Client("https://connect.example", "12345")

        # invoke
        session = client.oauth.sessions.get(guid=guid)

        # assert
        assert mock_get.call_count == 1
        assert session.guid == guid
