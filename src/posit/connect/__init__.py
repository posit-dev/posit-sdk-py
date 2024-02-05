from typing import Optional

from .client import Client


def make_client(
    api_key: Optional[str] = None, endpoint: Optional[str] = None
) -> Client:
    client = Client(api_key=api_key, endpoint=endpoint)
    return client
