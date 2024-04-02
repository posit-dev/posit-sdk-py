import uuid

from unittest.mock import Mock

import requests
import responses

from responses import matchers

from posit.connect.config import Config
from posit.connect.permissions import Permission, Permissions


class TestPermissionGuid:
    def test_from_id(self):
        config = Mock()
        session = Mock()
        guid = str(uuid.uuid4())
        permission = Permission(config, session, guid=guid)
        assert permission.guid == guid

    def test_from_guid(self):
        config = Mock()
        session = Mock()
        guid = str(uuid.uuid4())
        permission = Permission(config, session, id=guid)
        assert permission.guid == guid


class TestPermissionUpdate:
    @responses.activate
    def test_request_shape(self):
        # test data
        guid = str(uuid.uuid4())
        content_guid = str(uuid.uuid4())
        principal_guid = str(uuid.uuid4())
        principal_type = "principal_type"
        role = "role"
        extraneous = "extraneous"

        # define api behavior
        responses.put(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{guid}",
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
        config = Config(api_key="12345", url="https://connect.example/")
        session = requests.Session()
        permission = Permission(
            config,
            session,
            guid=guid,
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
        old_role = "old_role"
        new_role = "new_role"

        # define api behavior
        guid = str(uuid.uuid4())
        content_guid = str(uuid.uuid4())
        responses.put(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/{guid}",
            json={"role": new_role},
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
        config = Config(api_key="12345", url="https://connect.example/")
        session = requests.Session()
        permission = Permission(
            config, session, guid=guid, content_guid=content_guid, role=old_role
        )

        # assert role change with respect to api response
        assert permission.role == old_role
        permission.update(role=new_role)
        assert permission.role == new_role


class TestPermissionsFind:
    @responses.activate
    def test(self):
        # test data
        content_guid = str(uuid.uuid4())
        fake_permissions = [
            {
                "guid": str(uuid.uuid4()),
                "content_guid": content_guid,
                "principal_guid": str(uuid.uuid4()),
                "principal_type": "user",
                "role": "read",
            },
            {
                "guid": str(uuid.uuid4()),
                "content_guid": content_guid,
                "principal_guid": str(uuid.uuid4()),
                "principal_type": "group",
                "role": "write",
            },
        ]

        # define api behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permissions,
        )

        # setup
        config = Config(api_key="12345", url="https://connect.example/")
        session = requests.Session()
        permissions = Permissions(config, session, content_guid=content_guid)

        # invoke
        permissions = permissions.find()

        # assert response
        assert permissions == fake_permissions


class TestPermissionsFindOne:
    @responses.activate
    def test(self):
        # test data
        content_guid = str(uuid.uuid4())
        fake_permissions = [
            {
                "guid": str(uuid.uuid4()),
                "content_guid": content_guid,
                "principal_guid": str(uuid.uuid4()),
                "principal_type": "user",
                "role": "read",
            },
            {
                "guid": str(uuid.uuid4()),
                "content_guid": content_guid,
                "principal_guid": str(uuid.uuid4()),
                "principal_type": "group",
                "role": "write",
            },
        ]

        # define api behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=fake_permissions,
        )

        # setup
        config = Config(api_key="12345", url="https://connect.example/")
        session = requests.Session()
        permissions = Permissions(config, session, content_guid=content_guid)

        # invoke
        permission = permissions.find_one()

        # assert response
        assert permission == fake_permissions[0]
