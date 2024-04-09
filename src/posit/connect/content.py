"""Provides the Content resource interface."""

from __future__ import annotations

from typing import List, Optional, overload


from requests import Session

from . import urls

from .config import Config
from .bundles import Bundles
from .permissions import Permissions
from .resources import Resources, Resource


class ContentItem(Resource):
    """A piece of content."""

    # Relationships

    @property
    def bundles(self) -> Bundles:
        return Bundles(self.config, self.session, self.guid)

    @property
    def permissions(self) -> Permissions:
        return Permissions(self.config, self.session, self.guid)

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

    # CRUD Methods

    @property
    def tags(self) -> List[dict]:
        return self.get("tags", [])

    def delete(self) -> None:
        """Delete the content item."""
        path = f"v1/content/{self.guid}"
        url = urls.append_path(self.config.url, path)
        self.session.delete(url)

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
        url = urls.append_path(self.config.url, f"v1/content/{self.guid}")
        response = self.session.patch(url, json=body)
        super().update(**response.json())


class Content(Resources):
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/content")
        self.config = config
        self.session = session

    def count(self) -> int:
        """Count the number of content items.

        Returns
        -------
        int
        """
        results = self.session.get(self.url).json()
        return len(results)

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
        url = urls.append_path(self.config.url, path)
        response = self.session.post(url, json=body)
        return ContentItem(self.config, self.session, **response.json())

    @overload
    def find(
        self, owner_guid: str = ..., name: str = ..., include: str = "owner,tags"
    ) -> List[ContentItem]:
        """Find content items.

        Parameters
        ----------
        owner_guid : str, optional
            The owner's unique identifier, by default ...
        name : str, optional
            The simple URL friendly name, by default ...
        include : str, optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        List[ContentItem]
        """
        ...

    @overload
    def find(self, *args, **kwargs) -> List[ContentItem]:
        ...

    def find(self, *args, **kwargs) -> List[ContentItem]:
        """Find content items.

        Returns
        -------
        List[ContentItem]
        """
        params = dict(*args, **kwargs)
        if "include" not in params:
            params["include"] = "owner,tags"

        response = self.session.get(self.url, params=params)
        results = response.json()
        items = (
            ContentItem(
                config=self.config,
                session=self.session,
                **result,
            )
            for result in results
        )
        return [item for item in items]

    @overload
    def find_one(
        self, owner_guid: str = ..., name: str = ..., include: str = "owner,tags"
    ) -> ContentItem | None:
        """Find a content item.

        Parameters
        ----------
        owner_guid : str, optional
            The owner's unique identifier, by default ...
        name : str, optional
            The simple URL friendly name, by default ...
        include : str, optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        ContentItem | None
        """
        ...

    @overload
    def find_one(self, *args, **kwargs) -> ContentItem | None:
        """Find a content item.

        Returns
        -------
        ContentItem | None
        """
        ...

    def find_one(self, *args, **kwargs) -> ContentItem | None:
        """Find a content item.

        Returns
        -------
        ContentItem | None
        """
        items = self.find(*args, **kwargs)
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
        url = urls.append_path(self.url, guid)
        response = self.session.get(url)
        return ContentItem(self.config, self.session, **response.json())
