from __future__ import annotations

from typing import Any


def drop_none(x: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in x.items() if v is not None}


def assert_guid(guid: Any) -> str:
    assert isinstance(guid, str), "Expected 'guid' to be a string"
    assert len(guid) > 0, "Expected 'guid' to be non-empty"
    return guid


def assert_content_guid(content_guid: str):
    assert isinstance(content_guid, str), "Expected 'content_guid' to be a string"
    assert len(content_guid) > 0, "Expected 'content_guid' to be non-empty"
