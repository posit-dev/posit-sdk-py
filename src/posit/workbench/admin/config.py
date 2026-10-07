"""Client configuration for the Bearer-token Workbench launcher API client."""

from __future__ import annotations

import os

from ..urls import Url


def _get_api_key(api_key: str | None) -> str:
    value = api_key or os.environ.get("WORKBENCH_API_KEY")
    if not value:
        raise ValueError(
            "Invalid value for 'WORKBENCH_API_KEY': Must be a non-empty string. "
            "Pass api_key explicitly or set the WORKBENCH_API_KEY environment variable.",
        )
    return value


def _get_url(url: str | None) -> Url:
    value = url or os.environ.get("WORKBENCH_SERVER")
    if not value:
        raise ValueError(
            "Invalid value for 'WORKBENCH_SERVER': Must be a non-empty string. "
            "Pass url explicitly or set the WORKBENCH_SERVER environment variable.",
        )
    return Url(value)


class Config:
    """Resolved client configuration (server URL + API token)."""

    def __init__(self, url: str | None = None, api_key: str | None = None) -> None:
        self.url = _get_url(url)
        self.api_key = _get_api_key(api_key)
