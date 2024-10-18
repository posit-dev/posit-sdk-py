from typing import List, Sequence, TypedDict

from typing_extensions import Required, Unpack

from .resources import Resource, ResourceParameters, Resources


class Job(Resource):
    pass


class Jobs(Resources, Sequence[Job]):
    """A collection of jobs."""

    def __init__(self, params, endpoint):
        super().__init__(params)
        self._endpoint = endpoint
        self._cache = None

    @property
    def _data(self) -> List[Job]:
        if self._cache:
            return self._cache

        response = self.params.session.get(self._endpoint)
        results = response.json()
        self._cache = [Job(self.params, **result) for result in results]
        return self._cache

    def __getitem__(self, index):
        """Retrieve an item or slice from the sequence."""
        return self._data[index]

    def __len__(self):
        """Return the length of the sequence."""
        return len(self._data)

    def __repr__(self):
        """Return the string representation of the sequence."""
        return f"Jobs({', '.join(map(str, self._data))})"

    def count(self, value):
        """Return the number of occurrences of a value in the sequence."""
        return self._data.count(value)

    def index(self, value, start=0, stop=None):
        """Return the index of the first occurrence of a value in the sequence."""
        if stop is None:
            stop = len(self._data)
        return self._data.index(value, start, stop)

    def reload(self) -> "Jobs":
        """Unload the cached jobs.

        Forces the next access, if any, to query the jobs from the Connect server.
        """
        self._cache = None
        return self


class JobsMixin(Resource):
    """Mixin class to add a jobs attribute to a resource."""

    class HasGuid(TypedDict):
        """Has a guid."""

        guid: Required[str]

    def __init__(self, params: ResourceParameters, **kwargs: Unpack[HasGuid]):
        super().__init__(params, **kwargs)
        uid = kwargs["guid"]
        endpoint = self.params.url + f"v1/content/{uid}/jobs"
        self.jobs = Jobs(self.params, endpoint)
