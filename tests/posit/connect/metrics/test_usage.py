from unittest import mock

import pytest
import responses
from responses import matchers

from posit import connect
from posit.connect.metrics import shiny_usage, usage, visits

from ..api import load_mock, load_mock_dict


class TestUsageEventFromEvent:
    def test(self):
        with pytest.raises(TypeError):
            usage.UsageEvent.from_event(
                None  # pyright: ignore[reportArgumentType]
            )


class TestUsageEventFromVisitEvent:
    @classmethod
    def setup_class(cls):
        results = load_mock_dict("v1/instrumentation/content/visits?limit=500.json")["results"]
        assert isinstance(results, list)

        visit_event = visits.VisitEvent(
            mock.Mock(),
            **results[0],
        )
        cls.view_event = usage.UsageEvent.from_visit_event(visit_event)

    def test_content_guid(self):
        assert self.view_event.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"

    def test_user_guid(self):
        assert self.view_event.user_guid == "08e3a41d-1f8e-47f2-8855-f05ea3b0d4b2"

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
    @classmethod
    def setup_class(cls):
        results = load_mock_dict("v1/instrumentation/shiny/usage?limit=500.json")["results"]
        assert isinstance(results, list)
        visit_event = shiny_usage.ShinyUsageEvent(
            mock.Mock(),
            **results[0],
        )
        cls.view_event = usage.UsageEvent.from_shiny_usage_event(visit_event)

    def test_content_guid(self):
        assert self.view_event.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"

    def test_user_guid(self):
        assert self.view_event.user_guid == "08e3a41d-1f8e-47f2-8855-f05ea3b0d4b2"

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
        mock_get = [
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/content/visits",
                json=load_mock("v1/instrumentation/content/visits?limit=500.json"),
                match=[
                    matchers.query_param_matcher(
                        {
                            "limit": 500,
                        },
                    ),
                ],
            ),
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/content/visits",
                json=load_mock(
                    "v1/instrumentation/content/visits?limit=500&next=23948901087.json"
                ),
                match=[
                    matchers.query_param_matcher(
                        {
                            "next": "23948901087",
                            "limit": 500,
                        },
                    ),
                ],
            ),
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/shiny/usage",
                json=load_mock("v1/instrumentation/shiny/usage?limit=500.json"),
                match=[
                    matchers.query_param_matcher(
                        {
                            "limit": 500,
                        },
                    ),
                ],
            ),
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/shiny/usage",
                json=load_mock("v1/instrumentation/shiny/usage?limit=500&next=23948901087.json"),
                match=[
                    matchers.query_param_matcher(
                        {
                            "next": "23948901087",
                            "limit": 500,
                        },
                    ),
                ],
            ),
        ]

        # setup
        c = connect.Client("https://connect.example", "12345")

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
        mock_get = [
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/content/visits",
                json=load_mock("v1/instrumentation/content/visits?limit=500.json"),
                match=[
                    matchers.query_param_matcher(
                        {
                            "limit": 500,
                        },
                    ),
                ],
            ),
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/content/visits",
                json=load_mock(
                    "v1/instrumentation/content/visits?limit=500&next=23948901087.json"
                ),
                match=[
                    matchers.query_param_matcher(
                        {
                            "next": "23948901087",
                            "limit": 500,
                        },
                    ),
                ],
            ),
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/shiny/usage",
                json=load_mock("v1/instrumentation/shiny/usage?limit=500.json"),
                match=[
                    matchers.query_param_matcher(
                        {
                            "limit": 500,
                        },
                    ),
                ],
            ),
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/shiny/usage",
                json=load_mock("v1/instrumentation/shiny/usage?limit=500&next=23948901087.json"),
                match=[
                    matchers.query_param_matcher(
                        {
                            "next": "23948901087",
                            "limit": 500,
                        },
                    ),
                ],
            ),
        ]

        # setup
        c = connect.Client("https://connect.example", "12345")

        # invoke
        view_event = c.metrics.usage.find_one()

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 0
        assert mock_get[2].call_count == 0
        assert mock_get[3].call_count == 0
        assert view_event
        assert view_event.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"

    @responses.activate
    def test_none(self):
        # behavior
        mock_get = [
            # return an empty result set to push through the iterator
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/content/visits",
                json=load_mock(
                    "v1/instrumentation/content/visits?limit=500&next=23948901087.json"
                ),
            ),
            responses.get(
                "https://connect.example/__api__/v1/instrumentation/shiny/usage",
                json=load_mock("v1/instrumentation/shiny/usage?limit=500&next=23948901087.json"),
            ),
        ]

        # setup
        c = connect.Client("https://connect.example", "12345")

        # invoke
        view_event = c.metrics.usage.find_one(content_guid="not-found")

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 1
        assert view_event is None
