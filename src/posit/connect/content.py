from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional

from requests import Session

from . import urls

from .config import Config
from .resources import Resource, Resources


@dataclass(init=False)
class ContentItem(Resource):
    guid: str
    name: str
    title: Optional[str]
    description: str
    access_type: str
    connection_timeout: Optional[int]
    read_timeout: Optional[int]
    init_timeout: Optional[int]
    idle_timeout: Optional[int]
    max_processes: Optional[int]
    min_processes: Optional[int]
    max_conns_per_process: Optional[int]
    load_factor: Optional[float]
    cpu_request: Optional[float]
    cpu_limit: Optional[float]
    memory_request: Optional[int]
    memory_limit: Optional[int]
    amd_gpu_limit: Optional[int]
    nvidia_gpu_limit: Optional[int]
    created_time: str
    last_deployed_time: str
    bundle_id: Optional[str]
    app_mode: str
    content_category: Optional[str]
    parameterized: bool
    cluster_name: Optional[str]
    image_name: Optional[str]
    default_image_name: Optional[str]
    default_r_environment_management: Optional[bool]
    default_py_environment_management: Optional[bool]
    service_account_name: Optional[str]
    r_version: Optional[str]
    r_environment_management: Optional[bool]
    py_version: Optional[str]
    py_environment_management: Optional[bool]
    quarto_version: Optional[str]
    run_as: Optional[str]
    run_as_current_user: bool
    owner_guid: str
    content_url: str
    dashboard_url: str
    app_role: str
    id: str


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
