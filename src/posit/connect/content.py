"""Content resources."""

from __future__ import annotations

import posixpath
import time

from typing_extensions import (
    TYPE_CHECKING,
    Any,
    List,
    Literal,
    NotRequired,
    Optional,
    Required,
    TypedDict,
    Unpack,
    overload,
)

from . import tasks
from .bundles import Bundles
from .context import requires
from .env import EnvVars
from .oauth.associations import ContentItemAssociations
from .permissions import Permissions
from .repository import ContentItemRepositoryMixin
from .resources import Active, BaseResource, Resources, _ResourceSequence
from .tags import ContentItemTags
from .vanities import VanityMixin
from .variants import Variants

if TYPE_CHECKING:
    from .context import Context
    from .jobs import Jobs
    from .packages import ContentPackages
    from .tasks import Task


def _assert_guid(guid: str):
    assert isinstance(guid, str), "Expected 'guid' to be a string"
    assert len(guid) > 0, "Expected 'guid' to be non-empty"


class ContentItemOAuth(BaseResource):
    def __init__(self, ctx: Context, content_guid: str) -> None:
        super().__init__(ctx)
        self["content_guid"] = content_guid

    @property
    def associations(self) -> ContentItemAssociations:
        return ContentItemAssociations(self._ctx, content_guid=self["content_guid"])


class ContentItemOwner(BaseResource):
    pass


