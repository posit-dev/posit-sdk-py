"""Client configuration."""

from __future__ import annotations

import os

from . import urls


def reset():
    Config.instance = None


class Config:
    """Configuration object."""

    instance = None
    properties: dict

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super(Config, cls).__new__(cls)
            cls.instance.properties = {}
        return cls.instance

    @property
    def api_key(self) -> str:
        api_key = self.properties.get("api_key")
        if api_key is None:
            api_key = os.environ.get("CONNECT_API_KEY")
            if not api_key:
                raise ValueError(
                    "Invalid value for 'CONNECT_API_KEY': Must be a non-empty string."
                )
        return api_key

    @api_key.setter
    def api_key(self, api_key: str) -> None:
        self.properties["api_key"] = api_key

    @property
    def url(self) -> urls.Url:
        url = self.properties.get("url")
        if url is None:
            url = os.environ.get("CONNECT_SERVER")
            if not url:
                raise ValueError(
                    "Invalid value for 'CONNECT_SERVER': Must be a non-empty string."
                )
        return urls.create(url)

    @url.setter
    def url(self, url: urls.Url) -> None:
        self.properties["url"] = url
