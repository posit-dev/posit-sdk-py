"""Content resources."""

from __future__ import annotations

import posixpath
import time
from posixpath import dirname
from typing import (
    TYPE_CHECKING,
    Any,
    List,
    Literal,
    Optional,
    cast,
    overload,
)

from typing_extensions import NotRequired, Required, TypedDict, Unpack

from . import tasks
from ._content_repository import ContentItemRepository
from ._json import JsonifiableDict
from ._types_content_item import ContentItemActiveDict, ContentItemContext, ContentItemResourceDict
from ._utils import assert_guid
from .bundles import Bundles
from .context import Context
from .env import EnvVars
from .errors import ClientError
from .jobs import JobsMixin
from .oauth.associations import ContentItemAssociations
from .packages import ContentPackagesMixin as PackagesMixin
from .permissions import Permissions
from .resources import ResourceParameters, Resources, context_to_resource_parameters
from .vanities import ContentItemVanityMixin
from .variants import Variants

if TYPE_CHECKING:
    from .tasks import Task
    from .users import User


class ContentItemOAuth(ContentItemResourceDict):
    def __init__(self, ctx: ContentItemContext) -> None:
        super().__init__(ctx)

    @property
    def associations(self) -> ContentItemAssociations:
        return ContentItemAssociations(
            context_to_resource_parameters(self._ctx),
            content_guid=self._ctx.content_guid,
        )


class ContentItemOwner(ContentItemResourceDict):
    pass


