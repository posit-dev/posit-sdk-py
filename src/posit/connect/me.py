import requests

from . import urls

from . import config
from .users import User


def get(config: config.Config, session: requests.Session) -> User:
    """
    Gets the current user.

    Args:
        config (Config): The configuration object containing the URL.
        session (requests.Session): The session object used for making HTTP requests.

    Returns
    -------
        User: The current user.
    """
    url = urls.append(config.url, "v1/user")
    response = session.get(url)
    return User(config, session, **response.json())
