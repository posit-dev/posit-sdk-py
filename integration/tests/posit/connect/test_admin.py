from posit import connect
from posit.connect.admin import MergeResult, merge_users
from posit.connect.permissions import Permission, PermissionRole


class TestMergeUsers:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()

        cls.source = client.users.create(
            username="merge_source",
            email="merge_source@example.com",
            password="s3cur3p@ssword",
        )
        cls.target = client.users.create(
            username="merge_target",
            email="merge_target@example.com",
            password="s3cur3p@ssword",
        )

        # Create content owned by admin (me) and grant source a permission
        cls.content_shared = client.content.create(
            name="merge-shared",
            access_type="acl",
        )
        cls.content_shared.permissions.create(
            cls.source, role="viewer",
        )

    @classmethod
    def teardown_class(cls):
        cls.content_shared.delete()

        # Unlock source if locked
        try:
            cls.source.unlock()
        except Exception:
            pass

    def test_dry_run(self):
        result = merge_users(
            self.client,
            source=self.source,
            target=self.target,
            dry_run=True,
        )

        assert isinstance(result, MergeResult)
        # Source has viewer permission on shared content
        assert len(result.permissions_added) == 1
        assert result.permissions_added[0]["role"] == "viewer"
        assert result.source_locked is True

        # Verify nothing actually changed
        assert not self.source["locked"]
        source_perms = self.content_shared.permissions.find(
            principal_guid=self.source["guid"],
        )
        assert len(source_perms) == 1
        target_perms = self.content_shared.permissions.find(
            principal_guid=self.target["guid"],
        )
        assert len(target_perms) == 0

    def test_merge(self):
        result = merge_users(
            self.client,
            source=self.source,
            target=self.target,
        )

        assert isinstance(result, MergeResult)
        assert len(result.errors) == 0
        assert result.source_locked is True

        # Source permission should be removed
        source_perms = self.content_shared.permissions.find(
            principal_guid=self.source["guid"],
        )
        assert len(source_perms) == 0

        # Target should have the permission
        target_perms = self.content_shared.permissions.find(
            principal_guid=self.target["guid"],
        )
        assert len(target_perms) == 1
        assert target_perms[0]["role"] == "viewer"


class TestMergeUsersOwnership:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
        cls.me = client.me

        cls.source = client.users.create(
            username="merge_own_source",
            email="merge_own_source@example.com",
            password="s3cur3p@ssword",
        )
        cls.target = client.users.create(
            username="merge_own_target",
            email="merge_own_target@example.com",
            password="s3cur3p@ssword",
        )

        # Create content owned by source (via admin transferring ownership)
        cls.content_owned = client.content.create(
            name="merge-owned",
            access_type="acl",
        )
        cls.content_owned.update(owner_guid=cls.source["guid"])

    @classmethod
    def teardown_class(cls):
        # Take back ownership so we can delete
        try:
            cls.content_owned.update(owner_guid=cls.me["guid"])
        except Exception:
            pass
        cls.content_owned.delete()

        try:
            cls.source.unlock()
        except Exception:
            pass

    def test_transfers_ownership(self):
        result = merge_users(
            self.client,
            source=self.source,
            target=self.target,
        )

        assert len(result.errors) == 0
        assert self.content_owned["guid"] in result.ownership_transferred
        assert result.source_locked is True

        # Verify ownership transferred
        refreshed = self.client.content.get(self.content_owned["guid"])
        assert refreshed["owner_guid"] == self.target["guid"]


class TestMergeUsersRoleUpgrade:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()

        cls.source = client.users.create(
            username="merge_upg_source",
            email="merge_upg_source@example.com",
            password="s3cur3p@ssword",
        )
        cls.target = client.users.create(
            username="merge_upg_target",
            email="merge_upg_target@example.com",
            password="s3cur3p@ssword",
        )

        # Create content and give both users permissions (source=owner, target=viewer)
        cls.content = client.content.create(
            name="merge-upgrade",
            access_type="acl",
        )
        cls.content.permissions.create(cls.source, role="owner")
        cls.content.permissions.create(cls.target, role="viewer")

    @classmethod
    def teardown_class(cls):
        cls.content.delete()

        try:
            cls.source.unlock()
        except Exception:
            pass

    def test_upgrades_role(self):
        result = merge_users(
            self.client,
            source=self.source,
            target=self.target,
        )

        assert len(result.errors) == 0
        assert len(result.permissions_upgraded) == 1
        assert result.permissions_upgraded[0]["old_role"] == "viewer"
        assert result.permissions_upgraded[0]["new_role"] == "owner"

        # Verify target now has owner role
        target_perms = self.content.permissions.find(
            principal_guid=self.target["guid"],
        )
        assert len(target_perms) == 1
        assert target_perms[0]["role"] == "owner"

        # Verify source permission removed
        source_perms = self.content.permissions.find(
            principal_guid=self.source["guid"],
        )
        assert len(source_perms) == 0
