"""Metric resources."""

from .. import resources
from .shiny_usage import ShinyUsage
from .usage import Usage
from .visits import Visits


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
    def visits(self) -> Visits:
        return Visits(self._ctx)

    @property
    def shiny_usage(self) -> ShinyUsage:
        return ShinyUsage(self._ctx)
