from unittest.mock import Mock

import pytest
import requests
import responses

from posit.connect.client import Client
from posit.connect.users import User

from .api import load_mock  # type: ignore

session = Mock()
url = Mock()


class TestUserAttributes:
    def setup_class(cls):
        cls.user = User(
            None,
            **load_mock("v1/users/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.json"),
        )

    def test_guid(self):
        assert self.user.guid == "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"

    def test_email(self):
        assert self.user.email == "random_email@example.com"

    def test_username(self):
        assert self.user.username == "random_username"

    def test_first_name(self):
        assert self.user.first_name == "Random"

    def test_last_name(self):
        assert self.user.last_name == "User"

    def test_user_role(self):
        assert self.user.user_role == "admin"

    def test_created_time(self):
        assert self.user.created_time == "2022-01-01T00:00:00Z"

    def test_updated_time(self):
        assert self.user.updated_time == "2022-03-15T12:34:56Z"

    def test_active_time(self):
        assert self.user.active_time == "2022-02-28T18:30:00Z"

    def test_confirmed(self):
        assert self.user.confirmed is False

    def test_locked(self):
        assert self.user.locked is True


class TestUserLock:
    @responses.activate
    def test_lock(self):
        responses.get(
            "https://connect.example/__api__/v1/users/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
            json=load_mock(
                "v1/users/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.json"
            ),
        )
        c = Client("12345", "https://connect.example/__api__")
        user = c.users.get("a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6")
        assert user.guid == "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"

        responses.get(
            "https://connect.example/__api__/v1/user",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )
        responses.post(
            "https://connect.example/__api__/v1/users/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6/lock",
            match=[responses.matchers.json_params_matcher({"locked": True})],
        )
        user.lock()
        assert user.locked

    @responses.activate
    def test_lock_self_true(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )
        c = Client("12345", "https://connect.example/__api__")
        user = c.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert user.guid == "20a79ce3-6e87-4522-9faf-be24228800a4"

        responses.get(
            "https://connect.example/__api__/v1/user",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )
        responses.post(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4/lock",
            match=[responses.matchers.json_params_matcher({"locked": True})],
        )
        user.lock(force=True)
        assert user.locked

    @responses.activate
    def test_lock_self_false(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )
        c = Client("12345", "https://connect.example/__api__")
        user = c.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert user.guid == "20a79ce3-6e87-4522-9faf-be24228800a4"

        responses.get(
            "https://connect.example/__api__/v1/user",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )
        responses.post(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4/lock",
            match=[responses.matchers.json_params_matcher({"locked": True})],
        )
        with pytest.raises(RuntimeError):
            user.lock(force=False)
        assert not user.locked


class TestUserUnlock:
    @responses.activate
    def test_unlock(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )
        c = Client("12345", "https://connect.example/__api__")
        user = c.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert user.guid == "20a79ce3-6e87-4522-9faf-be24228800a4"

        responses.post(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4/lock",
            match=[responses.matchers.json_params_matcher({"locked": False})],
        )
        user.unlock()
        assert not user.locked


