import textwrap
from .support import create_github_issue_link


class ClientError(Exception):
    def __init__(
        self,
        error_code: int,
        error_message: str,
        http_status: int,
        http_message: str,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.http_status = http_status
        self.http_message = http_message
        title = f"fix: client error code {error_code}"
        body = f"{error_message} (Error Code: {error_code}, HTTP Status: {http_status} {http_message})"
        issue_link = create_github_issue_link(title, body)
        message = f"""{body}

        If you believe this error should not occur and you have confirmed that
        you are not doing anything wrong, please report this issue using the
        following link. Your feedback is appreciated and helps us improve.

        {issue_link}
        """
        super().__init__(textwrap.dedent(message))
