from pathlib import Path

import pytest
from packaging import version
from typing_extensions import Any, Dict, List, Tuple

from posit import connect

from . import CONNECT_VERSION


@pytest.mark.skipif(
    CONNECT_VERSION <= version.parse("2023.01.1"),
    reason="Quarto not available",
)
class TestSchedules:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        content = cls.client.content.create(name="example-quarto-minimal")

        path = Path("../../../resources/connect/bundles/example-quarto-minimal/bundle.tar.gz")
        path = Path(__file__).parent / path
        bundle = content.bundles.create(str(path.resolve()))
        task = bundle.deploy()
        task.wait_for()

        # `content` still has app_mode "unknown" because the record predates the
        # deploy; content.schedule refreshes it automatically.
        cls.content = content

    @classmethod
    def teardown_class(cls):
        cls.content.delete()
        assert cls.client.content.count() == 0

    def test_lifecycle(self):
        schedules = self.content.schedule

        assert schedules.find_one() is None

        created = schedules.create(
            type="dayofweek",
            days=["monday", "wednesday"],
            start_time="2026-01-01T09:00:00Z",
            timezone="America/New_York",
        )
        assert created.rule == {"Days": [1, 3]}
        assert created["activate"] is True
        assert created["timezone"] == "America/New_York"

        found = schedules.find_one()
        assert found is not None
        assert found["id"] == created["id"]
        assert found.rule == {"Days": [1, 3]}

        updated = schedules.create(type="hour", n=2, email=True)
        assert updated["id"] == created["id"]
        assert updated.rule == {"N": 2}
        assert updated["email"] is True
        assert updated["activate"] is True
        # fields not specified in the update are preserved
        assert updated["timezone"] == "America/New_York"
        assert updated["start_time"] == "2026-01-01T09:00:00Z"

        schedules.delete()
        assert schedules.find_one() is None

        # idempotent
        schedules.delete()
        assert schedules.find_one() is None

    def test_every_schedule_type(self):
        schedules = self.content.schedule
        cases: List[Tuple[Dict[str, Any], dict]] = [
            ({"type": "minute", "n": 15}, {"N": 15}),
            ({"type": "hour", "n": 2}, {"N": 2}),
            ({"type": "day", "n": 3}, {"N": 3}),
            ({"type": "weekday"}, {}),
            ({"type": "week", "n": 2}, {"N": 2}),
            ({"type": "dayofweek", "days": [0, 1, 6]}, {"Days": [0, 1, 6]}),
            ({"type": "semimonth", "first": True}, {"First": True}),
            ({"type": "semimonth", "first": False}, {"First": False}),
            ({"type": "dayofmonth", "n": 3, "day": 4}, {"N": 3, "Day": 4}),
            (
                {"type": "dayweekofmonth", "n": 3, "day": 1, "week": 4},
                {"N": 3, "Day": 1, "Week": 4},
            ),
            ({"type": "year", "n": 2}, {"N": 2}),
        ]
        try:
            for kwargs, expected_rule in cases:
                result = schedules.create(**kwargs)
                assert result.rule == expected_rule, kwargs
                found = schedules.find_one()
                assert found is not None
                assert found.rule == expected_rule, kwargs
        finally:
            if schedules.find_one() is not None:
                schedules.delete()

    def test_undeployed_content_not_schedulable(self):
        # nothing is deployed, so app_mode remains "unknown" even after the
        # refresh performed by content.schedule
        content = self.client.content.create(name="unschedulable")
        try:
            with pytest.raises(ValueError):
                content.schedule  # noqa: B018
        finally:
            content.delete()
