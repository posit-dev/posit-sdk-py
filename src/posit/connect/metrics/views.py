from __future__ import annotations

import itertools

from typing import List

from requests.sessions import Session as Session

from . import usage, visits

from .. import resources


class ViewEvent(resources.Resource):
    @staticmethod
    def from_event(event: visits.VisitEvent | usage.UsageEvent) -> ViewEvent:
        if type(event) == visits.VisitEvent:
            return ViewEvent.from_visit_event(event)

        if type(event) == usage.UsageEvent:
            return ViewEvent.from_usage_event(event)

        raise TypeError

    @staticmethod
    def from_visit_event(event: visits.VisitEvent) -> ViewEvent:
        return ViewEvent(
            event.config,
            event.session,
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
    def from_usage_event(event: usage.UsageEvent) -> ViewEvent:
        return ViewEvent(
            event.config,
            event.session,
            content_guid=event.content_guid,
            user_guid=event.user_guid,
            started=event.started,
            ended=event.ended,
            data_version=event.data_version,
        )

    def __init__(self, config: resources.Config, session: Session, **kwargs):
        super().__init__(config, session, **kwargs)

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
        return self.get("variant_key")

    @property
    def rendering_id(self) -> int | None:
        """The render id associated with the visit.

        Returns
        -------
        int | None
            The render id, or None if the associated content type is static.
        """
        return self.get("rendering_id")

    @property
    def bundle_id(self) -> int | None:
        """The bundle id associated with the visit.

        Returns
        -------
        int
        """
        return self.get("bundle_id")

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
        return self.get("path")


class Views(resources.Resources):
    def find(self, *args, **kwargs) -> List[ViewEvent]:
        events = []
        finders = (visits.Visits, usage.Usage)
        for finder in finders:
            instance = finder(self.config, self.session)
            events.extend(
                [
                    ViewEvent.from_event(event)
                    for event in instance.find(*args, **kwargs)  # type: ignore[attr-defined]
                ]
            )
        return events

    def find_one(self, *args, **kwargs) -> ViewEvent | None:
        finders = (visits.Visits, usage.Usage)
        for finder in finders:
            instance = finder(self.config, self.session)
            event = instance.find_one(*args, **kwargs)  # type: ignore[attr-defined]
            if event:
                return ViewEvent.from_event(event)
        return None
