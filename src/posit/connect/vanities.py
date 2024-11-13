from __future__ import annotations

from typing import Callable, Optional, Protocol

from typing_extensions import NotRequired, Required, TypedDict, Unpack

from ._types_content_item import ContentItemActiveDict, ContentItemContext, ContentItemP
from .errors import ClientError
from .resources import Resources, resource_parameters_to_content_item_context


class Vanity(ContentItemActiveDict):
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

    class _VanityAttributes(TypedDict):
        """Vanity attributes."""

        path: Required[str]
        created_time: Required[str]

    def __init__(
        self,
        /,
        ctx: ContentItemContext,
        *,
        after_destroy: Optional[AfterDestroyCallback] = None,
        **kwargs: Unpack[_VanityAttributes],
    ):
        """Initialize a Vanity.

        Parameters
        ----------
        params : ResourceParameters
        after_destroy : AfterDestroyCallback, optional
            Called after the Vanity is successfully destroyed, by default None
        """
        path = f"v1/content/{ctx.content_guid}/vanity"
        get_data = len(kwargs) == 0
        super().__init__(ctx, path, get_data, **kwargs)

        self._after_destroy = after_destroy

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
        self._delete_api()
        if self._after_destroy:
            self._after_destroy()


class Vanities(Resources):
    """Manages a collection of vanities."""

    def all(self) -> list[Vanity]:
        """Retrieve all vanities.

        Returns
        -------
        List[Vanity]

        Notes
        -----
        This action requires administrator privileges.
        """
        endpoint = self.params.url + "v1/vanities"
        response = self.params.session.get(endpoint)
        results = response.json()
        ret: list[Vanity] = []
        for result in results:
            assert isinstance(result, dict)
            assert "content_guid" in result

            ret.append(
                Vanity(
                    resource_parameters_to_content_item_context(
                        self.params,
                        content_guid=result["content_guid"],
                    ),
                    **result,
                )
            )
        return ret


class ContentItemVanityP(ContentItemP, Protocol):
    _vanity: Vanity | None

    def find_vanity(self) -> Vanity: ...

    def create_vanity(
        self, **kwargs: Unpack["ContentItemVanityMixin._CreateVanityRequest"]
    ) -> Vanity: ...

    def reset_vanity(self) -> None: ...

    @property
    def vanity(self) -> Optional[str]: ...

    @vanity.setter
    def vanity(self, value: str) -> None: ...

    @vanity.deleter
    def vanity(self) -> None: ...


class ContentItemVanityMixin:
    """Class to add a vanity attribute to a resource."""

    @property
    def vanity(self: ContentItemVanityP) -> str | None:
        """Get the vanity."""
        if hasattr(self, "_vanity") and self._vanity:
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
    def vanity(self: ContentItemVanityP, value: str) -> None:
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
    def vanity(self: ContentItemVanityP) -> None:
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

    def reset_vanity(self: ContentItemVanityP) -> None:
        """Unload the cached vanity.

        Forces the next access, if any, to query the vanity from the Connect server.
        """
        self._vanity = None

    class _CreateVanityRequest(TypedDict, total=False):
        """A request schema for creating a vanity."""

        path: Required[str]
        """The vanity path (e.g., 'my-dashboard')"""

        force: NotRequired[bool]
        """Whether to force creation of the vanity"""

    def create_vanity(self: ContentItemVanityP, **kwargs: Unpack[_CreateVanityRequest]) -> Vanity:
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
        endpoint = self._ctx.url + f"v1/content/{self._ctx.content_guid}/vanity"
        response = self._ctx.session.put(endpoint, json=kwargs)
        result = response.json()
        return Vanity(self._ctx, **result)

    def find_vanity(self: ContentItemVanityP) -> Vanity:
        """Find the vanity.

        Returns
        -------
        Vanity
        """
        endpoint = self._ctx.url + f"v1/content/{self._ctx.content_guid}/vanity"
        response = self._ctx.session.get(endpoint)
        result = response.json()
        return Vanity(self._ctx, **result)
