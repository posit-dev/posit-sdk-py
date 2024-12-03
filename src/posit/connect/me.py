from .context import Context
from .users import User


def get(ctx: Context) -> User:
    """
    Gets the current user.

    Args:
        config (Config): The configuration object containing the URL.
        session (requests.Session): The session object used for making HTTP requests.

    Returns
    -------
        User: The current user.
    """
    url = ctx.url + "v1/user"
    response = ctx.session.get(url)
    return User(ctx, **response.json())
