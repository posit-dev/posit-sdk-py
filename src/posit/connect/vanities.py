from typing import Callable, List, Optional, Union, overload

from posit.connect.errors import ClientError

from .resources import Resource, ResourceParameters, Resources

AfterDestroyCallback = Callable[[], None]


class Vanity(Resource):
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

    _fuid: str = "content_guid"
    """str : the foreign unique identifier field that points to the owner of this vanity, by default 'content_guid'"""

    def __init__(
        self,
        /,
        params: ResourceParameters,
        *,
        after_destroy: Optional[AfterDestroyCallback] = None,
        **kwargs,
    ):
        """Initialize a Vanity.

        Parameters
        ----------
        params : ResourceParameters
        after_destroy : AfterDestroyCallback, optional
            Called after the Vanity is successfully destroyed, by default None
        """
        super().__init__(params, **kwargs)
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
        fuid = self.get("content_guid")
        if fuid is None:
            raise ValueError("Missing value for required field: 'content_guid'.")
        endpoint = self.params.url + f"v1/content/{fuid}/vanity"
        self.params.session.delete(endpoint)

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
        endpoint = self.params.url + "v1/vanities"
        response = self.params.session.get(endpoint)
        results = response.json()
        return [Vanity(self.params, **result) for result in results]


class VanityMixin(Resource):
    """Mixin class to add a vanity attribute to a resource."""

    _uid: str = "guid"
    """str : the unique identifier field for this resource"""

    def __init__(self, /, params: ResourceParameters, **kwargs):
        super().__init__(params, **kwargs)
        self._vanity: Optional[Vanity] = None

    @property
    def vanity(self) -> Optional[Vanity]:
        """Retrieve or lazily load the associated vanity resource."""
        if self._vanity:
            return self._vanity

        try:
            v = self.get(self._uid)
            if v is None:
                raise ValueError(f"Missing value for required field: '{self._uid}'.")
            endpoint = self.params.url + f"v1/content/{v}/vanity"
            response = self.params.session.get(endpoint)
            result = response.json()
            self._vanity = Vanity(self.params, after_destroy=self.reset_vanity, **result)
            return self._vanity
        except ClientError as e:
            if e.http_status == 404:
                return None
            raise e

    @vanity.setter
    def vanity(self, value: Union[str, dict]) -> None:
        """Set the vanity.

        Parameters
        ----------
        value : str or dict
            The value can be a string or a dictionary. If provided as a string, it represents the vanity path. If provided as a dictionary, it contains key-value pairs with detailed information about the object.
        """
        if isinstance(value, str):
            self.set_vanity(path=value)
        elif isinstance(value, dict):
            self.set_vanity(**value)
        self.reset_vanity()

    @vanity.deleter
    def vanity(self) -> None:
        """Destroy the vanity.

        Warnings
        --------
        This operation is irreversible.

        Note
        ----
        This action requires administrator privileges.

        See Also
        --------
        reset_vanity
        """
        if self._vanity:
            self._vanity.destroy()
        self.reset_vanity()

    def reset_vanity(self) -> None:
        """Unload the cached vanity.

        Forces the next access, if any, to query the vanity from the Connect server.
        """
        self._vanity = None

    @overload
    def set_vanity(self, *, path: str) -> None:
        """Set the vanity.

        Parameters
        ----------
        path : str
            The vanity path.

        Raises
        ------
        ValueError
            If the unique identifier field is missing or the value is None.
        """
        ...

    @overload
    def set_vanity(self, *, path: str, force: bool) -> None:
        """Set the vanity.

        Parameters
        ----------
        path : str
            The vanity path.
        force : bool
            If `True`, overwrite the ownership of this vanity to this resource, default `False`

        Raises
        ------
        ValueError
            If the unique identifier field is missing or the value is None.
        """
        ...

    @overload
    def set_vanity(self, **attributes) -> None:
        """Set the vanity.

        Parameters
        ----------
        **attributes : dict, optional
            Arbitrary attributes. All attributes are passed as the request body to POST 'v1/content/:guid/vanity'

        Raises
        ------
        ValueError
            If the unique identifier field is missing or the value is None.
        """
        ...

    def set_vanity(self, **attributes) -> None:
        """Set the vanity.

        Parameters
        ----------
        **attributes : dict, optional
            Arbitrary attributes. All attributes are passed as the request body to POST 'v1/content/:guid/vanity'

        Raises
        ------
        ValueError
            If the unique identifier field is missing or the value is None.
        """
        v = self.get(self._uid)
        if v is None:
            raise ValueError(f"Missing value for required field: '{self._uid}'.")
        endpoint = self.params.url + f"v1/content/{v}/vanity"
        self.params.session.put(endpoint, json=attributes)
