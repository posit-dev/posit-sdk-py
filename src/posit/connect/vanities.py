from typing import Optional, TypedDict, overload

from typing_extensions import NotRequired, Required, Unpack

from .errors import ClientError
from .resources import (
    Active,
    ActiveDestroyMethods,
    ActiveFinderMethods,
    Resource,
)


class Vanity(ActiveDestroyMethods):
    """A vanity resource.

    Vanities maintain custom URL paths assigned to content.

    Warnings
    --------
    Vanity paths may only contain alphanumeric characters, hyphens, underscores, and slashes.

    Vanities cannot have children. For example, if the vanity path "/finance/" exists, the vanity path "/finance/budget/" cannot. But, if "/finance" does not exist, both "/finance/budget/" and "/finance/report" are allowed.

    The following vanities are reserved by Connect:
    - `/__`
    - `/favicon.ico`
    - `/connect`
    - `/apps`
    - `/users`
    - `/groups`
    - `/setpassword`
    - `/user-completion`
    - `/confirm`
    - `/recent`
    - `/reports`
    - `/plots`
    - `/unpublished`
    - `/settings`
    - `/metrics`
    - `/tokens`
    - `/help`
    - `/login`
    - `/welcome`
    - `/register`
    - `/resetpassword`
    - `/content`
    """

    class _Vanity(TypedDict):
        """Vanity attributes."""

        path: Required[str]
        """The URL path."""

        content_guid: Required[str]
        """Identifier of content associated with the vanity."""

        created_time: Required[str]
        """RFC3339 timestamp indicating when the vanity was created."""

    def __init__(self, ctx, **kwargs: Unpack[_Vanity]):
        super().__init__(ctx, **kwargs)

    @property
    def _endpoint(self):
        return self._ctx.url + f"v1/content/{self['content_guid']}/vanity"


class Vanities(ActiveFinderMethods[Vanity]):
    """A collection of vanities."""

    def __init__(self, ctx):
        super().__init__(Vanity, ctx)

    @property
    def _endpoint(self) -> str:
        return self._ctx.url + f"v1/vanities"

    def find(self, uid):
        """The 'find' method is not supported.

        Raises
        ------
        AttributeError
            Raised to indicate that the 'find' method is not supported in this subclass.
        """
        raise AttributeError(f"'{self.__class__.__name__}' does not support 'find'")

    class _FindByRequest(TypedDict, total=False):
        path: NotRequired[str]
        """The URL path."""

        content_guid: NotRequired[str]
        """Identifier of content associated with the vanity."""

        created_time: NotRequired[str]
        """RFC3339 timestamp indicating when the vanity was created."""

    @overload
    def find_by(self, **conditions: Unpack[_FindByRequest]) -> Optional[Vanity]:
        """Finds the first record matching the specified conditions.

        There is no implied ordering so if order matters, you should specify it yourself.

        Parameters
        ----------
        path: str, not required
            The URL path.
        content_guid: str, not required
            Identifier of content associated with the vanity.
        created_time: str, not required
            RFC3339 timestamp indicating when the vanity was created.

        Returns
        -------
        Optional[Vanity]
        """
        ...

    @overload
    def find_by(self, **conditions) -> Optional[Vanity]: ...

    def find_by(self, **conditions) -> Optional[Vanity]:
        return super().find_by(**conditions)


class VanityMixin(Active, Resource):
    """Mixin class to add a vanity attribute to a resource."""

    def __init__(self, ctx, **kwargs):
        super().__init__(ctx, **kwargs)
        self._vanity: Optional[Vanity] = None

    @property
    def _endpoint(self):
        return self.params.url + f"v1/content/{self['guid']}/vanity"

    @property
    def vanity(self) -> Optional[str]:
        """Get the vanity."""
        if self._vanity:
            return self._vanity["path"]

        try:
            self._vanity = self.find_vanity()
            self._vanity._after_destroy = self.reset_vanity
            return self._vanity["path"]
        except ClientError as e:
            if e.http_status == 404:
                return None
            raise e

    @vanity.setter
    def vanity(self, value: str) -> None:
        """Set the vanity.

        Parameters
        ----------
        value : str
            The vanity path.

        Note
        ----
        This action requires owner or administrator privileges.

        See Also
        --------
        create_vanity
        """
        self._vanity = self.create_vanity(path=value)
        self._vanity._after_destroy = self.reset_vanity

    @vanity.deleter
    def vanity(self) -> None:
        """Destroy the vanity.

        Warnings
        --------
        This operation is irreversible.

        Note
        ----
        This action requires owner or administrator privileges.

        See Also
        --------
        reset_vanity
        """
        self.vanity
        if self._vanity:
            self._vanity.destroy()
        self.reset_vanity()

    def reset_vanity(self) -> None:
        """Unload the cached vanity.

        Forces the next access, if any, to query the vanity from the Connect server.
        """
        self._vanity = None

    class CreateVanityRequest(TypedDict, total=False):
        """A request schema for creating a vanity."""

        path: Required[str]
        """The vanity path (e.g., 'my-dashboard')"""

        force: NotRequired[bool]
        """Whether to force creation of the vanity"""

    def create_vanity(self, **kwargs: Unpack[CreateVanityRequest]) -> Vanity:
        """Create a vanity.

        Parameters
        ----------
        path : str, required
            The path for the vanity.
        force : bool, not required
            Whether to force the creation of the vanity. When True, any other vanity with the same path will be deleted.

        Warnings
        --------
        If setting force=True, the destroy operation performed on the other vanity is irreversible.
        """
        response = self.params.session.put(self._endpoint, json=kwargs)
        result = response.json()
        return Vanity(self._ctx, **result)

    def find_vanity(self) -> Vanity:
        """Find the vanity.

        Returns
        -------
        Vanity
        """
        response = self.params.session.get(self._endpoint)
        result = response.json()
        return Vanity(self._ctx, **result)
