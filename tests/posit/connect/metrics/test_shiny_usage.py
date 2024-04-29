import responses
import requests

from responses import matchers

from posit.connect import Client, config
from posit.connect.metrics import shiny_usage

from ..api import load_mock  # type: ignore


class TestShinyUsageEventAttributes:
    def setup_class(cls):
        cls.event = shiny_usage.ShinyUsageEvent(
            None,
            None,
            **load_mock("v1/instrumentation/shiny/usage?limit=500.json")[
                "results"
            ][0],
        )

    def test_content_guid(self):
        assert (
            self.event.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"
        )

    def test_user_guid(self):
        assert self.event.user_guid == "08e3a41d-1f8e-47f2-8855-f05ea3b0d4b2"

    def test_started(self):
        assert self.event.started == "2018-09-15T18:00:00-05:00"

    def test_ended(self):
        assert self.event.ended == "2018-09-15T18:01:00-05:00"

    def test_data_version(self):
        assert self.event.data_version == 1


class TestShinyUsageFind:
    @responses.activate
    def test(self):
        # behavior
        mock_get = [None] * 2
        mock_get[0] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/shiny/usage",
            json=load_mock("v1/instrumentation/shiny/usage?limit=500.json"),
            match=[
                matchers.query_param_matcher(
                    {
                        "limit": 500,
                    }
                )
            ],
        )

        mock_get[1] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/shiny/usage",
            json=load_mock(
                "v1/instrumentation/shiny/usage?limit=500&next=23948901087.json"
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
        events = shiny_usage.ShinyUsage(c, session).find()

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 1
        assert len(events) == 1


class TestShinyUsageFindOne:
    @responses.activate
    def test(self):
        # behavior
        mock_get = [None] * 2
        mock_get[0] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/shiny/usage",
            json=load_mock("v1/instrumentation/shiny/usage?limit=500.json"),
            match=[
                matchers.query_param_matcher(
                    {
                        "limit": 500,
                    }
                )
            ],
        )

        mock_get[1] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/shiny/usage",
            json=load_mock(
                "v1/instrumentation/shiny/usage?limit=500&next=23948901087.json"
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
        event = shiny_usage.ShinyUsage(c, session).find_one()

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 0
        assert event
        assert event.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"


class TestRenameParams:
    def test_start_to_from(self):
        params = {"start": ...}
        params = shiny_usage.rename_params(params)
        assert "start" not in params
        assert "from" in params

    def test_end_to_to(self):
        params = {"end": ...}
        params = shiny_usage.rename_params(params)
        assert "end" not in params
        assert "to" in params
