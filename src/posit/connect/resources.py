import warnings

from abc import ABC, abstractmethod
from typing import Any, TypeVar

import requests

from . import context


T = TypeVar("T")


class Resource(ABC, dict):
    def __init__(self, ctx: context.Context, **kwargs):
        super().__init__(**kwargs)
        self.ctx: context.Context
        super().__setattr__("ctx", ctx)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("cannot set attributes: use update() instead")


class Resources(ABC):
    def __init__(self, ctx: context.Context) -> None:
        self.ctx = ctx
