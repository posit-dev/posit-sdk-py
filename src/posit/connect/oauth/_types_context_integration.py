"""OAuth integration resources."""

from ..context import Context


class IntegrationContext(Context):
    integration_guid: str

    def __init__(self, ctx: Context, /, *, integration_guid: str) -> None:
        super().__init__(ctx.session, ctx.url)
        self.integration_guid = integration_guid
