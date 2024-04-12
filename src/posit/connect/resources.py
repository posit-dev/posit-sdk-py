from abc import ABC
from typing import Any

import requests

from .config import Config


class Resource(ABC, dict):
    def __init__(self, config: Config, session: requests.Session, **kwargs):
        super().__init__(**kwargs)
        self.config: Config
        super().__setattr__("config", config)
        self.session: requests.Session
        super().__setattr__("session", session)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("cannot set attributes: use update() instead")


class Resources(ABC):
    def __init__(self, config: Config, session: requests.Session) -> None:
        self.config = config
        self.session = session
