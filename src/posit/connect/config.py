import os
import dataclasses

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
            value = os.environ.get("CONNECT_API_KEY")
            if value:
                return value
            if value == "":
                raise ValueError(
                    "Invalid value for 'CONNECT_API_KEY': Must be a non-empty string."
                )

        if key == "endpoint":
            value = os.environ.get("CONNECT_SERVER")
            if value:
                return os.path.join(value, "__api__")
            if value == "":
                raise ValueError(
                    "Invalid value for 'CONNECT_SERVER': Must be a non-empty string."
                )

        return None


class ConfigBuilder:
    def __init__(
        self, providers: List[ConfigProvider] = [EnvironmentConfigProvider()]
    ) -> None:
        self._config = Config()
        self._providers = providers

    def build(self) -> Config:
        for field in dataclasses.fields(Config):
            key = field.name
            if not getattr(self._config, key):
                setattr(
                    self._config,
                    key,
                    next(
                        (provider.get_value(key) for provider in self._providers), None
                    ),
                )
        return self._config

    def set_api_key(self, api_key: str):
        self._config.api_key = api_key

    def set_endpoint(self, endpoint: str):
        self._config.endpoint = endpoint
