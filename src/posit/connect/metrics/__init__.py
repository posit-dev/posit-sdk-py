from .. import resources

from . import usage


class Metrics(resources.Resources):
    @property
    def usage(self) -> usage.Usage:
        return usage.Usage(self.config, self.session)
