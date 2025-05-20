"""Metric resources."""

from .. import resources
from ..context import requires
from .hits import Hits, _Hits
from .usage import Usage


class Metrics(resources.Resources):
    """Metrics resource.

    Attributes
    ----------
    usage: Usage
        Usage resource.
    """

    @property
    def usage(self) -> Usage:
        return Usage(self._ctx)

    @property
    @requires(version="2025.04.0")
    def hits(self) -> Hits:
        return _Hits(self._ctx, "v1/instrumentation/content/hits", uid="id")
