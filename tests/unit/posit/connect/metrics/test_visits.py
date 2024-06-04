import responses
import requests

from responses import matchers

from posit.connect import Client, config
from posit.connect.metrics import visits

from ..api import load_mock  # type: ignore


class TestVisitAttributes:
    def setup_class(cls):
        cls.visit = visits.VisitEvent(
            None,
            None,
            **load_mock("v1/instrumentation/content/visits?limit=500.json")[
                "results"
            ][0],
        )

    def test_content_guid(self):
        assert (
            self.visit.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"
        )

    def test_user_guid(self):
        assert self.visit.user_guid == "08e3a41d-1f8e-47f2-8855-f05ea3b0d4b2"

    def test_variant_key(self):
        assert self.visit.variant_key == "HidI2Kwq"

    def test_rendering_id(self):
        assert self.visit.rendering_id == 7

    def test_bundle_id(self):
        assert self.visit.bundle_id == 33

    def test_time(self):
        assert self.visit.time == "2018-09-15T18:00:00-05:00"

    def test_data_version(self):
        assert self.visit.data_version == 1

    def test_path(self):
        assert self.visit.path == "/logs"


class TestVisitsFind:
    @responses.activate
    def test(self):
        # behavior
        mock_get = [None] * 2
        mock_get[0] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/content/visits",
            json=load_mock("v1/instrumentation/content/visits?limit=500.json"),
            match=[
                matchers.query_param_matcher(
                    {
                        "limit": 500,
                    }
                )
            ],
        )

        mock_get[1] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/content/visits",
            json=load_mock(
                "v1/instrumentation/content/visits?limit=500&next=23948901087.json"
            ),
            match=[
                matchers.query_param_matcher(
                    {
                        "next": "23948901087",
                        "limit": 500,
                    }
                )
            ],
        )

        # setup
        c = config.Config("12345", "https://connect.example")
        session = requests.Session()

        # invoke
        events = visits.Visits(c, session).find()

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 1
        assert len(events) == 1


class TestVisitsFindOne:
    @responses.activate
    def test(self):
        # behavior
        mock_get = [None] * 2
        mock_get[0] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/content/visits",
            json=load_mock("v1/instrumentation/content/visits?limit=500.json"),
            match=[
                matchers.query_param_matcher(
                    {
                        "limit": 500,
                    }
                )
            ],
        )

        mock_get[1] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/content/visits",
            json=load_mock(
                "v1/instrumentation/content/visits?limit=500&next=23948901087.json"
            ),
            match=[
                matchers.query_param_matcher(
                    {
                        "next": "23948901087",
                        "limit": 500,
                    }
                )
            ],
        )

        # setup
        c = config.Config("12345", "https://connect.example")
        session = requests.Session()

        # invoke
        event = visits.Visits(c, session).find_one()

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 0
        assert event
        assert event.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"


class TestRenameParams:
    def test_start_to_from(self):
        params = {"start": ...}
        params = visits.rename_params(params)
        assert "start" not in params
        assert "from" in params

    def test_end_to_to(self):
        params = {"end": ...}
        params = visits.rename_params(params)
        assert "end" not in params
        assert "to" in params
