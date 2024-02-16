import pytest

from unittest.mock import patch

from .users import Users


@pytest.fixture
def mock_config():
    with patch("posit.connect.users.Config") as mock:
        yield mock.return_value


@pytest.fixture
def mock_session():
    with patch("posit.connect.users.Session") as mock:
        yield mock.return_value


class TestUsers:
    def test_init(self, mock_config, mock_session):
        with pytest.raises(ValueError):
            Users(mock_config, mock_session, page_size=9999)
