from __future__ import annotations

from typing_extensions import (
    Iterable,
    Protocol,
)

from ..resources import Resource, ResourceSequence, _ResourceSequence
from .rename_params import rename_params


class Hit(Resource, Protocol):
    pass


class Hits(ResourceSequence[Hit], Protocol):
    def fetch(
        self,
        *,
        start: str = ...,
        end: str = ...,
    ) -> Iterable[Hit]:
        """
        Fetch all content hit records matching the specified conditions.

        Parameters
        ----------
        start : str, not required
            The timestamp that starts the time window of interest in RFC 3339 format.
            Any hit information that happened prior to this timestamp will not be returned.
            Example: "2025-05-01T00:00:00Z"
        end : str, not required
            The timestamp that ends the time window of interest in RFC 3339 format.
            Any hit information that happened after this timestamp will not be returned.
            Example: "2025-05-02T00:00:00Z"

        Returns
        -------
        Iterable[Hit]
            All content hit records matching the specified conditions.
        """
        ...

    def find_by(
        self,
        *,
        id: str = ...,  # noqa: A002
        content_guid: str = ...,
        user_guid: str = ...,
        timestamp: str = ...,
    ) -> Hit | None:
        """
        Find the first hit record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        Parameters
        ----------
        id : str, not required
            The ID of the activity record.
        content_guid : str, not required
            The GUID, in RFC4122 format, of the content this information pertains to.
        user_guid : str, not required
            The GUID, in RFC4122 format, of the user that visited the content.
            May be null when the target content does not require a user session.
        timestamp : str, not required
            The timestamp, in RFC 3339 format, when the user visited the content.

        Returns
        -------
        Hit | None
            The first hit record matching the specified conditions, or `None` if no such record exists.
        """
        ...


class _Hits(_ResourceSequence, Hits):
    def fetch(
        self,
        **kwargs,
    ) -> Iterable[Hit]:
        """
        Fetch all content hit records matching the specified conditions.

        Parameters
        ----------
        start : str, not required
            The timestamp that starts the time window of interest in RFC 3339 format.
            Any hit information that happened prior to this timestamp will not be returned.
            This corresponds to the `from` parameter in the API.
            Example: "2025-05-01T00:00:00Z"
        end : str, not required
            The timestamp that ends the time window of interest in RFC 3339 format.
            Any hit information that happened after this timestamp will not be returned.
            This corresponds to the `to` parameter in the API.
            Example: "2025-05-02T00:00:00Z"

        Returns
        -------
        Iterable[Hit]
            All content hit records matching the specified conditions.
        """
        params = rename_params(kwargs)
        return super().fetch(**params)
