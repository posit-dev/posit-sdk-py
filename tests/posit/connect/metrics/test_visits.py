from unittest import mock

import responses
from responses import matchers

from posit import connect
from posit.connect.metrics import visits

from ..api import load_mock, load_mock_dict


class TestVisitAttributes:
    @classmethod
    def setup_class(cls):
        results = load_mock_dict("v1/instrumentation/content/visits?limit=500.json")["results"]
        assert isinstance(results, list)
        first_result_dict = results[0]
        assert isinstance(first_result_dict, dict)
        cls.visit = visits.VisitEvent(
            mock.Mock(),
            **first_result_dict,
        )

    def test_content_guid(self):
        assert self.visit.content_guid == "bd1d2285-6c80-49af-8a83-a200effe3cb3"

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
        ]

        # setup
        c = connect.Client("https://connect.example", "12345")

        # invoke
        events = visits.Visits(c._ctx).find()

        # assert
        assert mock_get[0].call_count == 1
        assert mock_get[1].call_count == 1
        assert len(events) == 1


class TestVisitsFindOne:
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
        ]

        # setup
        c = connect.Client("https://connect.example", "12345")

        # invoke
        event = visits.Visits(c._ctx).find_one()

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
