from __future__ import annotations

import pytest
from typing_extensions import TYPE_CHECKING

from posit import connect

if TYPE_CHECKING:
    from posit.connect.content import ContentItem
    from posit.connect.permissions import Permission


class TestContentPermissions:
    content: ContentItem

    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(name="example")

        cls.user_aron = cls.client.users.create(
            username="permission_aron",
            email="permission_aron@example.com",
            password="permission_s3cur3p@ssword",
        )
        cls.user_bill = cls.client.users.create(
            username="permission_bill",
            email="permission_bill@example.com",
            password="permission_s3cur3p@ssword",
        )

        cls.group_friends = cls.client.groups.create(name="Friends")

    @classmethod
    def teardown_class(cls):
        cls.content.delete()
        assert cls.client.content.count() == 0

        cls.group_friends.delete()
        assert cls.client.groups.count() == 0

    def test_permissions_add_destroy(self):
        assert self.client.groups.count() == 1
        assert self.client.users.count() == 3
        assert self.content.permissions.find() == []

        # Add permissions
        self.content.permissions.create(
            principal_guid=self.user_aron["guid"],
            principal_type="user",
            role="viewer",
        )
        self.content.permissions.create(
            principal_guid=self.group_friends["guid"],
            principal_type="group",
            role="owner",
        )

        def assert_permissions_match_guids(permissions: list[Permission], objs_with_guid):
            for permission, obj_with_guid in zip(permissions, objs_with_guid):
                assert permission["principal_guid"] == obj_with_guid["guid"]

        # Prove they have been added
        assert_permissions_match_guids(
            self.content.permissions.find(),
            [self.user_aron, self.group_friends],
        )

        # Remove permissions (and from some that isn't an owner)
        self.content.permissions.destroy(self.user_aron)
        with pytest.raises(ValueError):
            self.content.permissions.destroy(self.user_bill)

        # Prove they have been removed
        assert_permissions_match_guids(
            self.content.permissions.find(),
            [self.group_friends],
        )

        # Remove the last permission
        self.content.permissions.destroy(self.group_friends)

        # Prove they have been removed
        assert self.content.permissions.find() == []
