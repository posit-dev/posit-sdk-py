import pytest

from posit.connect.errors import ClientError


class TestClientError:
    def test(self):
        error_code = 0
        error_message = "foo"
        http_status = 404
        http_message = "Foo Bar"
        with pytest.raises(
            ClientError,
            match=r"foo \(Error Code: 0, HTTP Status: 404 Foo Bar\)",
        ):
            raise ClientError(
                error_code=error_code,
                error_message=error_message,
                http_status=http_status,
                http_message=http_message,
            )
