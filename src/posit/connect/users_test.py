from unittest.mock import Mock

from .users import Users


class TestUsers:
    def test_get_user(self):
        session = Mock()
        session.get = Mock(return_value={})
        users = Users(endpoint="http://foo.bar/", session=session)
        response = users.get_user(user_id="foo")
        assert response == {}
        session.get.assert_called_once_with("http://foo.bar/v1/users/foo")

    def test_get_current_user(self):
        session = Mock()
        session.get = Mock(return_value={})
        users = Users(endpoint="http://foo.bar/", session=session)
        response = users.get_current_user()
        assert response == {}
        session.get.assert_called_once_with("http://foo.bar/v1/user")