class TestUsers:
    @responses.activate
    def test_users_get(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )

        con = Client("12345", "https://connect.example/__api__")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert carlos.username == "carlos12"
        assert carlos.first_name == "Carlos"
        assert carlos.created_time == "2019-09-09T15:24:32Z"

    @responses.activate
    def test_users_get_extra_fields(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json={
                "guid": "20a79ce3-6e87-4522-9faf-be24228800a4",
                "username": "carlos12",
                "some_new_field": "some_new_value",
            },
        )

        con = Client("12345", "https://connect.example/__api__")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert carlos.username == "carlos12"
        assert carlos["some_new_field"] == "some_new_value"

    @responses.activate
    def test_user_update(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )
        patch_request = responses.put(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            match=[
                responses.matchers.json_params_matcher(
                    {"first_name": "Carlitos"}
                )
            ],
            json={"first_name": "Carlitos"},
        )

        con = Client("12345", "https://connect.example/__api__")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")

        assert patch_request.call_count == 0
        assert carlos.first_name == "Carlos"

        carlos.update(first_name="Carlitos")

        assert patch_request.call_count == 1
        assert carlos.first_name == "Carlitos"

    @responses.activate
    def test_user_update_server_error(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )
        responses.put(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            status=500,
        )

        con = Client("12345", "https://connect.example/__api__")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        with pytest.raises(requests.HTTPError, match="500 Server Error"):
            carlos.update(first_name="Carlitos")

    @responses.activate
    def test_user_cant_setattr(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock(
                "v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )

        con = Client("12345", "https://connect.example/__api__")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")

        with pytest.raises(
            AttributeError,
            match=r"cannot set attributes: use update\(\) instead",
        ):
            carlos.first_name = "Carlitos"

    @responses.activate
    def test_count(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            json=load_mock("v1/users?page_number=1&page_size=500.jsonc"),
            match=[responses.matchers.query_param_matcher({"page_size": 1})],
        )
        con = Client("12345", "https://connect.example/__api__")
        count = con.users.count()
        assert count == 3


class TestUsersFindOne:
    @responses.activate
    def test_default(self):
        # validate first result returned
        responses.get(
            "https://connect.example/__api__/v1/users",
            json=load_mock("v1/users?page_number=1&page_size=500.jsonc"),
        )
        con = Client("12345", "https://connect.example/__api__")
        user = con.users.find_one()
        assert user.username == "al"
        assert len(responses.calls) == 1

    @responses.activate
    def test_params(self):
        mock_get = responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {
                        "page_size": 500,
                        "page_number": 1,
                        "key1": "value1",
                        "key2": "value2",
                        "key3": "value3",
                    }
                )
            ],
            json=load_mock("v1/users?page_number=1&page_size=500.jsonc"),
        )
        con = Client("12345", "https://connect.example/__api__")
        con.users.find_one(key1="value1", key2="value2", key3="value3")
        assert mock_get.call_count == 1

    @responses.activate
    def test_empty_results(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            json={"total": 0, "current_page": 1, "results": []},
        )

        con = Client("12345", "https://connect.example/__api__")
        user = con.users.find_one()
        assert user is None


class TestUsersFind:
    @responses.activate
    def test_default(self):
        # validate response body is parsed and returned
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/users?page_number=1&page_size=500.jsonc"),
        )
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 2}
                )
            ],
            json=load_mock("v1/users?page_number=2&page_size=500.jsonc"),
        )

        con = Client("12345", "https://connect.example/__api__")
        users = con.users.find()
        assert len(users) == 3
        assert users[0] == {
            "email": "alice@connect.example",
            "username": "al",
            "first_name": "Alice",
            "last_name": "User",
            "user_role": "publisher",
            "created_time": "2017-08-08T15:24:32Z",
            "updated_time": "2023-03-02T20:25:06Z",
            "active_time": "2018-05-09T16:58:45Z",
            "confirmed": True,
            "locked": False,
            "guid": "a01792e3-2e67-402e-99af-be04a48da074",
        }

    @responses.activate
    def test_params(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {
                        "page_size": 500,
                        "page_number": 1,
                        "key1": "value1",
                        "key2": "value2",
                        "key3": "value3",
                    }
                )
            ],
            json=load_mock("v1/users?page_number=1&page_size=500.jsonc"),
        )
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {
                        "page_size": 500,
                        "page_number": 2,
                        "key1": "value1",
                        "key2": "value2",
                        "key3": "value3",
                    }
                )
            ],
            json=load_mock("v1/users?page_number=2&page_size=500.jsonc"),
        )
        con = Client("12345", "https://connect.example/__api__")
        con.users.find_one(key1="value1", key2="value2", key3="value3")
        responses.assert_call_count(
            "https://connect.example/__api__/v1/users?key1=value1&key2=value2&key3=value3&page_number=1&page_size=500",
            1,
        )

    @responses.activate
    def test_params_not_dict_like(self):
        # validate input params are propagated to the query params
        con = Client("12345", "https://connect.example/__api__")
        not_dict_like = "string"
        with pytest.raises(ValueError):
            con.users.find(not_dict_like)
