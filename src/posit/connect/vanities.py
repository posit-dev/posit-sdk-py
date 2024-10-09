from typing import Callable, Optional, Union, overload

from .resources import Resource, ResourceParameters, Resources

AfterDestroyCallback = Callable[[], None]


class Vanity(Resource):
    """Represents a Vanity resource with the ability to destroy itself."""

    def __init__(
        self,
        /,
        params: ResourceParameters,
        *,
        after_destroy: AfterDestroyCallback = lambda: None,
        **kwargs,
    ):
        super().__init__(params, **kwargs)
        self._after_destroy = after_destroy

    def destroy(self) -> None:
        """Destroy the vanity resource."""
        content_guid = self.get("content_guid")
        if content_guid is None:
            raise ValueError(
                "The 'content_guid' is missing. Unable to perform the destroy operation."
            )
        endpoint = self.params.url + f"v1/content/{content_guid}/vanity"
        self.params.session.delete(endpoint)
        self._after_destroy()


class Vanities(Resources):
    """Manages a collection of Vanity resources."""

    def all(self) -> list[Vanity]:
        """Retrieve all vanity resources."""
        endpoint = self.params.url + "v1/vanities"
        response = self.params.session.get(endpoint)
        results = response.json()
        return [Vanity(self.params, **result) for result in results]


class VanityMixin(Resource):
    """Mixin class to add vanity management capabilities to a resource."""

    def __init__(self, /, params: ResourceParameters, **kwargs):
        super().__init__(params, **kwargs)
        self._vanity: Optional[Vanity] = None

    @property
    def vanity(self) -> Vanity:
        """Retrieve or lazily load the associated vanity resource."""
        if self._vanity is None:
            uid = self.get("guid")
            if uid is None:
                raise ValueError(
                    "The 'guid' is missing. Unable to perform the get vanity operation."
                )
            endpoint = self.params.url + f"v1/content/{uid}/vanity"
            response = self.params.session.get(endpoint)
            result = response.json()
            self._vanity = Vanity(
                self.params, after_destroy=lambda: setattr(self, "_vanity", None), **result
            )
        return self._vanity

    @vanity.setter
    def vanity(self, value: Union[str, dict]) -> None:
        """Set the vanity using a path or dictionary of attributes."""
        if isinstance(value, str):
            self.set_vanity(path=value)
        elif isinstance(value, dict):
            self.set_vanity(**value)
        self.reset()

    @vanity.deleter
    def vanity(self) -> None:
        """Delete the vanity resource."""
        if self._vanity:
            self._vanity.destroy()
        self.reset()

    def reset(self) -> None:
        """Reset the cached vanity resource."""
        self._vanity = None

    @overload
    def set_vanity(self, *, path: str) -> None: ...

    @overload
    def set_vanity(self, *, path: str, force: bool) -> None: ...

    @overload
    def set_vanity(self, **attributes) -> None: ...

    def set_vanity(self, **attributes) -> None:
        """Set or update the vanity resource with given attributes."""
        uid = self.get("guid")
        if uid is None:
            raise ValueError("The 'guid' is missing. Unable to perform the set vanity operation.")
        endpoint = self.params.url + f"v1/content/{uid}/vanity"
        self.params.session.put(endpoint, json=attributes)
