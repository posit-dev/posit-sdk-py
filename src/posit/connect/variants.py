import warnings

from typing_extensions import List, Literal

from .context import Context
from .resources import BaseResource, Resources
from .tasks import Task


class Variant(BaseResource):
    def render(self) -> Task:
        path = f"variants/{self['id']}/render"
        response = self._ctx.client.post(path)
        return Task(self._ctx, **response.json())

    def send_mail(
        self, to: Literal["me", "collaborators", "collaborators_viewers"] = "me"
    ) -> None:
        """Send email for this variant.

        Parameters
        ----------
        to : Literal["me", "collaborators", "collaborators_viewers"], optional
            The recipient type for the email. Default is "me".

        Returns
        -------
        None

        Warnings
        --------
            This operation is experimental.
        """
        warnings.warn(
            "send_mail() is experimental and may change in future releases.",
            FutureWarning,
            stacklevel=2,
        )
        path = f"variants/{self['id']}/sender"
        params = {
            "email": to,
            "rendering_id": self["rendering_id"],
        }
        self._ctx.client.post(path, params=params)


class Variants(Resources):
    def __init__(self, ctx: Context, content_guid: str) -> None:
        super().__init__(ctx)
        self.content_guid = content_guid

    def find(self) -> List[Variant]:
        path = f"applications/{self.content_guid}/variants"
        response = self._ctx.client.get(path)
        results = response.json() or []
        return [Variant(self._ctx, **result) for result in results]
