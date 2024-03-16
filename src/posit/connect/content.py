from __future__ import annotations

from typing import Callable, List, Optional

from requests import Session

from . import urls

from .config import Config
from .resources import Resources


class ContentItem(dict):
    @property
    def guid(self) -> str:
        return self.get("guid")

    @property
    def name(self) -> str:
        return self.get("name")

    @property
    def title(self) -> Optional[str]:
        return self.get("title")

    @property
    def description(self) -> str:
        return self.get("description")

    @property
    def access_type(self) -> str:
        return self.get("access_type")

    @property
    def connection_timeout(self) -> Optional[int]:
        return self.get("connection_timeout")

    @property
    def read_timeout(self) -> Optional[int]:
        return self.get("read_timeout")

    @property
    def init_timeout(self) -> Optional[int]:
        return self.get("init_timeout")

    @property
    def idle_timeout(self) -> Optional[int]:
        return self.get("idle_timeout")

    @property
    def max_processes(self) -> Optional[int]:
        return self.get("max_processes")

    @property
    def min_processes(self) -> Optional[int]:
        return self.get("min_processes")

    @property
    def max_conns_per_process(self) -> Optional[int]:
        return self.get("max_conns_per_process")

    @property
    def load_factor(self) -> Optional[float]:
        return self.get("load_factor")

    @property
    def cpu_request(self) -> Optional[float]:
        return self.get("cpu_request")

    @property
    def cpu_limit(self) -> Optional[float]:
        return self.get("cpu_limit")

    @property
    def memory_request(self) -> Optional[int]:
        return self.get("memory_request")

    @property
    def memory_limit(self) -> Optional[int]:
        return self.get("memory_limit")

    @property
    def amd_gpu_limit(self) -> Optional[int]:
        return self.get("amd_gpu_limit")

    @property
    def nvidia_gpu_limit(self) -> Optional[int]:
        return self.get("nvidia_gpu_limit")

    @property
    def created_time(self) -> str:
        return self.get("created_time")

    @property
    def last_deployed_time(self) -> str:
        return self.get("last_deployed_time")

    @property
    def bundle_id(self) -> Optional[str]:
        return self.get("bundle_id")

    @property
    def app_mode(self) -> str:
        return self.get("app_mode")

    @property
    def content_category(self) -> Optional[str]:
        return self.get("content_category")

    @property
    def parameterized(self) -> bool:
        return self.get("parameterized")

    @property
    def cluster_name(self) -> Optional[str]:
        return self.get("cluster_name")

    @property
    def image_name(self) -> Optional[str]:
        return self.get("image_name")

    @property
    def default_image_name(self) -> Optional[str]:
        return self.get("default_image_name")

    @property
    def default_r_environment_management(self) -> Optional[bool]:
        return self.get("default_r_environment_management")

    @property
    def default_py_environment_management(self) -> Optional[bool]:
        return self.get("default_py_environment_management")

    @property
    def service_account_name(self) -> Optional[str]:
        return self.get("service_account_name")

    @property
    def r_version(self) -> Optional[str]:
        return self.get("r_version")

    @property
    def r_environment_management(self) -> Optional[bool]:
        return self.get("r_environment_management")

    @property
    def py_version(self) -> Optional[str]:
        return self.get("py_version")

    @property
    def py_environment_management(self) -> Optional[bool]:
        return self.get("py_environment_management")

    @property
    def quarto_version(self) -> Optional[str]:
        return self.get("quarto_version")

    @property
    def run_as(self) -> Optional[str]:
        return self.get("run_as")

    @property
    def run_as_current_user(self) -> bool:
        return self.get("run_as_current_user")

    @property
    def owner_guid(self) -> str:
        return self.get("owner_guid")

    @property
    def content_url(self) -> str:
        return self.get("content_url")

    @property
    def dashboard_url(self) -> str:
        return self.get("dashboard_url")

    @property
    def app_role(self) -> str:
        return self.get("app_role")

    @property
    def id(self) -> str:
        return self.get("id")

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("Cannot set attributes: use update() instead")


class Content(Resources[ContentItem]):
    def __init__(self, config: Config, session: Session) -> None:
        self.url = urls.append_path(config.url, "v1/content")
        self.config = config
        self.session = session

    def find(
        self, filter: Callable[[ContentItem], bool] = lambda _: True
    ) -> List[ContentItem]:
        results = self.session.get(self.url).json()
        return [ContentItem(**c) for c in results if filter(ContentItem(**c))]

    def find_one(
        self, filter: Callable[[ContentItem], bool] = lambda _: True
    ) -> ContentItem | None:
        results = self.session.get(self.url).json()
        for c in results:
            content_item = ContentItem(**c)
            if filter(content_item):
                return content_item
        return None

    def get(self, id: str) -> ContentItem:
        url = urls.append_path(self.url, id)
        response = self.session.get(url)
        return ContentItem(**response.json())

    def create(self) -> ContentItem:
        raise NotImplementedError()

    def update(self) -> ContentItem:
        raise NotImplementedError()

    def delete(self) -> None:
        raise NotImplementedError()
