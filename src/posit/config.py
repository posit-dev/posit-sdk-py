import os

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Config:
    api_key: Optional[str] = None
    endpoint: Optional[str] = None


class ConfigProvider(ABC):
    @abstractmethod
    def get_value(self, key: str) -> Optional[str]:
        raise NotImplementedError  # pragma: no cover


class EnvironmentConfigProvider(ConfigProvider):
    def get_value(self, key: str) -> Optional[str]:
        if key == "api_key":
            return os.environ.get("CONNECT_API_KEY")

        if key == "endpoint":
            return os.environ.get("CONNECT_ENDPOINT")

        return None


class ConfigBuilder:
    def __init__(
        self, providers: List[ConfigProvider] = [EnvironmentConfigProvider()]
    ) -> None:
        self._config = Config()
        self._providers = providers

    def build(self) -> Config:
        for key in Config.__annotations__:
            if not getattr(self._config, key):
                setattr(
                    self._config,
                    key,
                    next(
                        (provider.get_value(key) for provider in self._providers), None
                    ),
                )
        return self._config

    def set_api_key(self, api_key: Optional[str]):
        self._config.api_key = api_key

    def set_endpoint(self, endpoint: Optional[str]):
        self._config.endpoint = endpoint
