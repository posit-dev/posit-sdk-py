import json
from datetime import datetime, timedelta, timezone

import pytest
import responses
from responses import matchers

from posit.connect.client import Client
from posit.connect.errors import ClientError
from posit.connect.schedules import (
    Schedule,
    Schedules,
    _build_schedule_json,
    _format_start_time,
    _normalize_days,
)
from posit.connect.variants import Variant

from .api import load_mock


class TestNormalizeDays:
    def test_names_and_ints(self):
        assert _normalize_days([0, 3, 6]) == [0, 3, 6]
        assert _normalize_days(["monday", "wednesday"]) == [1, 3]
        assert _normalize_days(["Saturday", 0, "monday"]) == [0, 1, 6]

    def test_dedupe_and_sort(self):
        assert _normalize_days(["sunday", 0, 6, "saturday"]) == [0, 6]

    def test_invalid_name(self):
        with pytest.raises(ValueError, match="Invalid day name"):
            _normalize_days(["mondayy"])

    def test_out_of_range(self):
        with pytest.raises(ValueError, match="Invalid day"):
            _normalize_days([7])

    def test_bool_rejected(self):
        with pytest.raises(TypeError, match="Invalid day"):
            _normalize_days([True])

    def test_empty(self):
        with pytest.raises(ValueError, match="At least one day"):
            _normalize_days([])


class TestBuildScheduleJson:
    @pytest.mark.parametrize(
        ("schedule_type", "kwargs", "expected"),
        [
            ("minute", {"n": 15}, {"N": 15}),
            ("hour", {"n": 2}, {"N": 2}),
            ("day", {"n": 3}, {"N": 3}),
            ("week", {"n": 2}, {"N": 2}),
            ("year", {"n": 1}, {"N": 1}),
            ("weekday", {}, {}),
            ("dayofweek", {"days": [1, 3]}, {"Days": [1, 3]}),
            ("dayofweek", {"days": ["monday", "wednesday"]}, {"Days": [1, 3]}),
            ("semimonth", {"first": True}, {"First": True}),
            ("semimonth", {"first": False}, {"First": False}),
            ("semimonth", {}, {"First": True}),
            ("dayofmonth", {"n": 3, "day": 4}, {"N": 3, "Day": 4}),
            ("dayofmonth", {"day": 4}, {"N": 1, "Day": 4}),
            ("dayweekofmonth", {"n": 3, "day": 1, "week": 4}, {"N": 3, "Day": 1, "Week": 4}),
            ("dayweekofmonth", {"day": 0, "week": 0}, {"N": 1, "Day": 0, "Week": 0}),
        ],
    )
    def test_encoding(self, schedule_type, kwargs, expected):
        result = _build_schedule_json(schedule_type, **kwargs)
        assert isinstance(result, str)
        assert json.loads(result) == expected

    @pytest.mark.parametrize(
        ("schedule_type", "kwargs", "match"),
        [
            ("minute", {}, "requires 'n'"),
            ("day", {"n": 0}, "Invalid n"),
            ("hour", {"n": 1, "days": [1]}, "Invalid parameters"),
            ("weekday", {"n": 1}, "takes no parameters"),
            ("dayofweek", {}, "requires 'days'"),
            ("dayofweek", {"days": []}, "At least one day"),
            ("dayofmonth", {}, "requires 'day'"),
            ("dayofmonth", {"day": 0}, "Invalid day"),
            ("dayofmonth", {"day": 32}, "Invalid day"),
            ("dayofmonth", {"day": 1, "n": 0}, "Invalid n"),
            ("dayweekofmonth", {"day": 1}, "requires 'week'"),
            ("dayweekofmonth", {"day": 7, "week": 1}, "Invalid day"),
            ("dayweekofmonth", {"day": 1, "week": 6}, "Invalid week"),
            ("fortnight", {}, "Invalid schedule type"),
        ],
    )
    def test_validation(self, schedule_type, kwargs, match):
        with pytest.raises(ValueError, match=match):
            _build_schedule_json(schedule_type, **kwargs)

    @pytest.mark.parametrize(
        ("schedule_type", "kwargs", "match"),
        [
            ("hour", {"n": True}, "Invalid n"),
            ("hour", {"n": 2.5}, "Invalid n"),
            ("dayofmonth", {"day": True}, "Invalid day"),
            ("dayweekofmonth", {"day": 1, "week": "1"}, "Invalid week"),
            ("semimonth", {"first": 1}, "Invalid first"),
            ("semimonth", {"first": "true"}, "Invalid first"),
        ],
    )
    def test_invalid_param_types_rejected(self, schedule_type, kwargs, match):
        with pytest.raises(TypeError, match=match):
            _build_schedule_json(schedule_type, **kwargs)


