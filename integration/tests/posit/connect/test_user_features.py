from posit import connect
from posit.connect.content import ContentItem
from posit.connect.permissions import Permission


class TestUserExactUsername:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
        cls.user_a = client.users.create(
            username="exact_kaia",
            email="exact_kaia@example.com",
            password="s3cur3p@ssword",
        )
        cls.user_b = client.users.create(
            username="exact_kaia_test",
            email="exact_kaia_test@example.com",
            password="s3cur3p@ssword",
        )

    @classmethod
    def teardown_class(cls):
        cls.user_a.lock()
        cls.user_b.lock()

    def test_find_username_exact(self):
        users = self.client.users.find(username="exact_kaia")
        assert len(users) == 1
        assert users[0]["username"] == "exact_kaia"

    def test_find_one_username_exact(self):
        user = self.client.users.find_one(username="exact_kaia")
        assert user is not None
        assert user["username"] == "exact_kaia"

    def test_find_username_no_match(self):
        users = self.client.users.find(username="exact_kaia_nonexistent")
        assert len(users) == 0

    def test_find_one_username_no_match(self):
        user = self.client.users.find_one(username="exact_kaia_nonexistent")
        assert user is None

    def test_prefix_still_returns_both(self):
        users = self.client.users.find(prefix="exact_kaia")
        usernames = {u["username"] for u in users}
        assert "exact_kaia" in usernames
        assert "exact_kaia_test" in usernames


class TestUsersGetBatch:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
        cls.user_a = client.users.create(
            username="batch_alice",
            email="batch_alice@example.com",
            password="s3cur3p@ssword",
        )
        cls.user_b = client.users.create(
            username="batch_bob",
            email="batch_bob@example.com",
            password="s3cur3p@ssword",
        )

    @classmethod
    def teardown_class(cls):
        cls.user_a.lock()
        cls.user_b.lock()

    def test_get_batch(self):
        guids = [self.user_a["guid"], self.user_b["guid"]]
        users = self.client.users.get_batch(guids)
        assert len(users) == 2
        assert users[0]["guid"] == self.user_a["guid"]
        assert users[1]["guid"] == self.user_b["guid"]

    def test_get_batch_empty(self):
        users = self.client.users.get_batch([])
        assert users == []


class TestUserPermissions:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
        cls.user = client.users.create(
            username="uperm_user",
            email="uperm_user@example.com",
            password="s3cur3p@ssword",
        )

        cls.content_a = client.content.create(
            name="uperm-content-a",
            access_type="acl",
        )
        cls.content_b = client.content.create(
            name="uperm-content-b",
            access_type="acl",
        )

        # Grant user permissions on both content items
        cls.content_a.permissions.create(cls.user, role="viewer")
        cls.content_b.permissions.create(cls.user, role="owner")

    @classmethod
    def teardown_class(cls):
        cls.content_a.delete()
        cls.content_b.delete()
        cls.user.lock()

    def test_find_permissions(self):
        perms = self.user.permissions.find()
        assert len(perms) >= 2
        assert all(isinstance(p, Permission) for p in perms)

        # Verify our specific permissions are in the results
        content_guids = {p["content_guid"] for p in perms}
        assert self.content_a["guid"] in content_guids
        assert self.content_b["guid"] in content_guids

    def test_find_permissions_roles(self):
        perms = self.user.permissions.find()
        perm_map = {p["content_guid"]: p["role"] for p in perms}
        assert perm_map[self.content_a["guid"]] == "viewer"
        assert perm_map[self.content_b["guid"]] == "owner"


class TestPermissionContentBackRef:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
        cls.user = client.users.create(
            username="backref_user",
            email="backref_user@example.com",
            password="s3cur3p@ssword",
        )
        cls.content = client.content.create(
            name="backref-content",
            access_type="acl",
        )
        cls.content.permissions.create(cls.user, role="viewer")

    @classmethod
    def teardown_class(cls):
        cls.content.delete()
        cls.user.lock()

    def test_permission_content_property(self):
        perms = self.content.permissions.find()
        assert len(perms) >= 1

        perm = perms[0]
        content_item = perm.content
        assert isinstance(content_item, ContentItem)
        assert content_item["guid"] == self.content["guid"]
        assert content_item["name"] == "backref-content"
