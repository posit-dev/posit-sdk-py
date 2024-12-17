"""Usage resources."""

from __future__ import annotations

from requests.sessions import Session as Session
from typing_extensions import List, overload

from .. import resources
from . import shiny_usage, visits


class UsageEvent(resources.BaseResource):
    @staticmethod
    def from_event(
        event: visits.VisitEvent | shiny_usage.ShinyUsageEvent,
    ) -> UsageEvent:
        if isinstance(event, visits.VisitEvent):
            return UsageEvent.from_visit_event(event)

        if isinstance(event, shiny_usage.ShinyUsageEvent):
            return UsageEvent.from_shiny_usage_event(event)

        raise TypeError

    @staticmethod
    def from_visit_event(event: visits.VisitEvent) -> UsageEvent:
        return UsageEvent(
            event._ctx,
            content_guid=event.content_guid,
            user_guid=event.user_guid,
            variant_key=event.variant_key,
            rendering_id=event.rendering_id,
            bundle_id=event.bundle_id,
            started=event.time,
            ended=event.time,
            data_version=event.data_version,
            path=event.path,
        )

    @staticmethod
    def from_shiny_usage_event(
        event: shiny_usage.ShinyUsageEvent,
    ) -> UsageEvent:
        return UsageEvent(
            event._ctx,
            content_guid=event.content_guid,
            user_guid=event.user_guid,
            variant_key=None,
            rendering_id=None,
            bundle_id=None,
            started=event.started,
            ended=event.ended,
            data_version=event.data_version,
            path=None,
        )

    @property
    def content_guid(self) -> str:
        """The associated unique content identifier.

        Returns
        -------
        str
        """
        return self["content_guid"]

    @property
    def user_guid(self) -> str:
        """The associated unique user identifier.

        Returns
        -------
        str
        """
        return self["user_guid"]

    @property
    def variant_key(self) -> str | None:
        """The variant key associated with the visit.

        Returns
        -------
        str | None
            The variant key, or None if the associated content type is static.
        """
        return self["variant_key"]

    @property
    def rendering_id(self) -> int | None:
        """The render id associated with the visit.

        Returns
        -------
        int | None
            The render id, or None if the associated content type is static.
        """
        return self["rendering_id"]

    @property
    def bundle_id(self) -> int | None:
        """The bundle id associated with the visit.

        Returns
        -------
        int
        """
        return self["bundle_id"]

    @property
    def started(self) -> str:
        """The visit timestamp.

        Returns
        -------
        str
        """
        return self["started"]

    @property
    def ended(self) -> str:
        """The visit timestamp.

        Returns
        -------
        str
        """
        return self["ended"]

    @property
    def data_version(self) -> int:
        """The data version.

        Returns
        -------
        int
        """
        return self["data_version"]

    @property
    def path(self) -> str | None:
        """The path requested by the user.

        Returns
        -------
        str
        """
        return self["path"]


class Usage(resources.Resources):
    """Usage resource."""

    @overload
    def find(
        self,
        *,
        content_guid: str = ...,
        min_data_version: int = ...,
        start: str = ...,
        end: str = ...,
    ) -> List[UsageEvent]:
        """Find view events.

        Parameters
        ----------
        content_guid : str, optional
            Filter by an associated unique content identifer, by default ...
        min_data_version : int, optional
            Filter by a minimum data version, by default ...
        start : str, optional
            Filter by the start time, by default ...
        end : str, optional
            Filter by the end time, by default ...

        Returns
        -------
        List[UsageEvent]
        """

    @overload
    def find(self, **kwargs) -> List[UsageEvent]:
        """Find view events.

        Returns
        -------
        List[UsageEvent]
        """

    def find(self, **kwargs) -> List[UsageEvent]:
        """Find view events.

        Returns
        -------
        List[UsageEvent]
        """
        events = []
        finders = (visits.Visits, shiny_usage.ShinyUsage)
        for finder in finders:
            instance = finder(self._ctx)
            events.extend(
                [UsageEvent.from_event(event) for event in instance.find(**kwargs)],
            )
        return events

    @overload
    def find_one(
        self,
        *,
        content_guid: str = ...,
        min_data_version: int = ...,
        start: str = ...,
        end: str = ...,
    ) -> UsageEvent | None:
        """Find a view event.

        Parameters
        ----------
        content_guid : str, optional
            Filter by an associated unique content identifer, by default ...
        min_data_version : int, optional
            Filter by a minimum data version, by default ...
        start : str, optional
            Filter by the start time, by default ...
        end : str, optional
            Filter by the end time, by default ...

        Returns
        -------
        Visit | None
        """

    @overload
    def find_one(self, **kwargs) -> UsageEvent | None:
        """Find a view event.

        Returns
        -------
        Visit | None
        """

    def find_one(self, **kwargs) -> UsageEvent | None:
        """Find a view event.

        Returns
        -------
        UsageEvent | None
        """
        finders = (visits.Visits, shiny_usage.ShinyUsage)
        for finder in finders:
            instance = finder(self._ctx)
            event = instance.find_one(**kwargs)
            if event:
                return UsageEvent.from_event(event)
        return None
