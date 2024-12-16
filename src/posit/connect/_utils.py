from __future__ import annotations

from typing_extensions import Any


def drop_none(x: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in x.items() if v is not None}
