class ClientError(Exception):
    def __init__(
        self, error_code: int, error_message: str, http_status: int, http_message: str
    ):
        self.error_code = error_code
        self.error_message = error_message
        self.http_status = http_status
        self.http_message = http_message
        super().__init__(
            f"{error_message} (Error Code: {error_code}, HTTP Status: {http_status} {http_message})"
        )
