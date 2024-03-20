from __future__ import annotations

from typing import Any, Callable, List, Optional

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

    def update(  # type: ignore
        self,
        name: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        access_type: Optional[str] = None,
        owner_guid: Optional[str] = None,
        connection_timeout: Optional[int] = None,
        read_timeout: Optional[int] = None,
        init_timeout: Optional[int] = None,
        idle_timeout: Optional[int] = None,
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
        run_as: Optional[str] = None,
        run_as_current_user: Optional[bool] = None,
        default_image_name: Optional[str] = None,
        default_r_environment_management: Optional[bool] = None,
        default_py_environment_management: Optional[bool] = None,
        service_account_name: Optional[str] = None,
    ) -> None:
        data: dict[str, Any] = {}
        if name is not None:
            data["name"] = name
        if title is not None:
            data["title"] = title
        if description is not None:
            data["description"] = description
        if access_type is not None:
            data["access_type"] = access_type
        if owner_guid is not None:
            data["owner_guid"] = owner_guid
        if connection_timeout is not None:
            data["connection_timeout"] = connection_timeout
        if read_timeout is not None:
            data["read_timeout"] = read_timeout
        if init_timeout is not None:
            data["init_timeout"] = init_timeout
        if idle_timeout is not None:
            data["idle_timeout"] = idle_timeout
        if max_processes is not None:
            data["max_processes"] = max_processes
        if min_processes is not None:
            data["min_processes"] = min_processes
        if max_conns_per_process is not None:
            data["max_conns_per_process"] = max_conns_per_process
        if load_factor is not None:
            data["load_factor"] = load_factor
        if cpu_request is not None:
            data["cpu_request"] = cpu_request
        if cpu_limit is not None:
            data["cpu_limit"] = cpu_limit
        if memory_request is not None:
            data["memory_request"] = memory_request
        if memory_limit is not None:
            data["memory_limit"] = memory_limit
        if amd_gpu_limit is not None:
            data["amd_gpu_limit"] = amd_gpu_limit
        if nvidia_gpu_limit is not None:
            data["nvidia_gpu_limit"] = nvidia_gpu_limit
        if run_as is not None:
            data["run_as"] = run_as
        if run_as_current_user is not None:
            data["run_as_current_user"] = run_as_current_user
        if default_image_name is not None:
            data["default_image_name"] = default_image_name
        if default_r_environment_management is not None:
            data["default_r_environment_management"] = default_r_environment_management
        if default_py_environment_management is not None:
            data["default_py_environment_management"] = (
                default_py_environment_management
            )
        if service_account_name is not None:
            data["service_account_name"] = service_account_name

        if len(data) == 0:
            return

        response = self.session.patch(self.url, json=data)
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
                session=self.session,
                url=urls.append_path(self.url, result["guid"]),
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
                session=self.session,
                url=urls.append_path(self.url, result["guid"]),
                **result,
            )
            if filter(item):
                return item
        return None

    def get(self, id: str) -> ContentItem:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        return ContentItem(self.session, url, **response.json())

    def create(self) -> ContentItem:
        raise NotImplementedError()

    def update(self) -> ContentItem:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()

    def count(self) -> int:
        results = self.session.get(self.url).json()
        return len(results)
