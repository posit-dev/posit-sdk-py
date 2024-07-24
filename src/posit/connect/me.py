from posit.connect.resources import ResourceParameters

from .users import User


def get(params: ResourceParameters) -> User:
    """
    Gets the current user.

    Args:
        config (Config): The configuration object containing the URL.
        session (requests.Session): The session object used for making HTTP requests.

    Returns
    -------
        User: The current user.
    """
    url = params.url + "v1/user"
    response = params.session.get(url)
    return User(params, **response.json())
