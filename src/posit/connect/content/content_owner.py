from typing import Optional

from ..resources import Resource


class ContentOwner(Resource):
    """Content item owner resource."""

    @property
    def guid(self) -> str:
        return self.get("guid")  # type: ignore

    @property
    def username(self) -> str:
        return self.get("username")  # type: ignore

    @property
    def first_name(self) -> Optional[str]:
        return self.get("first_name")  # type: ignore

    @property
    def last_name(self) -> Optional[str]:
        return self.get("last_name")  # type: ignore
