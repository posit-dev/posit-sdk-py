import pytest

from posit.connect.errors import ClientError


def test():
    error_code = 0
    error_message = "error"
    http_status = 404
    http_message = "Error"
    with pytest.raises(
        ClientError,
        match='{"error_code": 0, "error_message": "error", "http_status": 404, "http_message": "Error", "payload": null}',
    ):
        raise ClientError(
            error_code=error_code,
            error_message=error_message,
            http_status=http_status,
            http_message=http_message,
        )


def test_payload_is_str():
    error_code = 0
    error_message = "error"
    http_status = 404
    http_message = "Error"
    payload = "This is an error payload"
    with pytest.raises(
        ClientError,
        match='{"error_code": 0, "error_message": "error", "http_status": 404, "http_message": "Error", "payload": "This is an error payload"}',
    ):
        raise ClientError(
            error_code=error_code,
            error_message=error_message,
            http_status=http_status,
            http_message=http_message,
            payload=payload,
        )


def test_payload_is_dict():
    error_code = 0
    error_message = "error"
    http_status = 404
    http_message = "Error"
    payload = {"message": "This is an error payload"}
    with pytest.raises(
        ClientError,
        match='{"error_code": 0, "error_message": "error", "http_status": 404, "http_message": "Error", "payload": {"message": "This is an error payload"}}',
    ):
        raise ClientError(
            error_code=error_code,
            error_message=error_message,
            http_status=http_status,
            http_message=http_message,
            payload=payload,
        )
