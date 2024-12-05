from unittest.mock import Mock

import pytest
import requests
import responses
from responses import matchers

from posit.connect.client import Client
from posit.connect.groups import Group
from posit.connect.users import User

from .api import load_mock, load_mock_dict

session = Mock()
url = Mock()


class TestUserContent:
    """Check behavior of content attribute."""

    @responses.activate
    def test_find(self):
        """Check GET /v1/content call includes owner_guid query parameter."""
        # behavior
        mock_get_user = responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )

        mock_get_content = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content?owner_guid=20a79ce3-6e87-4522-9faf-be24228800a4.json"),
            match=[
                matchers.query_param_matcher(
                    {"owner_guid": "20a79ce3-6e87-4522-9faf-be24228800a4"},
                    strict_match=False,
                ),
            ],
        )

        # setup
        c = Client(api_key="12345", url="https://connect.example/")
        user = c.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")

        # invoke
        content = user.content.find()

        # assert
        assert mock_get_user.call_count == 1
        assert mock_get_content.call_count == 1
        assert len(content) == 1


class TestUserLock:
    @responses.activate
    def test_lock(self):
        responses.get(
            "https://connect.example/__api__/v1/users/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6",
            json=load_mock("v1/users/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6.json"),
        )
        c = Client(api_key="12345", url="https://connect.example/")
        user = c.users.get("a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6")
        assert user["guid"] == "a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6"

        responses.get(
            "https://connect.example/__api__/v1/user",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        responses.post(
            "https://connect.example/__api__/v1/users/a1b2c3d4-e5f6-g7h8-i9j0-k1l2m3n4o5p6/lock",
            match=[responses.matchers.json_params_matcher({"locked": True})],
        )
        user.lock()
        assert user["locked"]

    @responses.activate
    def test_lock_self_true(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        c = Client(api_key="12345", url="https://connect.example/")
        user = c.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert user["guid"] == "20a79ce3-6e87-4522-9faf-be24228800a4"

        responses.get(
            "https://connect.example/__api__/v1/user",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        responses.post(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4/lock",
            match=[responses.matchers.json_params_matcher({"locked": True})],
        )
        user.lock(force=True)
        assert user["locked"]

    @responses.activate
    def test_lock_self_false(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        c = Client(api_key="12345", url="https://connect.example/")
        user = c.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert user["guid"] == "20a79ce3-6e87-4522-9faf-be24228800a4"

        responses.get(
            "https://connect.example/__api__/v1/user",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        responses.post(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4/lock",
            match=[responses.matchers.json_params_matcher({"locked": True})],
        )
        with pytest.raises(RuntimeError):
            user.lock(force=False)
        assert not user["locked"]


class TestUserUnlock:
    @responses.activate
    def test_unlock(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        c = Client(api_key="12345", url="https://connect.example/")
        user = c.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert user["guid"] == "20a79ce3-6e87-4522-9faf-be24228800a4"

        responses.post(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4/lock",
            match=[responses.matchers.json_params_matcher({"locked": False})],
        )
        user.unlock()
        assert not user["locked"]


class TestUserGroups:
    @responses.activate
    def test_groups(self):
        # Get user
        carlos_guid = "20a79ce3-6e87-4522-9faf-be24228800a4"
        carlos_empty_group_guid = "empty-group-guid"
        responses.get(
            f"https://connect.example/__api__/v1/users/{carlos_guid}",
            json=load_mock_dict(f"v1/users/{carlos_guid}.json"),
        )
        responses.get(
            f"https://connect.example/__api__/v1/groups/{carlos_empty_group_guid}/members?page_number=1&page_size=500",
            json=load_mock_dict(f"v1/groups/{carlos_empty_group_guid}/members.json"),
        )
        responses.get(
            "https://connect.example/__api__/v1/users",
            json=load_mock_dict("v1/users?page_number=1&page_size=500.jsonc"),
        )
        # Get groups
        responses.get(
            "https://connect.example/__api__/v1/groups",
            json=load_mock_dict("v1/groups.json"),
        )
        # Get group members
        group_guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        responses.get(
            f"https://connect.example/__api__/v1/groups/{group_guid}/members",
            json=load_mock_dict(f"v1/groups/{group_guid}/members.json"),
        )

        client = Client("https://connect.example/", "12345")

        carlos = client.users.get(carlos_guid)
        no_groups = carlos.groups.find()
        assert len(no_groups) == 0

        user = client.users.find()[1]
        assert user["guid"] == "87c12c08-11cd-4de1-8da3-12a7579c4998"

        groups = user.groups.find()
        assert isinstance(groups, list)
        assert len(groups) == 1
        group = groups[0]
        assert isinstance(group, Group)
        assert group["name"] == "Friends"

    @responses.activate
    def test_groups_add(self):
        group_guid = "new-group-guid"
        user_guid = "user-guid"
        responses.get(
            f"https://connect.example/__api__/v1/groups/{group_guid}",
            json={"guid": group_guid},
        )
        responses.post(
            f"https://connect.example/__api__/v1/groups/{group_guid}/members",
            json=[],
        )

        client = Client("https://connect.example/", "12345")

        user = User(client._ctx, guid=user_guid)
        new_group = Group(client._ctx, guid=group_guid)
        # Add via Group
        user.groups.add(new_group)
        # Add via guid
        user.groups.add(new_group["guid"])

        with pytest.raises(ValueError):
            user.groups.add("")

    @responses.activate
    def test_groups_delete(self):
        group_guid = "new-group-guid"
        user_guid = "user-guid"
        responses.get(
            f"https://connect.example/__api__/v1/groups/{group_guid}",
            json={"guid": group_guid},
        )
        responses.delete(
            f"https://connect.example/__api__/v1/groups/{group_guid}/members/{user_guid}",
            json=[],
        )

        client = Client("https://connect.example/", "12345")

        user = User(client._ctx, guid=user_guid)
        group = Group(client._ctx, guid=group_guid)

        # Delete via Group
        user.groups.delete(group)
        # Delete via guid
        user.groups.delete(group["guid"])

        with pytest.raises(ValueError):
            user.groups.delete("")


class TestUsers:
    @responses.activate
    def test_users_get(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )

        con = Client(api_key="12345", url="https://connect.example/")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert carlos["username"] == "carlos12"
        assert carlos["first_name"] == "Carlos"
        assert carlos["created_time"] == "2019-09-09T15:24:32Z"

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

        con = Client(api_key="12345", url="https://connect.example/")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert carlos["username"] == "carlos12"
        assert carlos["some_new_field"] == "some_new_value"

    @responses.activate
    def test_user_update(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        patch_request = responses.put(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            match=[responses.matchers.json_params_matcher({"first_name": "Carlitos"})],
            json={"first_name": "Carlitos"},
        )

        con = Client(api_key="12345", url="https://connect.example/")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")

        assert patch_request.call_count == 0
        assert carlos["first_name"] == "Carlos"

        carlos.update(first_name="Carlitos")

        assert patch_request.call_count == 1
        assert carlos["first_name"] == "Carlitos"

    @responses.activate
    def test_user_update_server_error(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        responses.put(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            status=500,
        )

        con = Client(api_key="12345", url="https://connect.example/")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        with pytest.raises(requests.HTTPError, match="500 Server Error"):
            carlos.update(first_name="Carlitos")

    @responses.activate
    def test_count(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            json=load_mock("v1/users?page_number=1&page_size=500.jsonc"),
            match=[responses.matchers.query_param_matcher({"page_size": 1})],
        )
        con = Client(api_key="12345", url="https://connect.example/")
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
        con = Client(api_key="12345", url="https://connect.example/")
        user = con.users.find_one()
        assert user
        assert user["username"] == "al"
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
                    },
                ),
            ],
            json=load_mock("v1/users?page_number=1&page_size=500.jsonc"),
        )
        con = Client(api_key="12345", url="https://connect.example/")
        con.users.find_one(key1="value1", key2="value2", key3="value3")  # pyright: ignore[reportCallIssue]
        assert mock_get.call_count == 1

    @responses.activate
    def test_empty_results(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            json={"total": 0, "current_page": 1, "results": []},
        )

        con = Client(api_key="12345", url="https://connect.example/")
        user = con.users.find_one()
        assert user is None


class TestUsersFind:
    @responses.activate
    def test_default(self):
        # validate response body is parsed and returned
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[responses.matchers.query_param_matcher({"page_size": 500, "page_number": 1})],
            json=load_mock("v1/users?page_number=1&page_size=500.jsonc"),
        )
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[responses.matchers.query_param_matcher({"page_size": 500, "page_number": 2})],
            json=load_mock("v1/users?page_number=2&page_size=500.jsonc"),
        )
        con = Client(api_key="12345", url="https://connect.example/")
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
        # validate input params are propagated to the query params
        params = {"key1": "value1", "key2": "value2", "key3": "value3"}
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
                    },
                ),
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
                    },
                ),
            ],
            json=load_mock("v1/users?page_number=2&page_size=500.jsonc"),
        )
        con = Client(api_key="12345", url="https://connect.example/")
        con.users.find_one(key1="value1", key2="value2", key3="value3")  # pyright: ignore[reportCallIssue]
        responses.assert_call_count(
            "https://connect.example/__api__/v1/users?key1=value1&key2=value2&key3=value3&page_number=1&page_size=500",
            1,
        )

    @responses.activate
    def test_params_not_dict_like(self):
        # validate input params are propagated to the query params
        con = Client(api_key="12345", url="https://connect.example/")
        not_dict_like = "string"
        with pytest.raises(TypeError):
            con.users.find(
                not_dict_like  # pyright: ignore[reportCallIssue]
            )
