import os

from requests import Session, Response


class Users:
    def __init__(self, endpoint: str, session: Session) -> None:
        self._endpoint = endpoint
        self._session = session

    def get_user(self, user_id: str) -> Response:
        endpoint = os.path.join(self._endpoint, "__api__/v1/users", user_id)
        return self._session.get(endpoint)

    def get_current_user(self) -> Response:
        endpoint = os.path.join(self._endpoint, "__api__/v1/user")
        return self._session.get(endpoint)
