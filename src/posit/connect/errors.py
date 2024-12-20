import json

from typing_extensions import Any


class ClientError(Exception):
    def __init__(
        self,
        error_code: int,
        error_message: str,
        http_status: int,
        http_message: str,
        payload: Any = None,
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.http_status = http_status
        self.http_message = http_message
        self.payload = payload
        super().__init__(
            json.dumps(
                {
                    "error_code": error_code,
                    "error_message": error_message,
                    "http_status": http_status,
                    "http_message": http_message,
                    "payload": payload,
                },
            ),
        )
