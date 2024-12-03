import random
import uuid

import pytest
import requests
import responses
from responses import matchers

from posit.connect.groups import Group
from posit.connect.permissions import Permission, Permissions
from posit.connect.resources import ResourceParameters
from posit.connect.urls import Url
from posit.connect.users import User

from .api import load_mock, load_mock_dict, load_mock_list


class TestPermissionDestroy:
    @responses.activate
    def test(self):
        # data
        uid = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_delete = responses.delete(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{uid}",
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        fake_permission = load_mock_dict(f"v1/content/{content_guid}/permissions/{uid}.json")
        permission = Permission(params, **fake_permission)

        # invoke
        permission.destroy()

        # assert
        assert mock_delete.call_count == 1


class TestPermissionUpdate:
    @responses.activate
    def test_request_shape(self):
        # test data
        uid = random.randint(0, 100)
        content_guid = str(uuid.uuid4())
        principal_guid = str(uuid.uuid4())
        principal_type = "principal_type"
        role = "role"
        extraneous = "extraneous"

        # define api behavior
        responses.put(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{uid}",
            json={
                # doesn't matter for this test
            },
            match=[
                # assertion
                matchers.json_params_matcher(
                    {
                        # validate that initial permission fields are set
                        "principal_guid": principal_guid,
                        "principal_type": principal_type,
                        "role": role,
                        # validate that arguments passed to update are set
                        "extraneous": extraneous,
                    },
                ),
            ],
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        permission = Permission(
            params,
            id=uid,
            content_guid=content_guid,
            principal_guid=principal_guid,
            principal_type=principal_type,
            role=role,
        )

        # invoke
        # assertion occurs in match above
        permission.update(extraneous=extraneous)

    @responses.activate
    def test_role_update(self):
        # test data
        old_role = "owner"
        new_role = "viewer"

        uid = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permission = load_mock_dict(f"v1/content/{content_guid}/permissions/{uid}.json")
        fake_permission.update(role=new_role)

        # define api behavior
        uid = random.randint(0, 100)
        content_guid = str(uuid.uuid4())
        responses.put(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{uid}",
            json=fake_permission,
            match=[
                matchers.json_params_matcher(
                    {
                        "principal_guid": None,
                        "principal_type": None,
                        "role": new_role,
                    },
                ),
            ],
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        permission = Permission(params, id=uid, content_guid=content_guid, role=old_role)

        # assert role change with respect to api response
        assert permission["role"] == old_role
        permission.update(role=new_role)
        assert permission["role"] == new_role


class TestPermissionsCount:
    @responses.activate
    def test(self):
        # test data
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permissions = load_mock_list(f"v1/content/{content_guid}/permissions.json")

        # define api behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permissions,
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        permissions = Permissions(params, content_guid=content_guid)

        # invoke
        count = permissions.count()

        # assert response
        assert count == len(fake_permissions)


class TestPermissionsCreate:
    @responses.activate
    def test(self):
        # data
        uid = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        principal_guid = str(uuid.uuid4())
        principal_type = "user"
        role = "owner"
        fake_permission = {
            **load_mock_dict(f"v1/content/{content_guid}/permissions/{uid}.json"),
            "principal_guid": principal_guid,
            "principal_type": principal_type,
            "role": role,
        }

        # behavior
        responses.post(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permission,
            match=[
                matchers.json_params_matcher(
                    {
                        "principal_guid": principal_guid,
                        "principal_type": principal_type,
                        "role": role,
                    },
                ),
            ],
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        permissions = Permissions(params, content_guid=content_guid)

        # invoke
        permission = permissions.create(
            principal_guid=principal_guid,
            principal_type=principal_type,
            role=role,
        )

        # assert
        assert permission == fake_permission


class TestPermissionsFind:
    @responses.activate
    def test(self):
        # test data
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permissions = load_mock(f"v1/content/{content_guid}/permissions.json")

        # define api behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permissions,
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        permissions = Permissions(params, content_guid=content_guid)

        # invoke
        permissions = permissions.find()

        # assert response
        assert permissions == fake_permissions


class TestPermissionsFindOne:
    @responses.activate
    def test(self):
        # test data
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permissions = load_mock_list(f"v1/content/{content_guid}/permissions.json")

        # define api behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permissions,
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        permissions = Permissions(params, content_guid=content_guid)

        # invoke
        permission = permissions.find_one()

        # assert response
        assert permission == fake_permissions[0]


class TestPermissionsGet:
    @responses.activate
    def test(self):
        # data
        uid = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permission = load_mock(f"v1/content/{content_guid}/permissions/{uid}.json")

        # behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{uid}",
            json=fake_permission,
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        permissions = Permissions(params, content_guid=content_guid)

        # invoke
        permission = permissions.get(uid)

        # assert
        assert permission == fake_permission


class TestPermissionsDestroy:
    @responses.activate
    def test_destroy(self):
        # data
        permission_uid = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permissions = load_mock_list(f"v1/content/{content_guid}/permissions.json")
        fake_followup_permissions = fake_permissions.copy()
        fake_followup_permissions.pop(0)
        fake_permission = load_mock_dict(
            f"v1/content/{content_guid}/permissions/{permission_uid}.json"
        )
        fake_user = load_mock_dict("v1/user.json")
        fake_group = load_mock_dict("v1/groups/6f300623-1e0c-48e6-a473-ddf630c0c0c3.json")

        # behavior

        # Used in internal for-loop
        mock_permissions_get = [
            responses.get(
                f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
                json=fake_permissions,
            ),
            responses.get(
                f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
                json=fake_followup_permissions,
            ),
        ]
        # permission delete
        mock_permission_delete = responses.delete(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{permission_uid}",
        )

        # setup
        params = ResourceParameters(requests.Session(), Url("https://connect.example/__api__"))
        permissions = Permissions(params, content_guid=content_guid)

        # (Doesn't match any permissions, but that's okay)
        user_to_remove = User(params, **fake_user)
        group_to_remove = Group(params, **fake_group)
        permission_to_remove = Permission(params, **fake_permission)

        # invoke
        destroyed_permission = permissions.destroy(
            fake_permission["principal_guid"],
            # Make sure duplicates are dropped
            fake_permission["principal_guid"],
            # Extract info from User, Group, Permission
            user_to_remove,
            group_to_remove,
            permission_to_remove,
        )

        # Assert bad input value
        with pytest.raises(TypeError):
            permissions.destroy(
                42  # pyright: ignore[reportArgumentType]
            )
        with pytest.raises(ValueError):
            permissions.destroy()

        # Assert values
        assert mock_permissions_get[0].call_count == 1
        assert mock_permissions_get[1].call_count == 0
        assert mock_permission_delete.call_count == 1
        assert len(destroyed_permission) == 1
        assert destroyed_permission[0] == fake_permission

        # Invoking again is a no-op
        destroyed_permission = permissions.destroy(fake_permission["principal_guid"])

        assert mock_permissions_get[0].call_count == 1
        assert mock_permissions_get[1].call_count == 1
        assert mock_permission_delete.call_count == 1
        assert len(destroyed_permission) == 0
