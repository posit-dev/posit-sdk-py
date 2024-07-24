from dataclasses import dataclass

import requests


@dataclass(frozen=True)
class Context:
    """Context for information shared across the resource stack.

    Attributes
    ----------
        session: request.Session
        url: str
            The Connect API URL (e.g., 'https://connect.example.com/__api__')

    Notes
    -----
    This class should only contain attributes that are common across all resources.

    Adding attributes for convenience that are not required by all resources is an anti-pattern.
    """

    session: requests.Session
    url: str
