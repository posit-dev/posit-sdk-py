import responses

from posit.connect import Client
from posit.connect.visits import Visit, rename_params

from .api import load_mock  # type: ignore


class TestVisitAttributes:
    def setup_class(cls):
        cls.visit = Visit(
            None,
            None,
            **load_mock("v1/instrumentation/content/visits.json")["results"][0],
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
        mock_get = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/content/visits",
            json=load_mock("v1/instrumentation/content/visits.json"),
        )

        mock_get_sentinel = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/content/visits",
            json={"paging": {}, "results": []},
        )

        # setup
        c = Client("12345", "https://connect.example")

        # invoke
        visits = c.visits.find()

        # assert
        assert mock_get.call_count == 1
        assert mock_get_sentinel.call_count == 1
        assert len(visits) == 1


class TestVisitsFindOne:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            f"https://connect.example/__api__/v1/instrumentation/content/visits",
            json=load_mock("v1/instrumentation/content/visits.json"),
        )

        # setup
        c = Client("12345", "https://connect.example")

        # invoke
        visit = c.visits.find_one()

        # assert
        assert mock_get.call_count == 1
        assert visit


class TestRenameParams:
    def test_start_to_from(self):
        params = {"start": ...}
        params = rename_params(params)
        assert "start" not in params
        assert "from" in params

    def test_end_to_to(self):
        params = {"end": ...}
        params = rename_params(params)
        assert "end" not in params
        assert "to" in params