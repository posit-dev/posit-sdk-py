import json
from typing import Any


class ClientError(Exception):
    def __init__(
        self,
        error_code: int,
        error_message: str,
        http_status: int,
        http_message: str,
        payload: Any = None,
    ):
        message = {
            "error_code": error_code,
            "error_message": error_message,
            "http_status": http_status,
            "http_message": http_message,
            "payload": payload,
        }
        super().__init__(json.dumps(message))
