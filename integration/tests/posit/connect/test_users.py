from posit import connect

from . import fixtures


class TestUser:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
        cls.alice = client.users.create(
            username=fixtures.username(),
            email=fixtures.email(),
            password=fixtures.password(),
        )
        cls.bob = client.users.create(
            username=fixtures.username(),
            email=fixtures.email(),
            password=fixtures.password(),
        )
        cls.carol = client.users.create(
            username=fixtures.username(),
            email=fixtures.email(),
            password=fixtures.password(),
        )

    def test_lock(self):
        for user in (self.alice, self.bob, self.carol):
            user.lock()
            assert len(self.client.users.find(account_status="locked")) == 1
            user.unlock()

        assert len(self.client.users.find(account_status="locked")) == 0

    def test_count(self):
        # Assert that count works. We don't care what the count is.
        assert self.client.users.count()

    def test_find(self):
        assert self.client.users.find(prefix=self.alice["username"]) == [self.alice]
        assert self.client.users.find(prefix=self.bob["username"]) == [self.bob]
        assert self.client.users.find(prefix=self.carol["username"]) == [self.carol]

    def test_find_one(self):
        assert self.client.users.find_one(prefix=self.alice["username"]) == self.alice
        assert self.client.users.find_one(prefix=self.bob["username"]) == self.bob
        assert self.client.users.find_one(prefix=self.carol["username"]) == self.carol

    def test_get(self):
        assert self.client.users.get(self.alice["guid"]) == self.alice
        assert self.client.users.get(self.bob["guid"]) == self.bob
        assert self.client.users.get(self.carol["guid"]) == self.carol

    def test_members(self):
        group = self.client.groups.create(name=fixtures.name())

        # Add members to the group
        group.members.add(self.bob)

        # Assign group to member
        self.carol.groups.add(group)

        # Assert group members
        members = group.members.find()
        assert len(members) == 2
        assert members[0]["guid"] == self.bob["guid"]
        assert members[1]["guid"] == self.carol["guid"]

        # Assert group members through user
        assert self.bob.groups.find()[0]["guid"] == group["guid"]

        # Remove member from group
        group.members.delete(self.bob)
        assert group.members.count() == 1


class TestUserContent:
    """Checks behavior of the content attribute."""

    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
        cls.me = client.me
        cls.content = client.me.content.create(
            name=fixtures.name(),
            description="Simple sample content for testing",
            access_type="acl",
        )

    def test_count(self):
        # Assert that count works. We don't care what the count is.
        assert self.me.content.count() >= 1

    def test_find(self):
        assert self.me.content.find()

    def test_find_one(self):
        assert self.me.content.find_one()

    def test_multiple_users(self):
        user = self.client.users.create(
            username=fixtures.username(),
            email=fixtures.email(),
            password=fixtures.password(),
        )

        assert user.content.find_one() is None
