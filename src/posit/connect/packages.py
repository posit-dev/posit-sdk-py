from typing import Literal, Optional, Sequence, TypedDict

from typing_extensions import NotRequired, Required, Unpack

from .resources import Resource, ResourceParameters, Resources


class Package(Resource):
    """A package resource."""

    class PackageAttributes(TypedDict):
        """Package attributes."""

        language: Required[Literal["r", "python"]]
        name: Required[str]
        version: Required[str]
        hash: NotRequired[str]

    def __init__(self, params: ResourceParameters, **kwargs: Unpack[PackageAttributes]):
        super().__init__(params, **kwargs)


class Packages(Resources, Sequence[Package]):
    """A collection of packages."""

    def __init__(self, params, endpoint):
        super().__init__(params)
        self._endpoint = endpoint
        self._packages = []
        self.reload()

    def __getitem__(self, index):
        """Retrieve an item or slice from the sequence."""
        return self._packages[index]

    def __len__(self):
        """Return the length of the sequence."""
        return len(self._packages)

    def __repr__(self):
        """Return the string representation of the sequence."""
        return f"Packages({', '.join(map(str, self._packages))})"

    def count(self, value):
        """Return the number of occurrences of a value in the sequence."""
        return self._packages.count(value)

    def index(self, value, start=0, stop=None):
        """Return the index of the first occurrence of a value in the sequence."""
        if stop is None:
            stop = len(self._packages)
        return self._packages.index(value, start, stop)

    def reload(self) -> "Packages":
        """Reload packages from the Connect server.

        Returns
        -------
        List[Package]
        """
        response = self.params.session.get(self._endpoint)
        results = response.json()
        packages = [Package(self.params, **result) for result in results]
        self._packages = packages
        return self


class PackagesMixin(Resource):
    """Mixin class to add a packages to a resource."""

    class HasGuid(TypedDict):
        """Has a guid."""

        guid: Required[str]

    def __init__(self, params: ResourceParameters, **kwargs: Unpack[HasGuid]):
        super().__init__(params, **kwargs)
        self._guid = kwargs["guid"]
        self._packages: Optional[Packages] = None

    @property
    def packages(self) -> Packages:
        """Get the packages."""
        if self._packages:
            return self._packages

        endpoint = self.params.url + f"v1/content/{self._guid}/packages"
        self._packages = Packages(self.params, endpoint)
        return self._packages