class TestFormatStartTime:
    def test_string_passthrough(self):
        assert _format_start_time("2026-01-01T09:00:00Z") == "2026-01-01T09:00:00Z"

    def test_aware_datetime_converted_to_utc(self):
        eastern = timezone(timedelta(hours=-5))
        start_time = datetime(2026, 1, 1, 7, 0, 0, tzinfo=eastern)
        assert _format_start_time(start_time) == "2026-01-01T12:00:00Z"

    def test_naive_datetime_assumed_utc(self):
        start_time = datetime(2026, 1, 1, 12, 0, 0)
        assert _format_start_time(start_time) == "2026-01-01T12:00:00Z"


class TestSchedulesFindOne:
    @responses.activate
    def test_none_when_unscheduled(self):
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=[],
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        assert schedules.find_one() is None

    @responses.activate
    def test_returns_schedule(self):
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=load_mock("variants/6627/schedules.json"),
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        schedule = schedules.find_one()
        assert schedule is not None
        assert schedule["id"] == 24
        assert schedule["type"] == "day"
        assert schedule["schedule"] == '{"N":1}'
        assert schedule.rule == {"N": 1}


class TestSchedulesSet:
    @responses.activate
    def test_create(self):
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=[],
        )
        mock_post = responses.post(
            "https://connect.example.com/__api__/schedules",
            json=load_mock("schedules.json"),
            match=[
                matchers.json_params_matcher(
                    {
                        "type": "dayofweek",
                        "schedule": json.dumps({"Days": [1, 3]}),
                        "activate": True,
                        "start_time": "2026-01-01T12:00:00Z",
                        "timezone": "America/New_York",
                        "email": False,
                        "app_id": 50941,
                        "variant_id": 6627,
                    }
                )
            ],
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        schedule = schedules.set(
            type="dayofweek",
            days=["monday", "wednesday"],
            start_time="2026-01-01T12:00:00Z",
            timezone="America/New_York",
        )

        assert schedule["id"] == 24
        assert mock_post.call_count == 1

    @responses.activate
    def test_create_defaults(self):
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=[],
        )
        mock_post = responses.post(
            "https://connect.example.com/__api__/schedules",
            json=load_mock("schedules.json"),
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        schedules.set(type="day", n=1)

        body = json.loads(mock_post.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["start_time"].endswith("Z")
        assert body["timezone"] == "UTC"
        assert body["email"] is False
        assert body["activate"] is True
        assert body["app_id"] == 50941
        assert body["variant_id"] == 6627

    @responses.activate
    def test_update_merges_over_existing(self):
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=load_mock("variants/6627/schedules.json"),
        )
        mock_post = responses.post(
            "https://connect.example.com/__api__/schedules/24",
            json=load_mock("schedules/24.json"),
            match=[
                matchers.json_params_matcher(
                    {
                        # updated fields
                        "type": "hour",
                        "schedule": json.dumps({"N": 2}),
                        "email": True,
                        # fields preserved from the existing schedule, including a
                        # non-default "activate"; "next_run" is stripped
                        "id": 24,
                        "app_id": 50941,
                        "variant_id": 6627,
                        "start_time": "2026-01-01T12:00:00Z",
                        "timezone": "UTC",
                        "activate": False,
                    }
                )
            ],
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        schedule = schedules.set(type="hour", n=2, email=True)

        assert schedule["type"] == "hour"
        assert mock_post.call_count == 1

    @responses.activate
    def test_invalid_params_raise_before_any_request(self):
        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        with pytest.raises(ValueError, match="Invalid parameters"):
            schedules.set(type="hour", n=1, days=[1])  # pyright: ignore[reportCallIssue]


class TestSchedulesDelete:
    @responses.activate
    def test_delete(self):
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=load_mock("variants/6627/schedules.json"),
        )
        mock_delete = responses.delete(
            "https://connect.example.com/__api__/schedules/24",
            body="",
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        schedules.delete()

        assert mock_delete.call_count == 1

    @responses.activate
    def test_delete_without_schedule_is_noop(self):
        # no DELETE endpoint is registered; an attempted DELETE would error
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=[],
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        schedules.delete()

    @responses.activate
    def test_delete_tolerates_races(self):
        # the schedule disappears between the lookup and the DELETE
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=load_mock("variants/6627/schedules.json"),
        )
        mock_delete = responses.delete(
            "https://connect.example.com/__api__/schedules/24",
            json={"code": 24, "error": "not found"},
            status=404,
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        schedules.delete()

        assert mock_delete.call_count == 1

    @responses.activate
    def test_delete_raises_on_other_errors(self):
        responses.get(
            "https://connect.example.com/__api__/variants/6627/schedules",
            json=load_mock("variants/6627/schedules.json"),
        )
        responses.delete(
            "https://connect.example.com/__api__/schedules/24",
            json={"code": 1, "error": "boom"},
            status=500,
        )

        c = Client("https://connect.example.com", "12345")
        schedules = Schedules(c._ctx, app_id=50941, variant_id=6627)

        with pytest.raises(ClientError):
            schedules.delete()


class TestScheduleDestroy:
    @responses.activate
    def test(self):
        mock_delete = responses.delete(
            "https://connect.example.com/__api__/schedules/24",
            body="",
        )

        c = Client("https://connect.example.com", "12345")
        schedule = Schedule(c._ctx, id=24, app_id=50941, variant_id=6627)

        schedule.destroy()

        assert mock_delete.call_count == 1


class TestVariantSchedules:
    def test(self):
        c = Client("https://connect.example.com", "12345")
        variant = Variant(c._ctx, id=6627, app_id=50941, key="txvRW8SG", is_default=True)

        with pytest.warns(FutureWarning, match="experimental"):
            schedules = variant.schedules
        assert isinstance(schedules, Schedules)
        assert schedules.app_id == 50941
        assert schedules.variant_id == 6627


class TestContentItemSchedule:
    @responses.activate
    def test_resolves_default_variant(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )
        responses.get(
            f"https://connect.example.com/__api__/applications/{guid}/variants",
            json=load_mock(f"applications/{guid}/variants.json"),
        )

        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        with pytest.warns(FutureWarning, match="experimental"):
            schedules = content.schedule
        assert isinstance(schedules, Schedules)
        assert schedules.app_id == 50941
        assert schedules.variant_id == 6627

    @responses.activate
    def test_caches_default_variant(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )
        get_variants = responses.get(
            f"https://connect.example.com/__api__/applications/{guid}/variants",
            json=load_mock(f"applications/{guid}/variants.json"),
        )

        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        with pytest.warns(FutureWarning):
            first = content.schedule
        second = content.schedule
        assert first is second
        assert get_variants.call_count == 1

    @responses.activate
    def test_refreshes_unknown_app_mode(self):
        # the record predates the deploy: the first GET reports app_mode
        # "unknown", and the refresh triggered by `content.schedule` reports the
        # deployed app_mode
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        stale_json = load_mock(f"v1/content/{guid}.json")
        stale_json["app_mode"] = "unknown"
        responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=stale_json,
        )
        get_refresh = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )
        responses.get(
            f"https://connect.example.com/__api__/applications/{guid}/variants",
            json=load_mock(f"applications/{guid}/variants.json"),
        )

        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        with pytest.warns(FutureWarning):
            schedules = content.schedule
        assert isinstance(schedules, Schedules)
        assert content["app_mode"] == "quarto-static"
        assert get_refresh.call_count == 1

    @responses.activate
    def test_undeployed_content_raises(self):
        # app_mode is still "unknown" after the refresh (nothing is deployed)
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        content_json = load_mock(f"v1/content/{guid}.json")
        content_json["app_mode"] = "unknown"
        get_content = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=content_json,
        )

        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        with pytest.raises(ValueError, match="Scheduling is not supported"):
            content.schedule  # noqa: B018
        assert get_content.call_count == 2

    @responses.activate
    def test_interactive_content_raises(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        content_json = load_mock(f"v1/content/{guid}.json")
        content_json["app_mode"] = "shiny"
        responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=content_json,
        )

        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        with pytest.raises(ValueError, match="Scheduling is not supported"):
            content.schedule  # noqa: B018

    @responses.activate
    def test_no_default_variant_raises(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )
        responses.get(
            f"https://connect.example.com/__api__/applications/{guid}/variants",
            json=[],
        )

        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        with pytest.raises(RuntimeError, match="Found 0 default variants"):
            content.schedule  # noqa: B018

    @responses.activate
    def test_multiple_default_variants_raise(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )
        responses.get(
            f"https://connect.example.com/__api__/applications/{guid}/variants",
            json=[
                {"id": 6627, "app_id": 50941, "is_default": True},
                {"id": 6628, "app_id": 50941, "is_default": True},
            ],
        )

        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        with pytest.raises(RuntimeError, match="Found 2 default variants"):
            content.schedule  # noqa: B018
