import pytest
import responses

from responses import matchers

from posit import connect
from posit.connect.metrics import shiny_usage, usage, visits


from ..api import load_mock  # type: ignore


class TestUsageEventFromEvent:
    def test(self):
        with pytest.raises(TypeError):
            usage.UsageEvent.from_event(None)


class TestUsageEventFromVisitEvent:
    def setup_class(cls):
        visit_event = visits.VisitEvent(
            None,
            None,
            **load_mock("v1/instrumentation/content/visits?limit=500.json")[
                "results"
            ][0],
        )
        cls.view_event = usage.UsageEvent.from_visit_event(visit_event)

    def test_content_guid(self):
        assert (
            self.view_event.content_guid
            == "bd1d2285-6c80-49af-8a83-a200effe3cb3"
        )

    def test_user_guid(self):
        assert (
            self.view_event.user_guid == "08e3a41d-1f8e-47f2-8855-f05ea3b0d4b2"
        )

    def test_variant_key(self):
        assert self.view_event.variant_key == "HidI2Kwq"

    def test_rendering_id(self):
        assert self.view_event.rendering_id == 7

    def test_bundle_id(self):
        assert self.view_event.bundle_id == 33

    def test_started(self):
        assert self.view_event.started == "2018-09-15T18:00:00-05:00"

    def test_ended(self):
        assert self.view_event.ended == "2018-09-15T18:00:00-05:00"

    def test_data_version(self):
        assert self.view_event.data_version == 1

    def test_path(self):
        assert self.view_event.path == "/logs"


class TestUsageEventFromShinyUsageEvent:
    def setup_class(cls):
        visit_event = shiny_usage.ShinyUsageEvent(
            None,
            None,
            **load_mock("v1/instrumentation/shiny/usage?limit=500.json")[
                "results"
            ][0],
        )
        cls.view_event = usage.UsageEvent.from_shiny_usage_event(visit_event)

    def test_content_guid(self):
        assert (
            self.view_event.content_guid
            == "bd1d2285-6c80-49af-8a83-a200effe3cb3"
        )

    def test_user_guid(self):
        assert (
            self.view_event.user_guid == "08e3a41d-1f8e-47f2-8855-f05ea3b0d4b2"
        )

    def test_variant_key(self):
        assert self.view_event.variant_key is None

    def test_rendering_id(self):
        assert self.view_event.rendering_id is None

    def test_bundle_id(self):
        assert self.view_event.bundle_id is None

    def test_started(self):
        assert self.view_event.started == "2018-09-15T18:00:00-05:00"

    def test_ended(self):
        assert self.view_event.ended == "2018-09-15T18:01:00-05:00"

    def test_data_version(self):
        assert self.view_event.data_version == 1

    def test_path(self):
        assert self.view_event.path is None


class TestUsageFind:
    @responses.activate
    def test(self):
        # behavior
        mock_get = [None] * 4

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

        mock_get[2] = responses.get(
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

        mock_get[3] = responses.get(
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
        c = connect.Client("12345", "https://connect.example")

        # invoke
        events = c.metrics.usage.find()

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 1
        assert mock_get[2].call_count == 1
        assert mock_get[3].call_count == 1
        assert len(events) == 2


class TestUsageFindOne:
    @responses.activate
    def test(self):
        # behavior
        mock_get = [None] * 4

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

        mock_get[2] = responses.get(
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

        mock_get[3] = responses.get(
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
        c = connect.Client("12345", "https://connect.example")

        # invoke
        view_event = c.metrics.usage.find_one()

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 0
        assert mock_get[2].call_count == 0
        assert mock_get[3].call_count == 0
        assert view_event
        assert (
            view_event.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"
        )

    @responses.activate
    def test_none(self):
        # behavior
        mock_get = [None] * 2

        # return an empty result set to push through the iterator
        mock_get[0] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/content/visits",
            json=load_mock(
                "v1/instrumentation/content/visits?limit=500&next=23948901087.json"
            ),
        )

        mock_get[1] = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/shiny/usage",
            json=load_mock(
                "v1/instrumentation/shiny/usage?limit=500&next=23948901087.json"
            ),
        )

        # setup
        c = connect.Client("12345", "https://connect.example")

        # invoke
        view_event = c.metrics.usage.find_one(content_guid="not-found")

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 1
        assert view_event is None
