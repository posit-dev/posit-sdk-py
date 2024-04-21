import requests

from . import context, urls, users


def get(ctx: context.Context) -> users.User:
    """
    Gets the current user.

    Args:
        config (Config): The configuration object containing the URL.
        session (requests.Session): The session object used for making HTTP requests.

    Returns
    -------
        User: The current user.
    """
    url = urls.append(ctx.url, "v1/user")
    response = ctx.session.get(url)
    return users.User(ctx, **response.json())
