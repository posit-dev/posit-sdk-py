"""Schedule resources."""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone

from typing_extensions import TYPE_CHECKING, List, Literal, Optional, Sequence, Union, overload

from .errors import ClientError
from .resources import BaseResource, Resources

if TYPE_CHECKING:
    from .context import Context

# `datetime.timezone` under a distinct name; the `timezone` parameter of
# `Schedules.set()` shadows the module-level import within its scope.
_UTC = timezone.utc

ScheduleType = Literal[
    "minute",
    "hour",
    "day",
    "weekday",
    "week",
    "dayofweek",
    "semimonth",
    "dayofmonth",
    "dayweekofmonth",
    "year",
]

_DAY_NAMES = {
    "sunday": 0,
    "monday": 1,
    "tuesday": 2,
    "wednesday": 3,
    "thursday": 4,
    "friday": 5,
    "saturday": 6,
}

_INTERVAL_TYPES = ("minute", "hour", "day", "week", "year")


def _normalize_days(days: Sequence[Union[int, str]]) -> List[int]:
    """Normalize weekday values to integers where 0 is Sunday and 6 is Saturday."""
    normalized = set()
    for day in days:
        if isinstance(day, str):
            try:
                normalized.add(_DAY_NAMES[day.lower()])
            except KeyError:
                raise ValueError(
                    f"Invalid day name: {day!r}. Expected one of {sorted(_DAY_NAMES)}."
                ) from None
        elif isinstance(day, bool) or not isinstance(day, int):
            raise TypeError(f"Invalid day: {day!r}. Expected an int (0-6) or a day name.")
        elif not 0 <= day <= 6:
            raise ValueError(f"Invalid day: {day}. Expected an int between 0 (Sunday) and 6.")
        else:
            normalized.add(day)
    if not normalized:
        raise ValueError("At least one day is required.")
    return sorted(normalized)


def _build_schedule_json(
    type: ScheduleType,  # noqa: A002
    *,
    n: Optional[int] = None,
    days: Optional[Sequence[Union[int, str]]] = None,
    day: Optional[int] = None,
    week: Optional[int] = None,
    first: Optional[bool] = None,
) -> str:
    """Encode the per-type schedule parameters as the JSON string Connect expects."""
    provided = {
        name: value
        for name, value in (
            ("n", n),
            ("days", days),
            ("day", day),
            ("week", week),
            ("first", first),
        )
        if value is not None
    }
    allowed = {
        "weekday": set(),
        "dayofweek": {"days"},
        "semimonth": {"first"},
        "dayofmonth": {"n", "day"},
        "dayweekofmonth": {"n", "day", "week"},
        **{interval: {"n"} for interval in _INTERVAL_TYPES},
    }
    try:
        extraneous = set(provided) - allowed[type]
    except KeyError:
        raise ValueError(
            f"Invalid schedule type: {type!r}. Expected one of {sorted(allowed)}."
        ) from None
    if extraneous:
        if allowed[type]:
            raise ValueError(
                f"Invalid parameters for schedule type {type!r}: {sorted(extraneous)}. "
                f"Allowed parameters: {', '.join(sorted(allowed[type]))}."
            )
        raise ValueError(f"Schedule type {type!r} takes no parameters; got {sorted(extraneous)}.")
    for name, value in (("n", n), ("day", day), ("week", week)):
        if value is not None and (isinstance(value, bool) or not isinstance(value, int)):
            raise TypeError(f"Invalid {name}: {value!r}. Expected an int.")

    if type in _INTERVAL_TYPES:
        if n is None:
            raise ValueError(f"Schedule type {type!r} requires 'n'.")
        if n < 1:
            raise ValueError(f"Invalid n: {n}. Expected an int greater than or equal to 1.")
        return json.dumps({"N": n})
    if type == "weekday":
        return json.dumps({})
    if type == "dayofweek":
        if days is None:
            raise ValueError("Schedule type 'dayofweek' requires 'days'.")
        return json.dumps({"Days": _normalize_days(days)})
    if type == "semimonth":
        return json.dumps({"First": True if first is None else first})
    # 'dayofmonth' and 'dayweekofmonth'
    if day is None:
        raise ValueError(f"Schedule type {type!r} requires 'day'.")
    n = 1 if n is None else n
    if n < 1:
        raise ValueError(f"Invalid n: {n}. Expected an int greater than or equal to 1.")
    if type == "dayofmonth":
        if not 1 <= day <= 31:
            raise ValueError(f"Invalid day: {day}. Expected an int between 1 and 31.")
        return json.dumps({"N": n, "Day": day})
    if week is None:
        raise ValueError("Schedule type 'dayweekofmonth' requires 'week'.")
    if not 0 <= day <= 6:
        raise ValueError(f"Invalid day: {day}. Expected an int between 0 (Sunday) and 6.")
    if not 0 <= week <= 5:
        raise ValueError(f"Invalid week: {week}. Expected an int between 0 and 5.")
    return json.dumps({"N": n, "Day": day, "Week": week})


