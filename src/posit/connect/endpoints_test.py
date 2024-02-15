from unittest.mock import MagicMock, Mock, patch

from .endpoints import get_users


class TestGetUsers:
    @patch("posit.connect.users.Session")
    def test(self, Session: MagicMock):
        session = Session.return_value
        get = session.get = Mock()
        response = get.return_value = Mock()
        json = response.json = Mock()
        json.return_value = {"results": ["foo"]}
        users, exhausted = get_users("http://foo.bar", session, page_number=0)
        assert users == ["foo"]
        assert exhausted
