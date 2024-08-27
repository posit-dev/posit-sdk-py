from abc import ABC
from dataclasses import dataclass
from typing import Any

import requests

from .urls import Url


@dataclass(frozen=True)
class ResourceParameters:
    """Shared parameter object for resources.

    Attributes
    ----------
    session: requests.Session
    url: str
        The Connect API base URL (e.g., https://connect.example.com/__api__)
    """

    session: requests.Session
    url: Url


class Resource(ABC, dict):
    def __init__(self, params: ResourceParameters, **kwargs):
        super().__init__(**kwargs)
        self.params: ResourceParameters
        super().__setattr__("params", params)
        self.session: requests.Session
        super().__setattr__("session", params.session)
        self.url: Url
        super().__setattr__("url", params.url)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("cannot set attributes: use update() instead")

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class Resources(ABC):
    def __init__(self, params: ResourceParameters) -> None:
        self.params = params
        self.session = params.session
        self.url = params.url
