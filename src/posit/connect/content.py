"""Content resources."""

from __future__ import annotations

import posixpath
import time
from posixpath import dirname
from typing import List, Optional, overload

from . import tasks
from .bundles import Bundles
from .env import EnvVars
from .permissions import Permissions
from .resources import Resource, ResourceParameters, Resources
from .tasks import Task
from .variants import Variants


class ContentItemOwner(Resource):
    """Content item owner resource."""

    @property
    def guid(self) -> str:
        return self.get("guid")  # type: ignore

    @property
    def username(self) -> str:
        return self.get("username")  # type: ignore

    @property
    def first_name(self) -> Optional[str]:
        return self.get("first_name")  # type: ignore

    @property
    def last_name(self) -> Optional[str]:
        return self.get("last_name")  # type: ignore


class ContentItem(Resource):
    """Content item resource.

    Attributes
    ----------
    bundles : Bundles
        Bundles resource for the content item.
    permissions : Permissions
        Permissions resource for the content item.
    id : str
        Unique identifier of the content item.
    guid : str
        Globally unique identifier of the content item.
    name : str
        Name of the content item.
    title : Optional[str]
        Title of the content item.
    description : str
        Description of the content item.
    access_type : str
        Access type of the content item.
    connection_timeout : Optional[int]
        Connection timeout setting for the content item.
    read_timeout : Optional[int]
        Read timeout setting for the content item.
    init_timeout : Optional[int]
        Initialization timeout setting for the content item.
    idle_timeout : Optional[int]
        Idle timeout setting for the content item.
    max_processes : Optional[int]
        Maximum number of processes allowed for the content item.
    min_processes : Optional[int]
        Minimum number of processes required for the content item.
    max_conns_per_process : Optional[int]
        Maximum number of connections per process for the content item.
    load_factor : Optional[float]
        Load factor for the content item.
    cpu_request : Optional[float]
        CPU request for the content item.
    cpu_limit : Optional[float]
        CPU limit for the content item.
    memory_request : Optional[int]
        Memory request for the content item.
    memory_limit : Optional[int]
        Memory limit for the content item.
    amd_gpu_limit : Optional[int]
        AMD GPU limit for the content item.
    nvidia_gpu_limit : Optional[int]
        NVIDIA GPU limit for the content item.
    created_time : str
        Creation time of the content item.
    last_deployed_time : str
        Last deployment time of the content item.
    bundle_id : Optional[str]
        Bundle ID associated with the content item.
    app_mode : str
        Application mode of the content item.
    content_category : Optional[str]
        Content category of the content item.
    parameterized : bool
        Indicates if the content item is parameterized.
    cluster_name : Optional[str]
        Name of the cluster associated with the content item.
    image_name : Optional[str]
        Name of the image associated with the content item.
    default_image_name : Optional[str]
        Default image name for the content item.
    default_r_environment_management : Optional[bool]
        Indicates if R environment management is enabled by default.
    default_py_environment_management : Optional[bool]
        Indicates if Python environment management is enabled by default.
    service_account_name : Optional[str]
        Name of the service account associated with the content item.
    r_version : Optional[str]
        R version used by the content item.
    r_environment_management : Optional[bool]
        Indicates if R environment management is enabled.
    py_version : Optional[str]
        Python version used by the content item.
    py_environment_management : Optional[bool]
        Indicates if Python environment management is enabled.
    quarto_version : Optional[str]
        Quarto version used by the content item.
    run_as : Optional[str]
        User to run the content item as.
    run_as_current_user : bool
        Indicates if the content item runs as the current user.
    owner_guid : str
        GUID of the owner of the content item.
    owner : ContentItemOwner
        Owner information of the content item.
    content_url : str
        URL of the content item.
    dashboard_url : str
        Dashboard URL of the content item.
    app_role : str
        Application role of the content item.
    tags : List[dict]
        Tags associated with the content item.
    """

    # CRUD Methods

    def delete(self) -> None:
        """Delete the content item."""
        path = f"v1/content/{self.guid}"
        url = self.url + path
        self.session.delete(url)

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
        url = self.url + path
        response = self.session.post(url, json={"bundle_id": None})
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
            url = posixpath.join(dirname(self.url), f"content/{self.guid}")
            self.session.get(url)
            return None
        else:
            raise ValueError(
                f"Restart not supported for this application mode: {self.app_mode}. Did you need to use the 'render()' method instead? Note that some application modes do not support 'render()' or 'restart()'."
            )

    @overload
    def update(
        self,
        name: str = ...,
        title: Optional[str] = ...,
        description: str = ...,
        access_type: str = ...,
        owner_guid: Optional[str] = ...,
        connection_timeout: Optional[int] = ...,
        read_timeout: Optional[int] = ...,
        init_timeout: Optional[int] = ...,
        idle_timeout: Optional[int] = ...,
        max_processes: Optional[int] = ...,
        min_processes: Optional[int] = ...,
        max_conns_per_process: Optional[int] = ...,
        load_factor: Optional[float] = ...,
        cpu_request: Optional[float] = ...,
        cpu_limit: Optional[float] = ...,
        memory_request: Optional[int] = ...,
        memory_limit: Optional[int] = ...,
        amd_gpu_limit: Optional[int] = ...,
        nvidia_gpu_limit: Optional[int] = ...,
        run_as: Optional[str] = ...,
        run_as_current_user: Optional[bool] = ...,
        default_image_name: Optional[str] = ...,
        default_r_environment_management: Optional[bool] = ...,
        default_py_environment_management: Optional[bool] = ...,
        service_account_name: Optional[str] = ...,
    ) -> None:
        """Update the content item.

        Parameters
        ----------
        name : str, optional
        title : Optional[str], optional
        description : str, optional
        access_type : str, optional
        owner_guid : Optional[str], optional
        connection_timeout : Optional[int], optional
        read_timeout : Optional[int], optional
        init_timeout : Optional[int], optional
        idle_timeout : Optional[int], optional
        max_processes : Optional[int], optional
        min_processes : Optional[int], optional
        max_conns_per_process : Optional[int], optional
        load_factor : Optional[float], optional
        cpu_request : Optional[float], optional
        cpu_limit : Optional[float], optional
        memory_request : Optional[int], optional
        memory_limit : Optional[int], optional
        amd_gpu_limit : Optional[int], optional
        nvidia_gpu_limit : Optional[int], optional
        run_as : Optional[str], optional
        run_as_current_user : Optional[bool], optional
        default_image_name : Optional[str], optional
        default_r_environment_management : Optional[bool], optional
        default_py_environment_management : Optional[bool], optional
        service_account_name : Optional[str], optional
        """
        ...

    @overload
    def update(self, *args, **kwargs) -> None:
        """Update the content item."""
        ...

    def update(self, *args, **kwargs) -> None:
        """Update the content item."""
        body = dict(*args, **kwargs)
        url = self.url + f"v1/content/{self.guid}"
        response = self.session.patch(url, json=body)
        super().update(**response.json())

    # Relationships

    @property
    def bundles(self) -> Bundles:
        return Bundles(self.params, self.guid)

    @property
    def environment_variables(self) -> EnvVars:
        return EnvVars(self.params, self.guid)

    @property
    def permissions(self) -> Permissions:
        return Permissions(self.params, self.guid)

    @property
    def owner(self) -> ContentItemOwner:
        if "owner" not in self:
            # It is possible to get a content item that does not contain owner.
            # "owner" is an optional additional request param.
            # If it's not included, we can retrieve the information by `owner_guid`
            from .users import Users

            self["owner"] = Users(self.params).get(self.owner_guid)
        return ContentItemOwner(self.params, **self["owner"])

    @property
    def _variants(self) -> Variants:
        return Variants(self.params, self.guid)

    # Properties

    @property
    def id(self) -> str:
        return self.get("id")  # type: ignore

    @property
    def guid(self) -> str:
        return self.get("guid")  # type: ignore

    @property
    def name(self) -> str:
        return self.get("name")  # type: ignore

    @property
    def title(self) -> Optional[str]:
        return self.get("title")  # type: ignore

    @property
    def description(self) -> str:
        return self.get("description")  # type: ignore

    @property
    def access_type(self) -> str:
        return self.get("access_type")  # type: ignore

    @property
    def connection_timeout(self) -> Optional[int]:
        return self.get("connection_timeout")  # type: ignore

    @property
    def read_timeout(self) -> Optional[int]:
        return self.get("read_timeout")  # type: ignore

    @property
    def init_timeout(self) -> Optional[int]:
        return self.get("init_timeout")  # type: ignore

    @property
    def idle_timeout(self) -> Optional[int]:
        return self.get("idle_timeout")  # type: ignore

    @property
    def max_processes(self) -> Optional[int]:
        return self.get("max_processes")  # type: ignore

    @property
    def min_processes(self) -> Optional[int]:
        return self.get("min_processes")  # type: ignore

    @property
    def max_conns_per_process(self) -> Optional[int]:
        return self.get("max_conns_per_process")  # type: ignore

    @property
    def load_factor(self) -> Optional[float]:
        return self.get("load_factor")  # type: ignore

    @property
    def cpu_request(self) -> Optional[float]:
        return self.get("cpu_request")  # type: ignore

    @property
    def cpu_limit(self) -> Optional[float]:
        return self.get("cpu_limit")  # type: ignore

    @property
    def memory_request(self) -> Optional[int]:
        return self.get("memory_request")  # type: ignore

    @property
    def memory_limit(self) -> Optional[int]:
        return self.get("memory_limit")  # type: ignore

    @property
    def amd_gpu_limit(self) -> Optional[int]:
        return self.get("amd_gpu_limit")  # type: ignore

    @property
    def nvidia_gpu_limit(self) -> Optional[int]:
        return self.get("nvidia_gpu_limit")  # type: ignore

    @property
    def created_time(self) -> str:
        return self.get("created_time")  # type: ignore

    @property
    def last_deployed_time(self) -> str:
        return self.get("last_deployed_time")  # type: ignore

    @property
    def bundle_id(self) -> Optional[str]:
        return self.get("bundle_id")  # type: ignore

    @property
    def app_mode(self) -> str:
        return self.get("app_mode")  # type: ignore

    @property
    def content_category(self) -> Optional[str]:
        return self.get("content_category")  # type: ignore

    @property
    def parameterized(self) -> bool:
        return self.get("parameterized")  # type: ignore

    @property
    def cluster_name(self) -> Optional[str]:
        return self.get("cluster_name")  # type: ignore

    @property
    def image_name(self) -> Optional[str]:
        return self.get("image_name")  # type: ignore

    @property
    def default_image_name(self) -> Optional[str]:
        return self.get("default_image_name")  # type: ignore

    @property
    def default_r_environment_management(self) -> Optional[bool]:
        return self.get("default_r_environment_management")  # type: ignore

    @property
    def default_py_environment_management(self) -> Optional[bool]:
        return self.get("default_py_environment_management")  # type: ignore

    @property
    def service_account_name(self) -> Optional[str]:
        return self.get("service_account_name")  # type: ignore

    @property
    def r_version(self) -> Optional[str]:
        return self.get("r_version")  # type: ignore

    @property
    def r_environment_management(self) -> Optional[bool]:
        return self.get("r_environment_management")  # type: ignore

    @property
    def py_version(self) -> Optional[str]:
        return self.get("py_version")  # type: ignore

    @property
    def py_environment_management(self) -> Optional[bool]:
        return self.get("py_environment_management")  # type: ignore

    @property
    def quarto_version(self) -> Optional[str]:
        return self.get("quarto_version")  # type: ignore

    @property
    def run_as(self) -> Optional[str]:
        return self.get("run_as")  # type: ignore

    @property
    def run_as_current_user(self) -> bool:
        return self.get("run_as_current_user")  # type: ignore

    @property
    def owner_guid(self) -> str:
        return self.get("owner_guid")  # type: ignore

    @property
    def content_url(self) -> str:
        return self.get("content_url")  # type: ignore

    @property
    def dashboard_url(self) -> str:
        return self.get("dashboard_url")  # type: ignore

    @property
    def app_role(self) -> str:
        return self.get("app_role")  # type: ignore

    @property
    def tags(self) -> List[dict]:
        return self.get("tags", [])

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

    def _get_default_params(self) -> dict:
        """Build default parameters for GET requests.

        Returns
        -------
        dict
        """
        params = {}
        if self.owner_guid:
            params["owner_guid"] = self.owner_guid
        return params

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
        name: str = ...,
        title: Optional[str] = ...,
        description: str = ...,
        access_type: str = ...,
        connection_timeout: Optional[int] = ...,
        read_timeout: Optional[int] = ...,
        init_timeout: Optional[int] = ...,
        idle_timeout: Optional[int] = ...,
        max_processes: Optional[int] = ...,
        min_processes: Optional[int] = ...,
        max_conns_per_process: Optional[int] = ...,
        load_factor: Optional[float] = ...,
        cpu_request: Optional[float] = ...,
        cpu_limit: Optional[float] = ...,
        memory_request: Optional[int] = ...,
        memory_limit: Optional[int] = ...,
        amd_gpu_limit: Optional[int] = ...,
        nvidia_gpu_limit: Optional[int] = ...,
        run_as: Optional[str] = ...,
        run_as_current_user: Optional[bool] = ...,
        default_image_name: Optional[str] = ...,
        default_r_environment_management: Optional[bool] = ...,
        default_py_environment_management: Optional[bool] = ...,
        service_account_name: Optional[str] = ...,
    ) -> ContentItem:
        """Create a content item.

        Parameters
        ----------
        name : str, optional
        title : Optional[str], optional
        description : str, optional
        access_type : str, optional
        connection_timeout : Optional[int], optional
        read_timeout : Optional[int], optional
        init_timeout : Optional[int], optional
        idle_timeout : Optional[int], optional
        max_processes : Optional[int], optional
        min_processes : Optional[int], optional
        max_conns_per_process : Optional[int], optional
        load_factor : Optional[float], optional
        cpu_request : Optional[float], optional
        cpu_limit : Optional[float], optional
        memory_request : Optional[int], optional
        memory_limit : Optional[int], optional
        amd_gpu_limit : Optional[int], optional
        nvidia_gpu_limit : Optional[int], optional
        run_as : Optional[str], optional
        run_as_current_user : Optional[bool], optional
        default_image_name : Optional[str], optional
        default_r_environment_management : Optional[bool], optional
        default_py_environment_management : Optional[bool], optional
        service_account_name : Optional[str], optional

        Returns
        -------
        ContentItem
        """
        ...

    @overload
    def create(self, *args, **kwargs) -> ContentItem:
        """Create a content item.

        Returns
        -------
        ContentItem
        """
        ...

    def create(self, *args, **kwargs) -> ContentItem:
        """Create a content item.

        Returns
        -------
        ContentItem
        """
        body = dict(*args, **kwargs)
        path = "v1/content"
        url = self.url + path
        response = self.session.post(url, json=body)
        return ContentItem(self.params, **response.json())

    @overload
    def find(
        self,
        owner_guid: str = ...,
        name: str = ...,
        include: Optional[str] = "owner,tags",
    ) -> List[ContentItem]:
        """Find content items.

        Parameters
        ----------
        owner_guid : str, optional
            The owner's unique identifier, by default ...
        name : str, optional
            The simple URL friendly name, by default ...
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        List[ContentItem]
        """
        ...

    @overload
    def find(
        self, *args, include: Optional[str] = "owner,tags", **kwargs
    ) -> List[ContentItem]:
        """Find content items.

        Parameters
        ----------
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        List[ContentItem]
        """
        ...

    def find(
        self, *args, include: Optional[str] = "owner,tags", **kwargs
    ) -> List[ContentItem]:
        """Find content items.

        Parameters
        ----------
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        List[ContentItem]
        """
        params = self._get_default_params()
        params.update(args)
        params.update(kwargs)
        params["include"] = include
        path = "v1/content"
        url = self.url + path
        response = self.session.get(url, params=params)
        return [
            ContentItem(
                self.params,
                **result,
            )
            for result in response.json()
        ]

    @overload
    def find_one(
        self,
        owner_guid: str = ...,
        name: str = ...,
        include: Optional[str] = "owner,tags",
    ) -> ContentItem | None:
        """Find content items.

        Parameters
        ----------
        owner_guid : str, optional
            The owner's unique identifier, by default ...
        name : str, optional
            The simple URL friendly name, by default ...
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        ContentItem | None
        """
        ...

    @overload
    def find_one(
        self, *args, include: Optional[str] = "owner,tags", **kwargs
    ) -> ContentItem | None:
        """Find content items.

        Parameters
        ----------
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        ContentItem | None
        """
        ...

    def find_one(
        self, *args, include: Optional[str] = "owner,tags", **kwargs
    ) -> ContentItem | None:
        """Find content items.

        Parameters
        ----------
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        ContentItem | None
        """
        items = self.find(*args, include=include, **kwargs)
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
        url = self.url + path
        response = self.session.get(url)
        return ContentItem(self.params, **response.json())
