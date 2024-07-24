from abc import ABC
from typing import Any

from .config import Config
from .context import Context


class Resource(ABC, dict):
    def __init__(self, ctx: Context, **kwargs):
        super().__init__(**kwargs)
        self.ctx: Context
        super().__setattr__("ctx", ctx)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("cannot set attributes: use update() instead")


class Resources(ABC):
    def __init__(self, ctx: Context) -> None:
        self.ctx = ctx
