import pytest

from unittest.mock import MagicMock, patch

from .users import Users, User


class TestUsers:
    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_init(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        session = Session.return_value
        users = Users(config, session)
        assert users._config == config
        assert users._session == session

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_iter(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        session = Session.return_value
        users = Users(config, session)
        iter(users)
        assert users._index == 0

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_next_with_empty_result_set(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        session = Session.return_value
        users = Users(config, session)
        with patch("posit.connect.users.get_users") as get_users:
            get_users.return_value = [], True
            with pytest.raises(StopIteration):
                next(users)

        assert users._cached_users == []
        assert users._exhausted is True
        assert users._index == 0
        assert users._page_number == 1

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_next_with_single_page(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        config.endpoint = "http://foo.bar"
        session = Session.return_value
        users = Users(config, session)
        user: User = {}
        with patch("posit.connect.users.get_users") as get_users:
            get_users.return_value = [user], True
            assert next(users) == user
            get_users.assert_called_with(config.endpoint, session, 0)

            with pytest.raises(StopIteration):
                next(users)

        assert users._cached_users == [user]
        assert users._exhausted is True
        assert users._index == 1
        assert users._page_number == 1

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_next_with_multiple_pages(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        config.endpoint = "http://foo.bar"
        session = Session.return_value
        users = Users(config, session)
        user: User = {}
        with patch("posit.connect.users.get_users") as get_users:
            get_users.return_value = [user], False
            assert next(users) == user
            get_users.assert_called_with(config.endpoint, session, 0)

            get_users.return_value = [user], True
            assert next(users) == user
            get_users.assert_called_with(config.endpoint, session, 1)

        assert users._cached_users == [user, user]
        assert users._exhausted is True
        assert users._index == 2
        assert users._page_number == 2

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_find(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        config.endpoint = "http://foo.bar"
        session = Session.return_value
        users = Users(config, session)
        user = {"username": "foobar"}
        with patch("posit.connect.users.get_users") as get_users:
            get_users.return_value = [user], True
            found = users.find({"username": "foobar"})
            assert list(found) == [user]

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_find_miss(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        config.endpoint = "http://foo.bar"
        session = Session.return_value
        users = Users(config, session)
        user = {"username": "foo"}
        with patch("posit.connect.users.get_users") as get_users:
            get_users.return_value = [user], True
            assert list(users.find({"username": "bar"})) == []

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_find_one(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        config.endpoint = "http://foo.bar"
        session = Session.return_value
        users = Users(config, session)
        user = {"username": "foobar"}
        with patch("posit.connect.users.get_users") as get_users:
            get_users.return_value = [user], True
            assert users.find_one({"username": "foobar"}) == user

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_find_one_miss(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        config.endpoint = "http://foo.bar"
        session = Session.return_value
        users = Users(config, session)
        user = {"username": "foo"}
        with patch("posit.connect.users.get_users") as get_users:
            get_users.return_value = [user], True
            assert users.find_one({"username": "bar"}) is None

    @patch("posit.connect.users.Session")
    @patch("posit.connect.users.Config")
    def test_get(self, Config: MagicMock, Session: MagicMock):
        config = Config.return_value
        config.endpoint = "http://foo.bar"

        user = {"guid": "foobar"}
        response = MagicMock()
        response.json = MagicMock()
        response.json.return_value = user
        session = Session.return_value
        session.get = MagicMock()
        session.get.return_value = response

        users = Users(config, session)
        assert users.get("foobar") == user
