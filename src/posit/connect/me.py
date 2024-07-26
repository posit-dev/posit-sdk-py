import requests

from .config import Config
from .users import User


def get(config: Config, session: requests.Session) -> User:
    """
    Gets the current user.

    Args:
        config (Config): The configuration object containing the URL.
        session (requests.Session): The session object used for making HTTP requests.

    Returns
    -------
        User: The current user.
    """
    url = config.url + "v1/user"
    response = session.get(url)
    return User(config, session, **response.json())
