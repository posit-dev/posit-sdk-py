import random
import uuid

from unittest.mock import Mock

import requests
import responses

from responses import matchers

from posit.connect.config import Config
from posit.connect.context import Context
from posit.connect.permissions import Permission, Permissions

from .api import load_mock  # type: ignore


class TestPermissionDelete:
    @responses.activate
    def test(self):
        # data
        id = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_delete = responses.delete(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{id}"
        )

        # setup
        ctx = Context(
            api_key="12345",
            session=requests.Session(),
            url="https://connect.example/__api__",
        )
        fake_permission = load_mock(
            f"v1/content/{content_guid}/permissions/{id}.json"
        )
        permission = Permission(ctx, **fake_permission)

        # invoke
        permission.delete()

        # assert
        assert mock_delete.call_count == 1


class TestPermissionUpdate:
    @responses.activate
    def test_request_shape(self):
        # test data
        id = random.randint(0, 100)
        content_guid = str(uuid.uuid4())
        principal_guid = str(uuid.uuid4())
        principal_type = "principal_type"
        role = "role"
        extraneous = "extraneous"

        # define api behavior
        responses.put(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{id}",
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
                    }
                )
            ],
        )

        # setup
        ctx = Context(
            api_key="12345",
            session=requests.Session(),
            url="https://connect.example/__api__",
        )
        permission = Permission(
            ctx,
            id=id,
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

        id = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permission = load_mock(
            f"v1/content/{content_guid}/permissions/{id}.json"
        )
        fake_permission.update(role=new_role)

        # define api behavior
        id = random.randint(0, 100)
        content_guid = str(uuid.uuid4())
        responses.put(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{id}",
            json=fake_permission,
            match=[
                matchers.json_params_matcher(
                    {
                        "principal_guid": None,
                        "principal_type": None,
                        "role": new_role,
                    }
                )
            ],
        )

        # setup
        ctx = Context(
            api_key="12345",
            session=requests.Session(),
            url="https://connect.example/__api__",
        )
        permission = Permission(
            ctx, id=id, content_guid=content_guid, role=old_role
        )

        # assert role change with respect to api response
        assert permission.role == old_role
        permission.update(role=new_role)
        assert permission.role == new_role


class TestPermissionsCount:
    @responses.activate
    def test(self):
        # test data
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permissions = load_mock(
            f"v1/content/{content_guid}/permissions.json"
        )

        # define api behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permissions,
        )

        # setup
        ctx = Context(
            api_key="12345",
            session=requests.Session(),
            url="https://connect.example/__api__",
        )
        permissions = Permissions(ctx, content_guid=content_guid)

        # invoke
        count = permissions.count()

        # assert response
        assert count == len(fake_permissions)


class TestPermissionsCreate:
    @responses.activate
    def test(self):
        # data
        id = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        principal_guid = str(uuid.uuid4())
        principal_type = "user"
        role = "owner"
        fake_permission = {
            **load_mock(f"v1/content/{content_guid}/permissions/{id}.json"),
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
                    }
                )
            ],
        )

        # setup
        ctx = Context(
            api_key="12345",
            session=requests.Session(),
            url="https://connect.example/__api__",
        )
        permissions = Permissions(ctx, content_guid=content_guid)

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
        fake_permissions = load_mock(
            f"v1/content/{content_guid}/permissions.json"
        )

        # define api behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permissions,
        )

        # setup
        ctx = Context(
            api_key="12345",
            session=requests.Session(),
            url="https://connect.example/__api__",
        )
        permissions = Permissions(ctx, content_guid=content_guid)

        # invoke
        permissions = permissions.find()

        # assert response
        assert permissions == fake_permissions


class TestPermissionsFindOne:
    @responses.activate
    def test(self):
        # test data
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permissions = load_mock(
            f"v1/content/{content_guid}/permissions.json"
        )

        # define api behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permissions,
        )

        # setup
        ctx = Context(
            api_key="12345",
            session=requests.Session(),
            url="https://connect.example/__api__",
        )
        permissions = Permissions(ctx, content_guid=content_guid)

        # invoke
        permission = permissions.find_one()

        # assert response
        assert permission == fake_permissions[0]


class TestPermissionsGet:
    @responses.activate
    def test(self):
        # data
        id = "94"
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_permission = load_mock(
            f"v1/content/{content_guid}/permissions/{id}.json"
        )

        # behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{id}",
            json=fake_permission,
        )

        # setup
        ctx = Context(
            api_key="12345",
            session=requests.Session(),
            url="https://connect.example/__api__",
        )
        permissions = Permissions(ctx, content_guid=content_guid)

        # invoke
        permission = permissions.get(id)

        # assert
        assert permission == fake_permission
