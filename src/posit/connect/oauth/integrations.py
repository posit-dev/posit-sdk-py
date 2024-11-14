"""OAuth integration resources."""

from typing import List, Optional, cast, overload

from typing_extensions import TypedDict, Unpack

from .._active import ActiveDict
from .._api_call import ApiCallMixin
from .._json import JsonifiableList
from .._types_context import ContextP
from .._utils import assert_guid
from ..context import Context
from ._types_context_integration import IntegrationContext
from .associations import IntegrationAssociations


class Integration(ActiveDict[IntegrationContext]):
    """OAuth integration resource."""

    def __init__(self, ctx: Context, /, *, guid: str, **kwargs):
        guid = assert_guid(guid)

        integration_ctx = IntegrationContext(ctx, integration_guid=guid)
        path = f"v1/oauth/integrations/{guid}"
        get_data = len(kwargs) == 0  # `guid` is required
        super().__init__(integration_ctx, path, get_data, guid=guid, **kwargs)

    @property
    def associations(self) -> IntegrationAssociations:
        return IntegrationAssociations(
            self._ctx,
        )

    def delete(self) -> None:
        """Delete the OAuth integration."""
        path = f"v1/oauth/integrations/{self['guid']}"
        url = self._ctx.url + path
        self._ctx.session.delete(url)

    class _AttrsUpdate(TypedDict, total=False):
        name: str
        description: str
        config: dict

    def update(
        self,
        **kwargs: Unpack[_AttrsUpdate],
    ) -> "Integration":
        """Update the OAuth integration.

        Parameters
        ----------
        name: str, optional
            A descriptive name to identify each OAuth integration.
        description: str, optional
            A brief text to describe each OAuth integration.
        config: dict, optional
            The OAuth integration configuration based on the template. See List OAuth templates for
            more information on available fields for each template. The configuration combines
            elements from both options and fields from a given template.
        """
        result = self._patch_api(json=kwargs)
        return Integration(self._ctx, **result)


# TODO-barret; Should this auto retrieve? If so, it should inherit from ActiveSequence
class Integrations(ApiCallMixin, ContextP[Context]):
    """Integrations resource."""

    @classmethod
    def _api_path(cls) -> str:
        return "v1/oauth/integrations"

    def __init__(self, ctx: Context) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = self._api_path()

    @overload
    def create(
        self,
        *,
        name: str,
        description: Optional[str],
        template: str,
        config: dict,
    ) -> Integration:
        """Create an OAuth integration.

        Parameters
        ----------
        name : str
        description : Optional[str]
        template : str
        config : dict

        Returns
        -------
        Integration
        """

    @overload
    def create(self, **kwargs) -> Integration:
        """Create an OAuth integration.

        Returns
        -------
        Integration
        """

    def create(self, **kwargs) -> Integration:
        """Create an OAuth integration.

        Parameters
        ----------
        name : str
        description : Optional[str]
        template : str
        config : dict

        Returns
        -------
        Integration
        """
        result = self._post_api(json=kwargs)
        assert result is not None, "Integration creation failed"
        return Integration(self._ctx, **result)

    def find(self) -> List[Integration]:
        """Find OAuth integrations.

        Returns
        -------
        List[Integration]
        """
        results = self._get_api()
        results_list = cast(JsonifiableList, results)

        return [
            Integration(
                self._ctx,
                **result,
            )
            for result in results_list
        ]

    def get(self, guid: str) -> Integration:
        """Get an OAuth integration.

        Parameters
        ----------
        guid: str

        Returns
        -------
        Integration
        """
        result = self._get_api(guid)
        return Integration(self._ctx, **result)
