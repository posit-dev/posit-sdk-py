"""Metric resources."""

from .._types_context import ContextP
from ..context import Context
from .usage import Usage


class Metrics(ContextP[Context]):
    """Metrics resource.

    Attributes
    ----------
    usage: Usage
        Usage resource.
    """

    def __init__(self, ctx: Context):
        super().__init__()
        self._ctx = ctx

    @property
    def usage(self) -> Usage:
        return Usage(self._ctx)
