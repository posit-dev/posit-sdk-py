from .resources import (
    ActiveCreatorMethods,
    ActiveDestroyerMethods,
    ActiveFinderMethods,
    ActiveUpdaterMethods,
)


class Environment(ActiveUpdaterMethods, ActiveDestroyerMethods):
    pass


class Environments(ActiveFinderMethods[Environment], ActiveCreatorMethods[Environment]):
    def __init__(self, ctx, path, pathinfo="environments", uid="guid"):
        super().__init__(ctx, path, pathinfo, uid)

    def _create_instance(self, path, pathinfo, /, **attributes):
        return Environment(self._ctx, path, pathinfo, **attributes)
