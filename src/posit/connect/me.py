from . import urls

from .context import Context
from .users import User


def get(ctx: Context) -> User:
    """Get the current user.

    Get the user information from Connect for the user assumed via the provided API key.

    Parameters
    ----------
    ctx : Context

    Returns
    -------
    User
    """
    url = urls.append(ctx.url, "v1/user")
    response = ctx.session.get(url)
    return User(ctx, **response.json())
