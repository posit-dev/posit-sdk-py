"""Metric resources."""

from .. import resources
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
