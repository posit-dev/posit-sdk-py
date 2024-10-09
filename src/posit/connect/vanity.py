from typing import Callable, Optional

from .context import Context

AfterDestroyCallback = Callable[[], None]


class Vanity(dict):
    def __init__(
        self, ctx: Context, *, after_destroy: AfterDestroyCallback = lambda: None, **kwargs
    ):
        super().__init__(**kwargs)
        self._ctx = ctx
        self._after_destroy = after_destroy

    def destroy(self):
        url = self._ctx.url + f"v1/content/{self['content_guid']}/vanity"
        self._ctx.session.delete(url)
        self._after_destroy()


class Vanities:
    def __init__(self, ctx: Context) -> None:
        self._ctx = ctx

    def all(self) -> list[Vanity]:
        url = self._ctx.url + f"v1/vanities"
        response = self._ctx.session.get(url)
        results = response.json()
        return [Vanity(self._ctx, **result) for result in results]


class VanityContentMixin(dict):
    def __init__(self, ctx: Context, **kwargs):
        super().__init__(**kwargs)
        self._ctx = ctx
        self._vanity: Optional[Vanity] = None

    @property
    def vanity(self) -> Vanity:
        if self._vanity is None:
            url = self._ctx.url + f"v1/content/{self['guid']}/vanity"
            response = self._ctx.session.get(url)
            vanity_data = response.json()
            # Set the after_destroy callback to reset _vanity to None when destroyed
            after_destroy = lambda: setattr(self, "_vanity", None)
            self._vanity = Vanity(self._ctx, after_destroy=after_destroy, **vanity_data)
        return self._vanity

    @vanity.setter
    def vanity(self, value: dict):
        url = self._ctx.url + f"v1/content/{self['guid']}/vanity"
        self._ctx.session.put(url, json=value)
        # Refresh the vanity property to reflect the updated value
        self._vanity = self.vanity

    @vanity.deleter
    def vanity(self):
        if self._vanity:
            self._vanity.destroy()