def _format_start_time(start_time: Union[datetime, str]) -> str:
    """Format a start time as the UTC RFC 3339 timestamp Connect expects.

    Naive datetimes are assumed to be UTC.
    """
    if isinstance(start_time, str):
        return start_time
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    return start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Schedule(BaseResource):
    """A schedule for rendering a variant of a content item.

    Warnings
    --------
    This API is backed by unversioned Connect endpoints and is experimental; it may
    change in future releases.
    """

    @property
    def rule(self) -> dict:
        """The decoded per-type schedule parameters.

        The server returns the `"schedule"` field as a JSON-encoded string (e.g.
        `'{"N":3}'`). This property returns it decoded.

        Returns
        -------
        dict
        """
        return json.loads(self["schedule"])

    def destroy(self) -> None:
        """Destroy the schedule.

        Warnings
        --------
        This operation is backed by an unversioned Connect endpoint and is experimental.
        """
        warnings.warn(
            "destroy() is experimental and may change in future releases.",
            FutureWarning,
            stacklevel=2,
        )
        self._ctx.client.delete(f"schedules/{self['id']}")


class Schedules(Resources):
    """Manager for the render schedule of a single variant.

    A variant has at most one schedule.

    Warnings
    --------
    This API is backed by unversioned Connect endpoints and is experimental; it may
    change in future releases. `set()` and `delete()` emit `FutureWarning`.
    """

    def __init__(self, ctx: Context, *, app_id: int, variant_id: int) -> None:
        super().__init__(ctx)
        self.app_id = app_id
        self.variant_id = variant_id

    def find_one(self) -> Schedule | None:
        """Find the schedule for this variant.

        Returns
        -------
        Schedule | None
            The current schedule, or `None` if the variant is not scheduled.
        """
        response = self._ctx.client.get(f"variants/{self.variant_id}/schedules")
        results = response.json() or []
        return next((Schedule(self._ctx, **result) for result in results), None)

    @overload
    def set(
        self,
        *,
        type: Literal["minute", "hour", "day", "week", "year"],
        n: int,
        start_time: Union[datetime, str, None] = None,
        timezone: Optional[str] = None,
        email: Optional[bool] = None,
    ) -> Schedule: ...

    @overload
    def set(
        self,
        *,
        type: Literal["weekday"],
        start_time: Union[datetime, str, None] = None,
        timezone: Optional[str] = None,
        email: Optional[bool] = None,
    ) -> Schedule: ...

    @overload
    def set(
        self,
        *,
        type: Literal["dayofweek"],
        days: Sequence[Union[int, str]],
        start_time: Union[datetime, str, None] = None,
        timezone: Optional[str] = None,
        email: Optional[bool] = None,
    ) -> Schedule: ...

    @overload
    def set(
        self,
        *,
        type: Literal["semimonth"],
        first: bool = True,
        start_time: Union[datetime, str, None] = None,
        timezone: Optional[str] = None,
        email: Optional[bool] = None,
    ) -> Schedule: ...

    @overload
    def set(
        self,
        *,
        type: Literal["dayofmonth"],
        day: int,
        n: int = 1,
        start_time: Union[datetime, str, None] = None,
        timezone: Optional[str] = None,
        email: Optional[bool] = None,
    ) -> Schedule: ...

    @overload
    def set(
        self,
        *,
        type: Literal["dayweekofmonth"],
        day: int,
        week: int,
        n: int = 1,
        start_time: Union[datetime, str, None] = None,
        timezone: Optional[str] = None,
        email: Optional[bool] = None,
    ) -> Schedule: ...

    def set(
        self,
        *,
        type: ScheduleType,  # noqa: A002
        start_time: Union[datetime, str, None] = None,
        timezone: Optional[str] = None,
        email: Optional[bool] = None,
        **kwargs,
    ) -> Schedule:
        """Create or update the schedule for this variant.

        If the variant is not scheduled, a new schedule is created. Otherwise, the
        provided fields are merged over the existing schedule.

        New schedules are created with activation enabled (matching the Connect
        dashboard): each successful render is published as the variant's current
        rendering, making it what viewers see. Updates preserve the schedule's
        existing activation setting.

        Parameters
        ----------
        type : str
            The recurrence type. One of `"minute"`, `"hour"`, `"day"`, `"weekday"`
            (every Monday through Friday), `"week"`, `"dayofweek"`, `"semimonth"`,
            `"dayofmonth"`, `"dayweekofmonth"`, or `"year"`.
        n : int
            Render every `n` minutes/hours/days/weeks/months/years, depending on
            `type`. Required for `"minute"`, `"hour"`, `"day"`, `"week"`, and
            `"year"`; optional (default `1`) for `"dayofmonth"` and
            `"dayweekofmonth"`.
        days : Sequence[int | str]
            For `"dayofweek"`: the days of the week on which to render. Integers
            between `0` (Sunday) and `6` (Saturday), or case-insensitive day names
            (e.g. `"monday"`). Note the integer encoding differs from Python's
            `datetime.weekday()`, where 0 is Monday.
        first : bool
            For `"semimonth"`: `True` to render on the 1st and 15th of the month,
            `False` to render on the 14th and the last day of the month. Default
            `True`.
        day : int
            For `"dayofmonth"`: the day of the month, between 1 and 31. For
            `"dayweekofmonth"`: the day of the week, between `0` (Sunday) and `6`.
        week : int
            For `"dayweekofmonth"`: the week of the month, between 0 and 5.
        start_time : datetime | str, optional
            When the schedule takes effect. Strings are passed through unchanged and
            must be RFC 3339 timestamps; datetimes are converted to UTC, with naive
            datetimes assumed to be UTC. When creating a schedule, defaults to the
            current time; when updating, the existing value is kept.
        timezone : str, optional
            The IANA timezone in which the schedule is interpreted (e.g.
            `"America/New_York"`). When creating a schedule, defaults to `"UTC"`;
            when updating, the existing value is kept. See `GET v1/timezones` for
            valid values.
        email : bool, optional
            Whether to send an email upon rendering. When creating a schedule,
            defaults to `False`; when updating, the existing value is kept.

        Returns
        -------
        Schedule

        Warnings
        --------
        This operation is backed by an unversioned Connect endpoint and is experimental.

        Examples
        --------
        ```python
        from posit import connect

        client = connect.Client()
        content = client.content.get("CONTENT_GUID_HERE")

        # Render every Monday and Wednesday at the current time of day
        content.schedule.set(
            type="dayofweek",
            days=["monday", "wednesday"],
            timezone="America/New_York",
        )

        # Render every 2 hours
        content.schedule.set(type="hour", n=2)

        # Render on the 1st and 15th of each month
        content.schedule.set(type="semimonth", first=True)
        ```
        """
        warnings.warn(
            "set() is experimental and may change in future releases.",
            FutureWarning,
            stacklevel=2,
        )
        schedule = _build_schedule_json(type, **kwargs)
        body: dict = {"type": type, "schedule": schedule}
        if start_time is not None:
            body["start_time"] = _format_start_time(start_time)
        if timezone is not None:
            body["timezone"] = timezone
        if email is not None:
            body["email"] = email

        existing = self.find_one()
        if existing is None:
            body.setdefault("start_time", _format_start_time(datetime.now(tz=_UTC)))
            body.setdefault("timezone", "UTC")
            body.setdefault("email", False)
            # `activate` controls whether a scheduled render is published as the
            # variant's current rendering and whether the success email is sent;
            # the server stores false when omitted, which makes the schedule run
            # without any visible effect. The Connect dashboard always sends true
            # on create; do the same. Updates preserve the existing value via the
            # merge below.
            body["activate"] = True
            body["app_id"] = self.app_id
            body["variant_id"] = self.variant_id
            response = self._ctx.client.post("schedules", json=body)
        else:
            # The update endpoint has full-replace semantics: `id`, `app_id`,
            # `variant_id`, `start_time`, and `timezone` are required in the body,
            # and omitted writable fields (e.g. `activate`) are reset to zero
            # values. Extra fields are ignored, so send the complete existing
            # record with the changes merged over it.
            merged = dict(existing)
            merged.pop("next_run", None)
            merged.update(body)
            response = self._ctx.client.post(f"schedules/{existing['id']}", json=merged)
        return Schedule(self._ctx, **response.json())

    def delete(self) -> None:
        """Delete the schedule for this variant.

        Idempotent: does nothing if the variant is not scheduled.

        Warnings
        --------
        This operation is backed by an unversioned Connect endpoint and is experimental.
        """
        warnings.warn(
            "delete() is experimental and may change in future releases.",
            FutureWarning,
            stacklevel=2,
        )
        existing = self.find_one()
        if existing is None:
            return
        try:
            self._ctx.client.delete(f"schedules/{existing['id']}")
        except ClientError as e:
            # The schedule can disappear between the lookup and the delete (e.g.
            # removed in the dashboard or by a concurrent pipeline); that still
            # counts as successfully unscheduled.
            if e.http_status != 404:
                raise
