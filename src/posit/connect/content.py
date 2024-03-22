from __future__ import annotations

from typing import Callable, List, Optional, overload


from requests import Session

from . import urls

from .config import Config
from .resources import Resources, Resource


class ContentItem(Resource):
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
    def id(self) -> str:
        return self.get("id")  # type: ignore

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
        """
        Update the content item.

        Args:
            name (str): The name of the content.
            title (Optional[str]): The title of the content.
            description (str): The description of the content.
            access_type (str): The access type of the content.
            owner_guid (Optional[str]): The owner GUID of the content.
            connection_timeout (Optional[int]): The connection timeout in seconds.
            read_timeout (Optional[int]): The read timeout in seconds.
            init_timeout (Optional[int]): The initialization timeout in seconds.
            idle_timeout (Optional[int]): The idle timeout in seconds.
            max_processes (Optional[int]): The maximum number of processes.
            min_processes (Optional[int]): The minimum number of processes.
            max_conns_per_process (Optional[int]): The maximum number of connections per process.
            load_factor (Optional[float]): The load factor.
            cpu_request (Optional[float]): The CPU request.
            cpu_limit (Optional[float]): The CPU limit.
            memory_request (Optional[int]): The memory request in bytes.
            memory_limit (Optional[int]): The memory limit in bytes.
            amd_gpu_limit (Optional[int]): The AMD GPU limit.
            nvidia_gpu_limit (Optional[int]): The NVIDIA GPU limit.
            run_as (Optional[str]): The user to run as.
            run_as_current_user (Optional[bool]): Whether to run as the current user.
            default_image_name (Optional[str]): The default image name.
            default_r_environment_management (Optional[bool]): Whether to use default R environment management.
            default_py_environment_management (Optional[bool]): Whether to use default Python environment management.
            service_account_name (Optional[str]): The service account name.

        Returns:
            None
        """
        ...

    @overload
    def update(self, *args, **kwargs) -> None:
        """
        Update the content item.

        Args:
            *args
            **kwargs

        Returns:
            None
        """
        ...

    def update(self, *args, **kwargs) -> None:
        """
        Update the content item.

        Args:
            *args
            **kwargs

        Returns:
            None
        """
        body = dict(*args, **kwargs)
        url = urls.append_path(self.config.url, f"v1/content/{self.guid}")
        response = self.session.patch(url, json=body)
        super().update(**response.json())


class Content(Resources[ContentItem]):
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/content")
        self.config = config
        self.session = session

    def find(
        self, filter: Callable[[ContentItem], bool] = lambda _: True
    ) -> List[ContentItem]:
        results = self.session.get(self.url).json()
        items = (
            ContentItem(
                config=self.config,
                session=self.session,
                **result,
            )
            for result in results
        )
        return [item for item in items if filter(item)]

    def find_one(
        self, filter: Callable[[ContentItem], bool] = lambda _: True
    ) -> ContentItem | None:
        results = self.session.get(self.url).json()
        for result in results:
            item = ContentItem(
                config=self.config,
                session=self.session,
                **result,
            )
            if filter(item):
                return item
        return None

    def get(self, id: str) -> ContentItem:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        return ContentItem(self.config, self.session, **response.json())

    def create(self) -> ContentItem:
        raise NotImplementedError()

    def update(self) -> ContentItem:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()

    def count(self) -> int:
        results = self.session.get(self.url).json()
        return len(results)
