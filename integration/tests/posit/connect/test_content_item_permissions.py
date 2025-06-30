from __future__ import annotations

import pytest
from typing_extensions import TYPE_CHECKING

from posit import connect

from .fixtures import email, name, password, username

if TYPE_CHECKING:
    from posit.connect.content import ContentItem
    from posit.connect.permissions import Permission


class TestContentPermissions:
    content: ContentItem

    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(name=name())

        cls.alice = cls.client.users.create(
            username=name(),
            email=email(),
            password=password(),
        )

        cls.bob = cls.client.users.create(
            username=username(),
            email=email(),
            password=password(),
        )

        cls.group = cls.client.groups.create(name=name())

    def test_permissions_add_destroy(self):
        assert self.content.permissions.find() == []

        # Add permissions
        self.content.permissions.create(
            principal_guid=self.alice["guid"],
            principal_type="user",
            role="viewer",
        )
        self.content.permissions.create(
            principal_guid=self.group["guid"],
            principal_type="group",
            role="owner",
        )

        def assert_permissions_match_guids(permissions: list[Permission], objs_with_guid):
            for permission, obj_with_guid in zip(permissions, objs_with_guid):
                assert permission["principal_guid"] == obj_with_guid["guid"]

        # Prove they have been added
        assert_permissions_match_guids(
            self.content.permissions.find(),
            [self.alice, self.group],
        )

        # Remove permissions (and from some that isn't an owner)
        self.content.permissions.destroy(self.alice)
        with pytest.raises(ValueError):
            self.content.permissions.destroy(self.bob)

        # Prove they have been removed
        assert_permissions_match_guids(
            self.content.permissions.find(),
            [self.group],
        )

        # Remove the last permission
        self.content.permissions.destroy(self.group)

        # Prove they have been removed
        assert self.content.permissions.find() == []
