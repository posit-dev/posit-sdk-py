from dataclasses import dataclass

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


class Resource(dict):
    def __init__(self, /, params: ResourceParameters, **kwargs):
        self.params = params
        super().__init__(**kwargs)

    def update(self, *args, **kwargs):
        super().update(*args, **kwargs)


class Resources:
    def __init__(self, params: ResourceParameters) -> None:
        self.params = params
        self.session = params.session
        self.url = params.url
