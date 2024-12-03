"""OAuth session resources."""

from typing import List, Optional, overload

from typing_extensions import TypedDict, Unpack

from .._active import ActiveDict
from .._utils import assert_guid
from ..context import Context


class Session(ActiveDict):
    """OAuth session resource."""

    class _Attrs(TypedDict, total=False):
        id: str
        "The internal numeric identifier of this OAuth session."
        guid: str
        "The unique identifier of this OAuth session which is used in REST API requests."
        user_guid: str
        "The unique identifier of the user that is associated with this OAuth session."
        oauth_integration_guid: str
        "The unique identifier of the OAuth integration that is associated with this OAuth session."
        has_refresh_token: bool
        "Indicates whether this OAuth session has a refresh token."
        created_time: str
        "The timestamp (RFC3339) indicating when this OAuth session was created."
        updated_time: str
        "The timestamp (RFC3339) indicating when this OAuth session was last updated."

    @overload
    def __init__(self, ctx: Context, /, *, guid: str) -> None: ...

    """
    Retrieve an OAuth session by its unique identifier.

    Parameters
    ----------
    ctx : Context
        The context object containing the session and URL for API interactions.
    guid : str
        The unique identifier of the OAuth session.
    """

    @overload
    def __init__(self, ctx: Context, /, **kwargs: Unpack["Session._Attrs"]) -> None: ...

    """
    Retrieve an OAuth session by its unique identifier.

    Parameters
    ----------
    ctx : Context
        The context object containing the session and URL for API interactions.
    **kwargs : Session._Attrs
        Attributes for the OAuth session. If not supplied, the attributes will be retrieved from the API upon initialization.
    """

    def __init__(self, ctx: Context, /, **kwargs) -> None:
        guid = assert_guid(kwargs.get("guid"))
        path = self._api_path(guid)

        # Only fetch data if `kwargs` only contains `"guid"`
        get_data = len(kwargs) == 1

        super().__init__(ctx, path, get_data, **kwargs)

    # TODO-barret-future-q: Should this be destroy?
    def delete(self) -> None:
        """Destroy the OAuth session."""
        self._delete_api()

    @classmethod
    def _api_path(cls, session_guid: str) -> str:
        return f"v1/oauth/sessions/{session_guid}"


class Sessions:
    def __init__(self, ctx: Context) -> None:
        super().__init__()
        self._ctx = ctx

    # TODO-barret-future-q: Should this be `.all()`?
    @overload
    def find(
        self,
        *,
        all: Optional[bool] = ...,
    ) -> List[Session]: ...

    # TODO-barret-future-q: Should this be `.find_by()`?
    @overload
    def find(self, **kwargs) -> List[Session]: ...

    def find(self, **kwargs) -> List[Session]:
        url = self._ctx.url + "v1/oauth/sessions"
        response = self._ctx.session.get(url, params=kwargs)
        results = response.json()
        return [Session(self._ctx, **result) for result in results]

    def get(self, guid: str) -> Session:
        """Get an OAuth session.

        Parameters
        ----------
        guid: str

        Returns
        -------
        Session
        """
        return Session(self._ctx, guid=guid)