class ContentItem(Active, ContentItemRepositoryMixin, VanityMixin, BaseResource):
    class _AttrsBase(TypedDict, total=False):
        # # `name` will be set by other _Attrs classes
        # name: str

        # Content Metadata
        title: NotRequired[str]
        description: NotRequired[str]
        access_type: NotRequired[Literal["all", "acl", "logged_in"]]
        locked: NotRequired[bool]
        locked_message: NotRequired[str]
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
        # Bundle info
        content_category: NotRequired[str]
        parameterized: NotRequired[bool]
        cluster_name: NotRequired[str]
        image_name: NotRequired[str]
        default_image_name: NotRequired[str]
        default_r_environment_management: NotRequired[bool]
        default_py_environment_management: NotRequired[bool]
        service_account_name: NotRequired[str]
        r_version: NotRequired[str]
        r_environment_management: NotRequired[bool]
        py_version: NotRequired[str]
        py_environment_management: NotRequired[bool]
        quarto_version: NotRequired[str]
        # Execution Settings
        run_as: NotRequired[str]
        run_as_current_user: NotRequired[bool]
        created_time: NotRequired[str]
        last_deployed_time: NotRequired[str]
        bundle_id: NotRequired[str]
        app_mode: NotRequired[str]
        content_url: NotRequired[str]
        dashboard_url: NotRequired[str]
        app_role: NotRequired[Literal["owner", "editor", "viewer", "none"]]
        vanity_url: NotRequired[str]
        tags: NotRequired[List[dict]]
        owner: NotRequired[dict]
        id: NotRequired[str]
        extension: NotRequired[bool]

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
        ctx: Context,
        /,
        *,
        guid: str,
    ) -> None: ...

    @overload
    def __init__(
        self,
        ctx: Context,
        /,
        *,
        guid: str,
        **kwargs: Unpack[ContentItem._Attrs],
    ) -> None: ...

    def __init__(
        self,
        ctx: Context,
        /,
        *,
        guid: str,
        **kwargs: Unpack[ContentItem._AttrsNotRequired],
    ) -> None:
        """
        Content item.

        The content object models all the "things" you may deploy to Posit
        Connect. This includes Shiny applications, R Markdown documents, Jupyter notebooks,
        Plumber APIs, FastAPI and Flask APIs, Python apps, plots, and pins.

        The `app_mode` field specifies the type of content represented by this item
        and defines its runtime model.

        * Active content, such as apps and APIs, executes on demand as requests arrive.
        * Reports render from source to output HTML. This rendering can occur based on a
          schedule or when explicitly triggered. It is *not* on each visit. Viewers of this type of
          content see a previously rendered result.
        * Static content is presented to viewers in its deployed form.

        The fields `bundle_id`, `app_mode`, `content_category`, `parameterized`, `cluster_name`,
        `image_name`, `r_version`, `r_environment_management`, `py_version`,
        `py_environment_management`, and `quarto_version` are computed as a consequence of a <a
        href="#post-/v1/content/-guid-/deploy">POST /v1/content/{guid}/deploy</a> deployment
        operation.

        Parameters
        ----------
        ctx : Context
            Context object.
        guid : str
            The unique identifier of this content item.
        name: str, optional
            A simple, URL-friendly identifier. Allows alpha-numeric characters, hyphens ("-"), and
            underscores ("_").
        title : str, optional
            The title of this content.
        description : str, optional
            A rich description of this content.
        access_type : Literal['all', 'acl', 'logged_in'], optional
            Access type describes how this content manages its viewers. The value `all` is the most
            permissive; any visitor to Posit Connect will be able to view this content. The value
            `logged_in` indicates that all Posit Connect accounts may view the content. The `acl`
            value lets specifically enumerated users and groups view the content. Users configured
            as collaborators may always view content.
        locked : bool, optional
            Whether or not the content is locked.
        locked_message : str, optional
            A custom message that is displayed by the content item when locked. It is possible to
            format this message using Markdown.
        connection_timeout : int, optional
            Maximum number of seconds allowed without data sent or received across a client
            connection. A value of `0` means connections will never time-out (not recommended).
            When `null`, the default `Scheduler.ConnectionTimeout` is used. Applies only to content
            types that are executed on demand.
        read_timeout : int, optional
            Maximum number of seconds allowed without data received from a client connection. A
            value of `0` means a lack of client (browser) interaction never causes the connection
            to close. When `null`, the default `Scheduler.ReadTimeout` is used. Applies only to
            content types that are executed on demand.
        init_timeout : int, optional
            The maximum number of seconds allowed for an interactive application to start. Posit
            Connect must be able to connect to a newly launched application before this threshold
            has elapsed. When `null`, the default `Scheduler.InitTimeout` is used. Applies only to
            content types that are executed on demand.
        idle_timeout : int, optional
            The maximum number of seconds a worker process for an interactive application to remain
            alive after it goes idle (no active connections). When `null`, the default
            `Scheduler.IdleTimeout` is used. Applies only to content types that are executed on
            demand.
        max_processes : int, optional
            Specifies the total number of concurrent processes allowed for a single interactive
            application per Posit Connect node. When `null`, the default `Scheduler.MaxProcesses`
            is used. Applies only to content types that are executed on demand.
        min_processes : int, optional
            Specifies the minimum number of concurrent processes allowed for a single interactive
            application per Posit Connect node. When `null`, the default `Scheduler.MinProcesses`
            is used. Applies only to content types that are executed on demand.
        max_conns_per_process : int, optional
            Specifies the maximum number of client connections allowed to an individual process.
            Incoming connections which will exceed this limit are routed to a new process or
            rejected. When `null`, the default `Scheduler.MaxConnsPerProcess` is used. Applies only
            to content types that are executed on demand.
        load_factor : float, optional
            Controls how aggressively new processes are spawned. When `null`, the default
            `Scheduler.LoadFactor` is used. Applies only to content types that are executed on
            demand.
        cpu_request : float, optional
            The minimum amount of compute power this content needs when executing or rendering,
            expressed in ["CPU
            Units"](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu),
            where 1.0 unit is equivalent to 1 physical or virtual core. Fractional values are
            allowed. This is used when running in an off-host execution configuration to determine
            where the content should be run. When `null`, the default `Scheduler.CPURequest` is
            used.
        cpu_limit : float, optional
            The maximum amount of compute power this content will be allowed to consume when
            executing or rendering, expressed in ["CPU
            Units"](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/#meaning-of-cpu),
            where 1.0 unit is equivalent to 1 physical or virtual core. Fractional values are
            allowed. This is used when running in an off-host execution configuration. If the
            process tries to use more CPU than allowed, it will be throttled. When `null`, the
            default `Scheduler.CPULimit` is used.
        memory_request : int, optional
            The minimum amount of RAM this content needs when executing or rendering, expressed in
            bytes. This is used when running in an off-host execution configuration to determine
            where the content should be run. When `null`, the default `Scheduler.MemoryRequest` is
            used.
        memory_limit : int, optional
            The maximum amount of RAM this content will be allowed to consume when executing or
            rendering, expressed in bytes. If the process tries to use more memory than allowed, it
            will be terminated. When `null`, the default `Scheduler.MemoryLimit` is used.
        amd_gpu_limit : int, optional
            The number of AMD GPUs that will be [allocated by
            Kubernetes](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/) to run this
            content. This is used when running in an off-host execution configuration. When `null`,
            the default `Scheduler.AMDGPULimit` is used. This setting can not exceed
            `Scheduler.MaxAMDGPULimit`.
        nvidia_gpu_limit : int, optional
            The number of NVIDIA GPUs that will be [allocated by
            Kubernetes](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/) to run this
            content. This is used when running in an off-host execution configuration. When `null`,
            the default `Scheduler.NvidiaGPULimit` is used. This setting can not exceed
            `Scheduler.MaxNvidiaGPULimit`.
        created_time : str, optional
            The timestamp (RFC3339) indicating when this content was created.
        last_deployed_time : str, optional
            The timestamp (RFC3339) indicating when this content last had a successful bundle
            deployment performed.
        bundle_id : str, optional
            The identifier for the active deployment bundle. Automatically assigned upon the
            successful deployment of that bundle.
        app_mode : Literal['api', 'jupyter-static', 'jupyter-voila', 'python-api', 'python-bokeh', 'python-dash', 'python-fastapi', 'python-shiny', 'python-streamlit', 'quarto-shiny', 'quarto-static', 'rmd-shiny', 'rmd-static', 'shiny', 'static', 'tensorflow-saved-model', 'unknown'], optional
            The runtime model for this content. Has a value of `unknown` before data is deployed to
            this item. Automatically assigned upon the first successful bundle deployment.
        content_category : str, optional
            Describes the specialization of the content runtime model. Automatically assigned upon
            the first successful bundle deployment.
        parameterized : bool, optional
            True when R Markdown rendered content allows parameter configuration. Automatically
            assigned upon the first successful bundle deployment. Applies only to content with an
            `app_mode` of `rmd-static`.
        cluster_name : str, optional
            The location where this content runs. Content running on the same server as Connect
            will have either a `null` value or the string "Local". Gives the name of the cluster
            when run external to the Connect host. A `null` value is returned when the client does
            not have sufficient rights to see this information.
        image_name : str, optional
            The location where this content runs. Content running on the same server as Connect
            will have either a `null` value or the string "Local". References the name of the
            target image when content runs in a clustered environment such as Kubernetes. A `null`
            value is returned when the client does not have sufficient rights to see this
            information.
        default_image_name : str, optional
            The default image that will be used when none is defined by the bundle's manifest. A
            specific image may be selected by setting the `environment.image` field in the
            manifest. If no image is selected by the manifest file, then the `default_image_name`
            is used. If a target image is not defined by the manifest, and no `default_image_name`
            is configured, then Connect will select an image from the list of configured execution
            environments. A `null` value is returned when the client does not have sufficient
            rights to see this information. Use the `/v1/environments` API endpoints to determine
            which environments are available for content execution.
        default_r_environment_management : bool, optional
            Indicates whether or not Connect should create and manage an R environment (installing
            required packages) for this content. When `null`, Connect makes this determination
            based on the server configuration. A `null` value is also returned when the client does
            not have sufficient rights to see this information. This value is ignored if the server
            setting `Applications.DefaultEnvironmentManagementSelection` is disabled.
        default_py_environment_management : bool, optional
            Indicates whether or not Connect should create and manage a Python environment
            (installing required packages) for this content. When `null`, Connect makes this
            determination based on the server configuration. A `null` value is also returned when
            the client does not have sufficient rights to see this information. This value is
            ignored if the server setting `Applications.DefaultEnvironmentManagementSelection` is
            disabled.
        service_account_name : str, optional
            The name of the Kubernetes service account that is used to run a particular piece of
            content. It must adhere to valid Kubernetes service account naming rules. Connect must
            be configured to run with `Launcher.Enabled = true`, `Launcher.Kubernetes = true` and
            `Launcher.KubernetesContentServiceAccountSelection = true` for this value to be
            applied. It will have precedence over the `Launcher.KubernetesDefaultServiceAccount`
            that may be set in the configuration for Connect. If this value is defined and Connect
            is configured with `Launcher.KubernetesContentServiceAccountSelection = false` an error
            will be returned. Only administrators and publishers can view this value. Only
            administrators can set or change this value.
        r_version : str, optional
            The of R interpreter associated with this content. A `null` value represents that R is
            not used by this content, that the content has not been prepared for execution, or that
            the client does not have sufficient rights to see this information. Automatically
            assigned upon the successful deployment of a bundle.
        r_environment_management : bool, optional
            Indicates whether or not Connect is managing an R environment and has installed the
            required packages for this content. A `null` value represents that R is not used by
            this content, that the content has not been prepared for execution, or that the client
            does not have sufficient rights to see this information. Automatically assigned upon
            the successful deployment of a bundle.
        py_version : str, optional
            The version of Python associated with this content. A `null` value represents that
            Python is not used by this content, that the content has not been prepared for
            execution, or that the client does not have sufficient rights to see this information.
            Automatically assigned upon the successful deployment of a bundle.
        py_environment_management : bool, optional
            Indicates whether or not Connect is managing a Python environment and has installed the
            required packages for this content. A `null` value represents that Python is not used
            by this content, that the content has not been prepared for execution, or that the
            client does not have sufficient rights to see this information. Automatically assigned
            upon the successful deployment of a bundle.
        quarto_version : str, optional
            The version of Quarto associated with this content. A `null` represents that Quarto is
            not used by this content, that the content has not been prepared for execution, or that
            the client does not have sufficient rights to see this information. Automatically
            assigned upon the successful deployment of a bundle.
        run_as : str, optional
            The UNIX user that executes this content. When `null`, the default `Applications.RunAs`
            is used. Applies only to executable content types - not `static`.
        run_as_current_user : bool, optional
            Indicates that Connect should run processes for this content item under the Unix
            account of the user who visits it. Content accessed anonymously will continue to run as
            the specified `run_as` user. Connect must be configured to use PAM authentication with
            the server settings `Applications.RunAsCurrentUser = true` and `PAM.ForwardPassword =
            true`. This setting has no effect for other authentication types. This setting only
            applies to application content types (Shiny, Dash, Streamlit, and Bokeh).
        owner_guid : str, optional
            The unique identifier of the user who owns this content item.
        content_url : str, optional
            The URL associated with this content. Computed from the associated GUID for this
            content.
        dashboard_url : str, optional
            The URL within the Connect dashboard where this content can be configured. Computed
            from the GUID for this content.
        app_role : Literal['owner', 'editor', 'viewer', 'none'], optional
            The relationship of the accessing user to this content. A value of `owner` is returned
            for the content owner. `editor` indicates a collaborator. The `viewer` value is given
            to users who are permitted to view the content. A `none` role is returned for
            administrators who cannot view the content but are permitted to view its configuration.
            Computed at the time of the request.
        vanity_url : str, optional
            The vanity URL associated with this content item. Included in responses when the vanity
            URL is set and `include=vanity_url` is provided.
        tags : List[Tag], optional
            Tags associated with this content item. Included in responses when `include=tags` is
            provided.
        owner : ContentItemOwner, optional
            Basic details about the owner of this content item. Included in responses when
            `include=owner` is provided.
        id : str, optional
            The internal numeric identifier of this content item.
        extension : bool, optional
            Whether the content is a Connect Extension.
        """
        _assert_guid(guid)

        path = f"v1/content/{guid}"
        super().__init__(ctx, path, guid=guid, **kwargs)

    def __getitem__(self, key: Any) -> Any:
        v = super().__getitem__(key)
        if key == "owner" and isinstance(v, dict):
            return ContentItemOwner(self._ctx, **v)
        return v

    @property
    def oauth(self) -> ContentItemOAuth:
        return ContentItemOAuth(self._ctx, content_guid=self["guid"])

    def delete(self) -> None:
        """Delete the content item."""
        path = f"v1/content/{self['guid']}"
        self._ctx.client.delete(path)

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
        response = self._ctx.client.post(path, json={"bundle_id": None})
        result = response.json()
        ts = tasks.Tasks(self._ctx)
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
        self.update()  # pyright: ignore[reportCallIssue]

        if self.is_rendered:
            variants = self._variants.find()
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
        self.update()  # pyright: ignore[reportCallIssue]

        if self.is_interactive:
            unix_epoch_in_seconds = str(int(time.time()))
            key = f"_CONNECT_RESTART_TMP_{unix_epoch_in_seconds}"
            self.environment_variables.create(key, unix_epoch_in_seconds)
            self.environment_variables.delete(key)
            # GET via the base Connect URL to force create a new worker thread.
            path = f"../content/{self['guid']}"
            self._ctx.client.get(path)
            return None
        else:
            raise ValueError(
                f"Restart not supported for this application mode: {self['app_mode']}. Did you need to use the 'render()' method instead? Note that some application modes do not support 'render()' or 'restart()'.",
            )

    def update(
        self,
        **attrs: Unpack[ContentItem._Attrs],
    ) -> None:
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
        response = self._ctx.client.patch(f"v1/content/{self['guid']}", json=attrs)
        super().update(**response.json())

    # Relationships

    @property
    def bundles(self) -> Bundles:
        return Bundles(self._ctx, self["guid"])

    @property
    def environment_variables(self) -> EnvVars:
        return EnvVars(self._ctx, self["guid"])

    @property
    def permissions(self) -> Permissions:
        return Permissions(self._ctx, self["guid"])

    @property
    def owner(self) -> dict:
        if "owner" not in self:
            # It is possible to get a content item that does not contain owner.
            # "owner" is an optional additional request param.
            # If it's not included, we can retrieve the information by `owner_guid`
            from .users import Users

            self["owner"] = Users(
                self._ctx,
            ).get(self["owner_guid"])
        return self["owner"]

    @property
    def _variants(self) -> Variants:
        return Variants(self._ctx, self["guid"])

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

    @property
    def tags(self) -> ContentItemTags:
        path = f"v1/content/{self['guid']}/tags"
        return ContentItemTags(
            self._ctx,
            path,
            tags_path="v1/tags",
            content_guid=self["guid"],
        )

    @property
    def jobs(self) -> Jobs:
        path = posixpath.join(self._path, "jobs")
        return _ResourceSequence(self._ctx, path, uid="key")

    @property
    @requires(version="2024.11.0")
    def packages(self) -> ContentPackages:
        path = posixpath.join(self._path, "packages")
        return _ResourceSequence(self._ctx, path, uid="name")


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
        ctx: Context,
        *,
        owner_guid: str | None = None,
    ) -> None:
        super().__init__(ctx)
        self.owner_guid = owner_guid
        self._ctx = ctx

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
        response = self._ctx.client.post("v1/content", json=attrs)
        return ContentItem(self._ctx, **response.json())

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

        response = self._ctx.client.get("v1/content", params=conditions)
        return [
            ContentItem(
                self._ctx,
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

        Examples
        --------
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
        response = self._ctx.client.get(f"v1/content/{guid}")
        return ContentItem(self._ctx, **response.json())
