from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class Context:
    api_key: str
    session: requests.Session
    url: str
