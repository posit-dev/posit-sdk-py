"""Vanity URL resources."""

from typing_extensions import Callable, List, NotRequired, Optional, Required, TypedDict, Unpack

from .context import Context
from .errors import ClientError
from .resources import BaseResource, Resources


class Vanity(BaseResource):
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

    AfterDestroyCallback = Callable[[], None]

    class VanityAttributes(TypedDict):
        """Vanity attributes."""

        path: Required[str]
        content_guid: Required[str]
        created_time: Required[str]

    def __init__(
        self,
        /,
        ctx: Context,
        *,
        after_destroy: Optional[AfterDestroyCallback] = None,
        **kwargs: Unpack[VanityAttributes],
    ):
        """Initialize a Vanity.

        Parameters
        ----------
        ctx : Context
        after_destroy : AfterDestroyCallback, optional
            Called after the Vanity is successfully destroyed, by default None
        """
        super().__init__(ctx, **kwargs)
        self._after_destroy = after_destroy
        self._content_guid = kwargs["content_guid"]

    def destroy(self) -> None:
        """Destroy the vanity.

        Raises
        ------
        ValueError
            If the foreign unique identifier is missing or its value is `None`.

        Warnings
        --------
        This operation is irreversible.

        Note
        ----
        This action requires administrator privileges.
        """
        path = f"v1/content/{self._content_guid}/vanity"
        self._ctx.client.delete(path)

        if self._after_destroy:
            self._after_destroy()


class Vanities(Resources):
    """Manages a collection of vanities."""

    def all(self) -> List[Vanity]:
        """Retrieve all vanities.

        Returns
        -------
        List[Vanity]

        Notes
        -----
        This action requires administrator privileges.
        """
        path = "v1/vanities"
        response = self._ctx.client.get(path)
        results = response.json()
        return [Vanity(self._ctx, **result) for result in results]


class VanityMixin(BaseResource):
    """Mixin class to add a vanity attribute to a resource."""

    class HasGuid(TypedDict):
        """Has a guid."""

        guid: Required[str]

    def __init__(self, ctx: Context, **kwargs: Unpack[HasGuid]):
        super().__init__(ctx, **kwargs)
        self._content_guid = kwargs["guid"]
        self._vanity: Optional[Vanity] = None

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
        # Populate value
        self.vanity  # noqa: B018

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
        path = f"v1/content/{self._content_guid}/vanity"
        response = self._ctx.client.put(path, json=kwargs)
        result = response.json()
        return Vanity(self._ctx, **result)

    def find_vanity(self) -> Vanity:
        """Find the vanity.

        Returns
        -------
        Vanity
        """
        path = f"v1/content/{self._content_guid}/vanity"
        response = self._ctx.client.get(path)
        result = response.json()
        return Vanity(self._ctx, **result)
