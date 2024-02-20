import pytest

from unittest.mock import patch

from .users import Users


@pytest.fixture
def mock_client():
    with patch("posit.connect.client.Client") as mock:
        yield mock.return_value


class TestUsers:
    def test_init(self, mock_client):
        with pytest.raises(ValueError):
            Users(mock_client, page_size=9999)
