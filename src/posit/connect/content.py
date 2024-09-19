"""Content resources."""

from __future__ import annotations

import posixpath
import time
from posixpath import dirname
from typing import Any, List, Literal, Optional, overload

from posit.connect.oauth.associations import ContentItemAssociations

from . import tasks
from .bundles import Bundles
from .env import EnvVars
from .permissions import Permissions
from .resources import Resource, ResourceParameters, Resources
from .tasks import Task
from .variants import Variants


class ContentItemOAuth(Resource):
    def __init__(self, params: ResourceParameters, content_guid: str) -> None:
        super().__init__(params)
        self.content_guid = content_guid

    @property
    def associations(self) -> ContentItemAssociations:
        return ContentItemAssociations(self.params, content_guid=self.content_guid)


class ContentItemOwner(Resource):
    pass


class ContentItem(Resource):
    def __getitem__(self, key: Any) -> Any:
        v = super().__getitem__(key)
        if key == "owner" and isinstance(v, dict):
            return ContentItemOwner(params=self.params, **v)
        return v

    @property
    def oauth(self) -> ContentItemOAuth:
        return ContentItemOAuth(self.params, content_guid=self["guid"])

    def delete(self) -> None:
        """Delete the content item."""
        path = f"v1/content/{self.guid}"
        url = self.params.url + path
        self.params.session.delete(url)

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
        path = f"v1/content/{self.guid}/deploy"
        url = self.params.url + path
        response = self.params.session.post(url, json={"bundle_id": None})
        result = response.json()
        ts = tasks.Tasks(self.params)
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
        self.update()

        if self.is_rendered:
            variants = self._variants.find()
            variants = [variant for variant in variants if variant.is_default]
            if len(variants) != 1:
                raise RuntimeError(
                    f"Found {len(variants)} default variants. Expected 1. Without a single default variant, the content cannot be refreshed. This is indicative of a corrupted state."
                )
            variant = variants[0]
            return variant.render()
        else:
            raise ValueError(
                f"Render not supported for this application mode: {self.app_mode}. Did you need to use the 'restart()' method instead? Note that some application modes do not support 'render()' or 'restart()'."
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
        self.update()

        if self.is_interactive:
            unix_epoch_in_seconds = str(int(time.time()))
            key = f"_CONNECT_RESTART_TMP_{unix_epoch_in_seconds}"
            self.environment_variables.create(key, unix_epoch_in_seconds)
            self.environment_variables.delete(key)
            # GET via the base Connect URL to force create a new worker thread.
            url = posixpath.join(dirname(self.params.url), f"content/{self.guid}")
            self.params.session.get(url)
            return None
        else:
            raise ValueError(
                f"Restart not supported for this application mode: {self.app_mode}. Did you need to use the 'render()' method instead? Note that some application modes do not support 'render()' or 'restart()'."
            )

    @overload
    def update(
        self,
        *,
        # Required argument
        name: str,
        # Content Metadata
        title: Optional[str] = None,
        description: Optional[str] = None,
        access_type: Literal["all", "acl", "logged_in"] = "acl",
        owner_guid: Optional[str] = None,
        # Timeout Settings
        connection_timeout: Optional[int] = None,
        read_timeout: Optional[int] = None,
        init_timeout: Optional[int] = None,
        idle_timeout: Optional[int] = None,
        # Process and Resource Limits
        max_processes: Optional[int] = None,
        min_processes: Optional[int] = None,
        max_conns_per_process: Optional[int] = None,
        load_factor: Optional[float] = None,
        cpu_request: Optional[float] = None,
        cpu_limit: Optional[float] = None,
        memory_request: Optional[int] = None,
        memory_limit: Optional[int] = None,
        amd_gpu_limit: Optional[int] = None,
        nvidia_gpu_limit: Optional[int] = None,
        # Execution Settings
        run_as: Optional[str] = None,
        run_as_current_user: Optional[bool] = False,
        default_image_name: Optional[str] = None,
        default_r_environment_management: Optional[bool] = None,
        default_py_environment_management: Optional[bool] = None,
        service_account_name: Optional[str] = None,
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
        ...

    @overload
    def update(self, **attributes: Any) -> None:
        """Update the content."""
        ...

    def update(self, **attributes: Any) -> None:
        """Update the content."""
        url = self.params.url + f"v1/content/{self['guid']}"
        response = self.params.session.patch(url, json=attributes)
        super().update(**response.json())

    # Relationships

    @property
    def bundles(self) -> Bundles:
        return Bundles(self.params, self["guid"])

    @property
    def environment_variables(self) -> EnvVars:
        return EnvVars(self.params, self["guid"])

    @property
    def permissions(self) -> Permissions:
        return Permissions(self.params, self["guid"])

    @property
    def owner(self) -> dict:
        if "owner" not in self:
            # It is possible to get a content item that does not contain owner.
            # "owner" is an optional additional request param.
            # If it's not included, we can retrieve the information by `owner_guid`
            from .users import Users

            self["owner"] = Users(self.params).get(self["owner_guid"])
        return self["owner"]

    @property
    def _variants(self) -> Variants:
        return Variants(self.params, self["guid"])

    @property
    def is_interactive(self) -> bool:
        return self.app_mode in {
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
        return self.app_mode in {
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

    @overload
    def create(
        self,
        *,
        # Required argument
        name: str,
        # Content Metadata
        title: Optional[str] = None,
        description: Optional[str] = None,
        access_type: Literal["all", "acl", "logged_in"] = "acl",
        # Timeout Settings
        connection_timeout: Optional[int] = None,
        read_timeout: Optional[int] = None,
        init_timeout: Optional[int] = None,
        idle_timeout: Optional[int] = None,
        # Process and Resource Limits
        max_processes: Optional[int] = None,
        min_processes: Optional[int] = None,
        max_conns_per_process: Optional[int] = None,
        load_factor: Optional[float] = None,
        cpu_request: Optional[float] = None,
        cpu_limit: Optional[float] = None,
        memory_request: Optional[int] = None,
        memory_limit: Optional[int] = None,
        amd_gpu_limit: Optional[int] = None,
        nvidia_gpu_limit: Optional[int] = None,
        # Execution Settings
        run_as: Optional[str] = None,
        run_as_current_user: Optional[bool] = False,
        default_image_name: Optional[str] = None,
        default_r_environment_management: Optional[bool] = None,
        default_py_environment_management: Optional[bool] = None,
        service_account_name: Optional[str] = None,
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
        access_type : Literal['all', 'acl', 'logged_in', optional
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

        Returns
        -------
        ContentItem
        """
        ...

    @overload
    def create(self, **attributes) -> ContentItem:
        """Create a content item.

        Returns
        -------
        ContentItem
        """
        ...

    def create(self, **attributes) -> ContentItem:
        """Create a content item.

        Returns
        -------
        ContentItem
        """
        path = "v1/content"
        url = self.params.url + path
        response = self.params.session.post(url, json=attributes)
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
        ...

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
        ...

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

    @overload
    def find_by(
        self,
        *,
        # Required
        name: str,
        # Content Metadata
        title: Optional[str] = None,
        description: Optional[str] = None,
        access_type: Literal["all", "acl", "logged_in"] = "acl",
        owner_guid: Optional[str] = None,
        # Timeout Settings
        connection_timeout: Optional[int] = None,
        read_timeout: Optional[int] = None,
        init_timeout: Optional[int] = None,
        idle_timeout: Optional[int] = None,
        # Process and Resource Limits
        max_processes: Optional[int] = None,
        min_processes: Optional[int] = None,
        max_conns_per_process: Optional[int] = None,
        load_factor: Optional[float] = None,
        cpu_request: Optional[float] = None,
        cpu_limit: Optional[float] = None,
        memory_request: Optional[int] = None,
        memory_limit: Optional[int] = None,
        amd_gpu_limit: Optional[int] = None,
        nvidia_gpu_limit: Optional[int] = None,
        # Execution Settings
        run_as: Optional[str] = None,
        run_as_current_user: Optional[bool] = False,
        default_image_name: Optional[str] = None,
        default_r_environment_management: Optional[bool] = None,
        default_py_environment_management: Optional[bool] = None,
        service_account_name: Optional[str] = None,
    ) -> Optional[ContentItem]:
        """Find the first content record matching the specified attributes. There is no implied ordering so if order matters, you should find it yourself.

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
        """
        ...

    @overload
    def find_by(self, **attributes) -> Optional[ContentItem]:
        """Find the first content record matching the specified attributes. There is no implied ordering so if order matters, you should find it yourself.

        Returns
        -------
        Optional[ContentItem]
        """
        ...

    def find_by(self, **attributes) -> Optional[ContentItem]:
        """Find the first content record matching the specified attributes. There is no implied ordering so if order matters, you should find it yourself.

        Returns
        -------
        Optional[ContentItem]

        Example
        -------
        >>> find_by(name="example-content-name")
        """
        results = self.find()
        results = (
            result
            for result in results
            if all(item in result.items() for item in attributes.items())
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
        ...

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
        ...

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