class ContentItem(JobsMixin, PackagesMixin, ContentItemVanityMixin, ContentItemActiveDict):
    class _AttrsBase(TypedDict, total=False):
        # # `name` will be set by other _Attrs classes
        # name: str

        # Content Metadata
        title: NotRequired[str]
        description: NotRequired[str]
        access_type: NotRequired[Literal["all", "acl", "logged_in"]]
        # Timeout Settings
        connection_timeout: NotRequired[int]
        read_timeout: NotRequired[int]
        init_timeout: NotRequired[int]
        idle_timeout: NotRequired[int]
        # Process and Resource Limits
        max_processes: NotRequired[int]
        min_processes: NotRequired[int]
        max_conns_per_process: NotRequired[int]
        load_factor: NotRequired[float]
        cpu_request: NotRequired[float]
        cpu_limit: NotRequired[float]
        memory_request: NotRequired[int]
        memory_limit: NotRequired[int]
        amd_gpu_limit: NotRequired[int]
        nvidia_gpu_limit: NotRequired[int]
        # Execution Settings
        run_as: NotRequired[str]
        run_as_current_user: NotRequired[bool]
        default_image_name: NotRequired[str]
        default_r_environment_management: NotRequired[bool]
        default_py_environment_management: NotRequired[bool]
        service_account_name: NotRequired[str]

    class _AttrsNotRequired(_AttrsBase):
        name: NotRequired[str]
        owner_guid: NotRequired[str]

    class _Attrs(_AttrsBase):
        name: Required[str]
        owner_guid: NotRequired[str]

    class _AttrsCreate(_AttrsBase):
        name: NotRequired[str]
        # owner_guid is not supported

    @overload
    def __init__(
        self,
        /,
        params: ResourceParameters,
        guid: str,
    ) -> None: ...

    @overload
    def __init__(
        self,
        /,
        params: ResourceParameters,
        guid: str,
        **kwargs: Unpack[ContentItem._Attrs],
    ) -> None: ...

    def __init__(
        self,
        /,
        params: ResourceParameters,
        guid: str,
        **kwargs: Unpack[ContentItem._AttrsNotRequired],
    ) -> None:
        assert_guid(guid)

        ctx = ContentItemContext(Context(params.session, params.url), content_guid=guid)
        path = f"v1/content/{guid}"
        get_data = len(kwargs) == 0

        super().__init__(ctx, path, get_data, guid=guid, **kwargs)

    def __getitem__(self, key: Any) -> Any:
        v = super().__getitem__(key)
        # TODO-barret-Q: Why isn't this a property?
        if key == "owner" and isinstance(v, dict):
            return ContentItemOwner(self._ctx, **v)
        return v

    @property
    def oauth(self) -> ContentItemOAuth:
        return ContentItemOAuth(self._ctx)

    @property
    def repository(self) -> ContentItemRepository | None:
        try:
            return ContentItemRepository(self._ctx)
        except ClientError:
            return None

    def create_repository(
        self,
        **attrs: Unpack[ContentItemRepository._Attrs],
    ) -> ContentItemRepository:
        """Create repository.

        Parameters
        ----------
        repository : str
            URL for the respository.
        branch : str, optional
            The tracked Git branch. Default is 'main'.
        directory : str, optional
            Directory containing the content. Default is '.'.
        polling : bool, optional
            Indicates that the Git repository is regularly polled. Default is False.

        Returns
        -------
        ContentItemRepository
        """
        return ContentItemRepository._create(self._ctx, self["guid"], **attrs)

    # Rename to destroy()?
    def delete(self) -> None:
        """Delete the content item."""
        self._delete_api()

    def deploy(self) -> tasks.Task:
        """Deploy the content.

        Spawns an asynchronous task, which activates the latest bundle.

        Returns
        -------
        tasks.Task
            The task for the deployment.

        Examples
        --------
        >>> task = content.deploy()
        >>> task.wait_for()
        None
        """
        path = f"v1/content/{self['guid']}/deploy"
        url = self._ctx.url + path
        response = self._ctx.session.post(url, json={"bundle_id": None})
        result = response.json()
        ts = tasks.Tasks(context_to_resource_parameters(self._ctx))
        return ts.get(result["task_id"])

    def render(self) -> Task:
        """Render the content.

        Submit a render request to the server for the content. After submission, the server executes an asynchronous process to render the content. This is useful when content is dependent on external information, such as a dataset.

        See Also
        --------
        restart

        Examples
        --------
        >>> render()
        """
        full_content_item: ContentItem = self.update()  # pyright: ignore[reportCallIssue]

        if full_content_item.is_rendered:
            variants = full_content_item._variants.find()
            variants = [variant for variant in variants if variant["is_default"]]
            if len(variants) != 1:
                raise RuntimeError(
                    f"Found {len(variants)} default variants. Expected 1. Without a single default variant, the content cannot be refreshed. This is indicative of a corrupted state.",
                )
            variant = variants[0]
            return variant.render()
        else:
            raise ValueError(
                f"Render not supported for this application mode: {self['app_mode']}. Did you need to use the 'restart()' method instead? Note that some application modes do not support 'render()' or 'restart()'.",
            )

    def restart(self) -> None:
        """Mark for restart.

        Sends a restart request to the server for the content. Once submitted, the server performs an asynchronous process to restart the content. This is particularly useful when the content relies on external information loaded into application memory, such as datasets. Additionally, restarting can help clear memory leaks or reduce excessive memory usage that might build up over time.

        See Also
        --------
        render

        Examples
        --------
        >>> restart()
        """
        full_content_item: ContentItem = self.update()  # pyright: ignore[reportCallIssue]

        if full_content_item.is_interactive:
            unix_epoch_in_seconds = str(int(time.time()))
            key = f"_CONNECT_RESTART_TMP_{unix_epoch_in_seconds}"
            full_content_item.environment_variables.create(key, unix_epoch_in_seconds)
            full_content_item.environment_variables.delete(key)
            # GET via the base Connect URL to force create a new worker thread.
            url = posixpath.join(
                dirname(full_content_item._ctx.url), f"content/{full_content_item['guid']}"
            )
            full_content_item._ctx.session.get(url)
            return None
        else:
            raise ValueError(
                f"Restart not supported for this application mode: {self['app_mode']}. Did you need to use the 'render()' method instead? Note that some application modes do not support 'render()' or 'restart()'.",
            )

    def update(
        self,
        **attrs: Unpack[ContentItem._Attrs],
    ) -> ContentItem:
        """Update the content item.

        Parameters
        ----------
        name : str
            URL-friendly identifier. Allows alphanumeric characters, hyphens ("-"), and underscores ("_").
        title : str, optional
            Content title. Default is None.
        description : str, optional
            Content description. Default is None.
        access_type : Literal['all', 'acl', 'logged_in'], optional
            How content manages viewers. Default is 'acl'. Options: 'all', 'logged_in', 'acl'.
        owner_guid : str, optional
            The unique identifier of the user who owns this content item. Default is None.
        connection_timeout : int, optional
            Max seconds without data exchange. Default is None. Falls back to server setting 'Scheduler.ConnectionTimeout'.
        read_timeout : int, optional
            Max seconds without data received. Default is None. Falls back to server setting 'Scheduler.ReadTimeout'.
        init_timeout : int, optional
            Max startup time for interactive apps. Default is None. Falls back to server setting 'Scheduler.InitTimeout'.
        idle_timeout : int, optional
            Max idle time before process termination. Default is None. Falls back to server setting 'Scheduler.IdleTimeout'.
        max_processes : int, optional
            Max concurrent processes allowed. Default is None. Falls back to server setting 'Scheduler.MaxProcesses'.
        min_processes : int, optional
            Min concurrent processes required. Default is None. Falls back to server setting 'Scheduler.MinProcesses'.
        max_conns_per_process : int, optional
            Max client connections per process. Default is None. Falls back to server setting 'Scheduler.MaxConnsPerProcess'.
        load_factor : float, optional
            Aggressiveness in spawning new processes (0.0 - 1.0). Default is None. Falls back to server setting 'Scheduler.LoadFactor'.
        cpu_request : float, optional
            Min CPU units required (1 unit = 1 core). Default is None. Falls back to server setting 'Scheduler.CPURequest'.
        cpu_limit : float, optional
            Max CPU units allowed. Default is None. Falls back to server setting 'Scheduler.CPULimit'.
        memory_request : int, optional
            Min memory (bytes) required. Default is None. Falls back to server setting 'Scheduler.MemoryRequest'.
        memory_limit : int, optional
            Max memory (bytes) allowed. Default is None. Falls back to server setting 'Scheduler.MemoryLimit'.
        amd_gpu_limit : int, optional
            Number of AMD GPUs allocated. Default is None. Falls back to server setting 'Scheduler.AMDGPULimit'.
        nvidia_gpu_limit : int, optional
            Number of NVIDIA GPUs allocated. Default is None. Falls back to server setting 'Scheduler.NvidiaGPULimit'.
        run_as : str, optional
            UNIX user to execute the content. Default is None. Falls back to server setting 'Applications.RunAs'.
        run_as_current_user : bool, optional
            Run process as the visiting user (for app content). Default is False.
        default_image_name : str, optional
            Default image for execution if not defined in the bundle. Default is None.
        default_r_environment_management : bool, optional
            Manage R environment for the content. Default is None.
        default_py_environment_management : bool, optional
            Manage Python environment for the content. Default is None.
        service_account_name : str, optional
            Kubernetes service account name for running content. Default is None.

        Returns
        -------
        None
        """
        result = self._patch_api(json=cast(JsonifiableDict, dict(attrs)))
        assert isinstance(result, dict)
        assert "guid" in result
        new_content_item = ContentItem(
            params=context_to_resource_parameters(self._ctx),
            # `guid=` is contained within the `result` dict
            **result,  # pyright: ignore[reportArgumentType, reportCallIssue]
        )
        # TODO-barret Update method returns new content item
        return new_content_item

    # Relationships

    @property
    def bundles(self) -> Bundles:
        return Bundles(context_to_resource_parameters(self._ctx), self["guid"])

    @property
    def environment_variables(self) -> EnvVars:
        return EnvVars(context_to_resource_parameters(self._ctx), self["guid"])

    @property
    def permissions(self) -> Permissions:
        return Permissions(context_to_resource_parameters(self._ctx), self["guid"])

    @property
    def owner(self) -> dict:
        if not hasattr(self, "_owner"):
            # It is possible to get a content item that does not contain owner.
            # "owner" is an optional additional request param.
            # If it's not included, we can retrieve the information by `owner_guid`
            from .users import Users

            self._owner: User = Users(context_to_resource_parameters(self._ctx)).get(
                self["owner_guid"]
            )
        return self._owner

    @property
    def _variants(self) -> Variants:
        return Variants(self._ctx)

    @property
    def is_interactive(self) -> bool:
        return self["app_mode"] in {
            "api",
            "jupyter-voila",
            "python-api",
            "python-bokeh",
            "python-dash",
            "python-fastapi",
            "python-shiny",
            "python-streamlit",
            "quarto-shiny",
            "rmd-shiny",
            "shiny",
            "tensorflow-saved-model",
        }

    @property
    def is_rendered(self) -> bool:
        return self["app_mode"] in {
            "rmd-static",
            "jupyter-static",
            "quarto-static",
        }


