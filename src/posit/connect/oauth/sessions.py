"""OAuth session resources."""

from typing_extensions import List, Optional, overload

from ..resources import BaseResource, Resources


class Session(BaseResource):
    """OAuth session resource."""

    def delete(self) -> None:
        path = f"v1/oauth/sessions/{self['guid']}"
        self._ctx.client.delete(path)


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
        path = "v1/oauth/sessions"
        response = self._ctx.client.get(path, params=kwargs)
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
        path = f"v1/oauth/sessions/{guid}"
        response = self._ctx.client.get(path)
        return Session(self._ctx, **response.json())
