from typing import Dict, List, overload

from requests import Session

from . import urls
from .config import Config
from .resources import Resource, Resources


class EnvironmentVariable(Resource):
    def __init__(
        self, config: Config, session: Session, content_guid: str, **kwargs
    ):
        super().__init__(config, session, **kwargs)
        self.update(content_guid=content_guid)

    @property
    def name(self) -> str:
        return self["name"]

    def delete(self) -> None:
        path = f"v1/content/{self['content_guid']}/environment"
        url = urls.append(self.config.url, path)
        self.session.patch(url, json=[{"name": self.name, "value": None}])


class EnvironmentVariables(Resources):
    def __init__(
        self, config: Config, session: Session, content_guid: str
    ) -> None:
        super().__init__(config, session)
        self.content_guid = content_guid

    def fetch(self) -> List[EnvironmentVariable]:
        path = f"v1/content/{self.content_guid}/environment"
        url = urls.append(self.config.url, path)
        response = self.session.get(url)
        return [
            EnvironmentVariable(
                self.config, self.session, self.content_guid, name=name
            )
            for name in response.json()
        ]

    @overload
    def set(
        self, **variables: Dict[str, str]
    ) -> List[EnvironmentVariable]: ...

    @overload
    def set(self, **kwargs) -> List[EnvironmentVariable]: ...

    def set(self, **kwargs) -> List[EnvironmentVariable]:
        path = f"v1/content/{self.content_guid}/environment"
        url = urls.append(self.config.url, path)
        body = [{"name": key, "value": value} for key, value in kwargs.items()]
        response = self.session.patch(url, json=body)
        return [
            EnvironmentVariable(
                self.config, self.session, self.content_guid, name=name
            )
            for name in response.json()
        ]

    @overload
    def unset(self, *name: List[str]) -> List[EnvironmentVariable]: ...

    @overload
    def unset(self, *args) -> List[EnvironmentVariable]: ...

    def unset(self, *args) -> List[EnvironmentVariable]:
        path = f"v1/content/{self.content_guid}/environment"
        url = urls.append(self.config.url, path)
        body = [{"name": arg, "value": None} for arg in args]
        response = self.session.patch(url, json=body)
        return [
            EnvironmentVariable(
                self.config, self.session, self.content_guid, name=name
            )
            for name in response.json()
        ]
