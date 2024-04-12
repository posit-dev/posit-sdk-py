import warnings

from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

import requests

from . import config


class Resource(ABC, dict):
    def __init__(self, session: requests.Session, **kwargs):
        super().__init__(**kwargs)
        self.session: requests.Session
        super().__setattr__("session", session)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("cannot set attributes: use update() instead")


class Resources(ABC):
    def __init__(self, session: requests.Session) -> None:
        self.session = session
