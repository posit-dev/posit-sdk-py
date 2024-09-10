"""OAuth session resources."""

from typing import List, Optional, overload

from ..resources import Resource, Resources


class Session(Resource):
    """OAuth session resource."""

    def delete(self) -> None:
        path = f"v1/oauth/sessions/{self['guid']}"
        url = self.params.url + path
        self.params.session.delete(url)


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
        response = self.params.session.get(url, params=kwargs)
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
        url = self.params.url + path
        response = self.params.session.get(url)
        return Session(self.params, **response.json())
