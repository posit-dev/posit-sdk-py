import importlib.metadata
import platform
import textwrap
import urllib.parse


def create_github_issue_link(title: str, body: str, footer: str = "") -> str:
    """Create a GitHub issue link.

    Create a GitHub issue link that can be presented to the user. The provided body is placed in a summary section. Additional system information is bundled with the issue for diagnostic purposes.

    Parameters
    ----------
    title: str
        The GitHub issue title.
    body: str
        The GitHub issue body.

    Examples
    --------
    >>> create_github_issue_link(
    ...     "fix: please fix this", "This thing needs fixed."
    ... )
    """
    body = f"""
    ### Summary

    {body}

    ### System Information

    - Package Version: {importlib.metadata.version('posit-sdk')}
    - Python Version: {platform.python_version()}
    - Python Compiler: {platform.python_compiler()}
    - Operating System Name: {platform.system()}
    - Operating System Architecture: {platform.machine()}
    - Operating System Version: {platform.version()}
    - Operating System Release: {platform.release()}
    """

    title = urllib.parse.quote(title)
    body = urllib.parse.quote(textwrap.dedent(body))
    return f"https://github.com/posit-dev/posit-sdk-py/issues/new?title={title}&body={body}"
