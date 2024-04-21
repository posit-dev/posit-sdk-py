import requests

from dataclasses import dataclass

from . import context, urls


@dataclass()
class Context:
    api_key: str
    session: requests.Session
    url: urls.Url
