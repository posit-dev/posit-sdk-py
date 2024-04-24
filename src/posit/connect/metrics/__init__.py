from .. import resources

from . import views


class Metrics(resources.Resources):
    @property
    def views(self) -> views.Views:
        return views.Views(self.config, self.session)
