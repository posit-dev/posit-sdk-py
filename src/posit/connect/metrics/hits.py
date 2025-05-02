from typing_extensions import (
    Iterable,
    List,
    Literal,
    Protocol,
    overload,
)

from ..context import requires
from ..resources import Resource, ResourceSequence


class Hit(Resource, Protocol):
    pass


class Hits(ResourceSequence[Hit], Protocol):
    pass


# TODO:
# fetch, find_by documentation
# - fetch function args are gonna be the query params
# - find_by is the object props
#   if the server fails with extra query params that'd be bad.
# tests
# - reference packages_test file