class Content(Resources):
    """Content resource.

    Parameters
    ----------
    config : Config
        Configuration object.
    session : Session
        Requests session object.
    owner_guid : str, optional
        Content item owner identifier. Filters results to those owned by a specific user (the default is None, which implies not filtering results on owner identifier).
    """

    def __init__(
        self,
        params: ResourceParameters,
        *,
        owner_guid: str | None = None,
    ) -> None:
        super().__init__(params)
        self.owner_guid = owner_guid

    def count(self) -> int:
        """Count the number of content items.

        Returns
        -------
        int
        """
        return len(self.find())

    def create(
        self,
        **attrs: Unpack[ContentItem._AttrsCreate],
    ) -> ContentItem:
        """Create content.

        Parameters
        ----------
        name : str
            URL-friendly identifier. Allows alphanumeric characters, hyphens ("-"), and underscores ("_").
        title : str, optional
            Content title. Default is None.
        description : str, optional
            Content description. Default is None.
        access_type : Literal['all', 'acl', 'logged_in'], optional
            How content manages viewers. Default is 'acl'. Options: 'all', 'logged_in', 'acl'.
        connection_timeout : int, optional
            Max seconds without data exchange. Default is None. Falls back to server setting 'Scheduler.ConnectionTimeout'.
        read_timeout : int, optional
            Max seconds without data received. Default is None. Falls back to server setting 'Scheduler.ReadTimeout'.
        init_timeout : int, optional
            Max startup time for interactive apps. Default is None. Falls back to server setting 'Scheduler.InitTimeout'.
        idle_timeout : int, optional
            Max idle time before process termination. Default is None. Falls back to server setting 'Scheduler.IdleTimeout'.
        max_processes : int, optional
            Max concurrent processes allowed. Default is None. Falls back to server setting 'Scheduler.MaxProcesses'.
        min_processes : int, optional
            Min concurrent processes required. Default is None. Falls back to server setting 'Scheduler.MinProcesses'.
        max_conns_per_process : int, optional
            Max client connections per process. Default is None. Falls back to server setting 'Scheduler.MaxConnsPerProcess'.
        load_factor : float, optional
            Aggressiveness in spawning new processes (0.0 - 1.0). Default is None. Falls back to server setting 'Scheduler.LoadFactor'.
        cpu_request : float, optional
            Min CPU units required (1 unit = 1 core). Default is None. Falls back to server setting 'Scheduler.CPURequest'.
        cpu_limit : float, optional
            Max CPU units allowed. Default is None. Falls back to server setting 'Scheduler.CPULimit'.
        memory_request : int, optional
            Min memory (bytes) required. Default is None. Falls back to server setting 'Scheduler.MemoryRequest'.
        memory_limit : int, optional
            Max memory (bytes) allowed. Default is None. Falls back to server setting 'Scheduler.MemoryLimit'.
        amd_gpu_limit : int, optional
            Number of AMD GPUs allocated. Default is None. Falls back to server setting 'Scheduler.AMDGPULimit'.
        nvidia_gpu_limit : int, optional
            Number of NVIDIA GPUs allocated. Default is None. Falls back to server setting 'Scheduler.NvidiaGPULimit'.
        run_as : str, optional
            UNIX user to execute the content. Default is None. Falls back to server setting 'Applications.RunAs'.
        run_as_current_user : bool, optional
            Run process as the visiting user (for app content). Default is False.
        default_image_name : str, optional
            Default image for execution if not defined in the bundle. Default is None.
        default_r_environment_management : bool, optional
            Manage R environment for the content. Default is None.
        default_py_environment_management : bool, optional
            Manage Python environment for the content. Default is None.
        service_account_name : str, optional
            Kubernetes service account name for running content. Default is None.
        **attributes : Any
            Additional attributes.

        Returns
        -------
        ContentItem
        """
        path = "v1/content"
        url = self.params.url + path
        response = self.params.session.post(url, json=attrs)
        return ContentItem(self.params, **response.json())

    @overload
    def find(
        self,
        *,
        name: Optional[str] = None,
        owner_guid: Optional[str] = None,
        include: Optional[
            Literal["owner", "tags", "vanity_url"] | list[Literal["owner", "tags", "vanity_url"]]
        ] = None,
    ) -> List[ContentItem]:
        """Find content matching the specified criteria.

        **Applies to Connect versions 2024.06.0 and later.**

        Parameters
        ----------
        name : str, optional
            The content name specified at creation; unique within the owner's account.
        owner_guid : str, optional
            The UUID of the content owner.
        include : str or list of str, optional
            Additional details to include in the response. Allowed values: 'owner', 'tags', 'vanity_url'.

        Returns
        -------
        List[ContentItem]
            List of matching content items.

        Note
        ----
        Specifying both `name` and `owner_guid` returns at most one content item due to uniqueness.
        """

    @overload
    def find(
        self,
        *,
        name: Optional[str] = None,
        owner_guid: Optional[str] = None,
        include: Optional[Literal["owner", "tags"] | list[Literal["owner", "tags"]]] = None,
    ) -> List[ContentItem]:
        """Find content matching the specified criteria.

        **Applies to Connect versions prior to 2024.06.0.**

        Parameters
        ----------
        name : str, optional
            The content name specified at creation; unique within the owner's account.
        owner_guid : str, optional
            The UUID of the content owner.
        include : str or list of str, optional
            Additional details to include in the response. Allowed values: 'owner', 'tags'.

        Returns
        -------
        List[ContentItem]
            List of matching content items.

        Note
        ----
        Specifying both `name` and `owner_guid` returns at most one content item due to uniqueness.
        """

    @overload
    def find(self, include: Optional[str | list[Any]], **conditions) -> List[ContentItem]: ...

    def find(self, include: Optional[str | list[Any]] = None, **conditions) -> List[ContentItem]:
        """Find content matching the specified conditions.

        Returns
        -------
        List[ContentItem]
        """
        if isinstance(include, list):
            include = ",".join(include)

        if include is not None:
            conditions["include"] = include

        if self.owner_guid:
            conditions["owner_guid"] = self.owner_guid

        path = "v1/content"
        url = self.params.url + path
        response = self.params.session.get(url, params=conditions)
        return [
            ContentItem(
                self.params,
                **result,
            )
            for result in response.json()
        ]

    def find_by(
        self,
        **attrs: Unpack[ContentItem._AttrsNotRequired],
    ) -> Optional[ContentItem]:
        """Find the first content record matching the specified attributes.

        There is no implied ordering so if order matters, you should find it yourself.

        Parameters
        ----------
        name : str, optional
            URL-friendly identifier. Allows alphanumeric characters, hyphens ("-"), and underscores ("_").
        title : str, optional
            Content title. Default is None
        description : str, optional
            Content description.
        access_type : Literal['all', 'acl', 'logged_in'], optional
            How content manages viewers.
        owner_guid : str, optional
            The unique identifier of the user who owns this content item.
        connection_timeout : int, optional
            Max seconds without data exchange.
        read_timeout : int, optional
            Max seconds without data received.
        init_timeout : int, optional
            Max startup time for interactive apps.
        idle_timeout : int, optional
            Max idle time before process termination.
        max_processes : int, optional
            Max concurrent processes allowed.
        min_processes : int, optional
            Min concurrent processes required.
        max_conns_per_process : int, optional
            Max client connections per process.
        load_factor : float, optional
            Aggressiveness in spawning new processes (0.0 - 1.0).
        cpu_request : float, optional
            Min CPU units required (1 unit = 1 core).
        cpu_limit : float, optional
            Max CPU units allowed.
        memory_request : int, optional
            Min memory (bytes) required.
        memory_limit : int, optional
            Max memory (bytes) allowed.
        amd_gpu_limit : int, optional
            Number of AMD GPUs allocated.
        nvidia_gpu_limit : int, optional
            Number of NVIDIA GPUs allocated.
        run_as : str, optional
            UNIX user to execute the content.
        run_as_current_user : bool, optional
            Run process as the visiting user (for app content). Default is False.
        default_image_name : str, optional
            Default image for execution if not defined in the bundle.
        default_r_environment_management : bool, optional
            Manage R environment for the content.
        default_py_environment_management : bool, optional
            Manage Python environment for the content.
        service_account_name : str, optional
            Kubernetes service account name for running content.

        Returns
        -------
        Optional[ContentItem]

        Example
        -------
        >>> find_by(name="example-content-name")
        """
        attr_items = attrs.items()
        results = self.find()
        results = (
            result for result in results if all(item in result.items() for item in attr_items)
        )
        return next(results, None)

    @overload
    def find_one(
        self,
        *,
        name: Optional[str] = None,
        owner_guid: Optional[str] = None,
        include: Optional[
            Literal["owner", "tags", "vanity_url"] | list[Literal["owner", "tags", "vanity_url"]]
        ] = None,
    ) -> Optional[ContentItem]:
        """Find first content result matching the specified conditions.

        Parameters
        ----------
        name : str, optional
            The content name specified at creation; unique within the owner's account.
        owner_guid : str, optional
            The UUID of the content owner.
        include : str or list of str, optional
            Additional details to include in the response. Allowed values: 'owner', 'tags', 'vanity_url'.

        Returns
        -------
        Optional[ContentItem]
            List of matching content items.

        Note
        ----
        Specifying both `name` and `owner_guid` returns at most one content item due to uniqueness.
        """

    @overload
    def find_one(
        self,
        *,
        name: Optional[str] = None,
        owner_guid: Optional[str] = None,
        include: Optional[Literal["owner", "tags"] | list[Literal["owner", "tags"]]] = None,
    ) -> Optional[ContentItem]:
        """Find first content result matching the specified conditions.

        **Applies to Connect versions prior to 2024.06.0.**

        Parameters
        ----------
        name : str, optional
            The content name specified at creation; unique within the owner's account.
        owner_guid : str, optional
            The UUID of the content owner.
        include : str or list of str, optional
            Additional details to include in the response. Allowed values: 'owner', 'tags'.

        Returns
        -------
        Optional[ContentItem]
            List of matching content items.

        Note
        ----
        Specifying both `name` and `owner_guid` returns at most one content item due to uniqueness.
        """

    @overload
    def find_one(self, **conditions) -> Optional[ContentItem]: ...

    def find_one(self, **conditions) -> Optional[ContentItem]:
        """Find first content result matching the specified conditions.

        Returns
        -------
        Optional[ContentItem]
        """
        items = self.find(**conditions)
        return next(iter(items), None)

    def get(self, guid: str) -> ContentItem:
        """Get a content item.

        Parameters
        ----------
        guid : str

        Returns
        -------
        ContentItem
        """
        path = f"v1/content/{guid}"
        url = self.params.url + path
        response = self.params.session.get(url)
        return ContentItem(self.params, **response.json())
