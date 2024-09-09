"""OAuth session resources."""

from typing import List, Optional, overload

from ..resources import Resource, Resources


class Session(Resource):
    """OAuth session resource.

    Attributes
    ----------
    id : str
        The internal numeric identifier of this OAuth session.
    guid : str
        The unique identifier of this OAuth session which is used in REST API requests.
    user_guid : str
        The unique identifier of the user that is associatid with this OAuth session.
    oauth_integration_guid : str
        The unique identifier of the OAuth integration that is associated with this OAuth session.
    has_refresh_token : bool
        Indicates whether this OAuth session has a refresh token.
    created_time : str
        The timestamp (RFC3339) indicating when this OAuth session was created.
    updated_time : str
        The timestamp (RFC3339) indicating when this OAuth session was last updated.
    """

    # Properties

    @property
    def id(self) -> str:
        return self.get("id")  # type: ignore

    @property
    def guid(self) -> str:
        return self.get("guid")  # type: ignore

    @property
    def user_guid(self) -> str:
        return self.get("user_guid")  # type: ignore

    @property
    def oauth_integration_guid(self) -> str:
        return self.get("oauth_integration_guid")  # type: ignore

    @property
    def has_refresh_token(self) -> bool:
        return self.get("has_refresh_token")  # type: ignore

    @property
    def created_time(self) -> str:
        return self.get("created_time")  # type: ignore

    @property
    def updated_time(self) -> str:
        return self.get("updated_time")  # type: ignore

    # CRUD Methods

    def delete(self) -> None:
        path = f"v1/oauth/sessions/{self.guid}"
        url = self.url + path
        self.session.delete(url)


class Sessions(Resources):
    @overload
    def find(
        self,
        *,
        all: Optional[bool] = ...,
    ) -> List[Session]: ...

    @overload
    def find(self, **kwargs) -> List[Session]: ...

    def find(self, **kwargs) -> List[Session]:
        url = self.params.url + "v1/oauth/sessions"
        response = self.session.get(url, params=kwargs)
        results = response.json()
        return [Session(self.params, **result) for result in results]

    def get(self, guid: str) -> Session:
        """Get an OAuth session.

        Parameters
        ----------
        guid: str

        Returns
        -------
        Session
        """
        path = f"v1/oauth/sessions/{guid}"
        url = self.url + path
        response = self.session.get(url)
        return Session(self.params, **response.json())
