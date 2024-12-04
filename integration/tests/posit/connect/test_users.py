from posit import connect


class TestUser:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()

        # Play nicely with other tests
        cls.existing_user_count = client.users.count()

        cls.aron = client.users.create(
            username="aron",
            email="aron@example.com",
            password="s3cur3p@ssword",
        )
        cls.bill = client.users.create(
            username="bill",
            email="bill@example.com",
            password="s3cur3p@ssword",
        )
        cls.cole = client.users.create(
            username="cole",
            email="cole@example.com",
            password="s3cur3p@ssword",
        )

    def test_lock(self):
        for user in (self.aron, self.bill, self.cole):
            user.lock()
            assert len(self.client.users.find(account_status="locked")) == 1
            user.unlock()
        assert len(self.client.users.find(account_status="locked")) == 0

    def test_count(self):
        # aron, bill, cole, and me (and existing user)
        assert self.client.users.count() == 3 + self.existing_user_count

    def test_find(self):
        assert self.client.users.find(prefix="aron") == [self.aron]
        assert self.client.users.find(prefix="bill") == [self.bill]
        assert self.client.users.find(prefix="cole") == [self.cole]

    def test_find_one(self):
        assert self.client.users.find_one(prefix="aron") == self.aron
        assert self.client.users.find_one(prefix="bill") == self.bill
        assert self.client.users.find_one(prefix="cole") == self.cole

    def test_get(self):
        assert self.client.users.get(self.aron["guid"]) == self.aron
        assert self.client.users.get(self.bill["guid"]) == self.bill
        assert self.client.users.get(self.cole["guid"]) == self.cole

    # Also tests Groups.members
    def test_user_group_interactions(self):
        try:
            test_group = self.client.groups.create(name="UnitFriends")

            # `Group.members.count()`
            assert test_group.members.count() == 0

            # `Group.members.add()`
            test_group.members.add(self.bill)
            # `User.groups.add()`
            assert test_group.members.count() == 1
            self.cole.groups.add(test_group)
            assert test_group.members.count() == 2

            # `Group.members.find()`
            group_users = test_group.members.find()
            assert len(group_users) == 2
            assert group_users[0]["guid"] == self.bill["guid"]
            assert group_users[1]["guid"] == self.cole["guid"]

            # `User.group.find()`
            bill_groups = self.bill.groups.find()
            assert len(bill_groups) == 1
            assert bill_groups[0]["guid"] == test_group["guid"]

            # `Group.members.delete()`
            test_group.members.delete(self.bill)
            assert test_group.members.count() == 1

            # `User.groups.delete()`
            self.cole.groups.delete(test_group)
            assert test_group.members.count() == 0

        finally:
            groups = self.client.groups.find(prefix="UnitFriends")
            if len(groups) > 0:
                test_group = groups[0]
                test_group.delete()

            assert len(self.client.groups.find(prefix="UnitFriends")) == 0


class TestUserContent:
    """Checks behavior of the content attribute."""

    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
        cls.me = me = client.me
        cls.content = me.content.create(
            name="Sample",
            description="Simple sample content for testing",
            access_type="acl",
        )

    @classmethod
    def teardown_class(cls):
        assert cls.content.delete() is None
        assert cls.me.content.count() == 0

    def test_count(self):
        assert self.me.content.count() == 1

    def test_find(self):
        assert self.me.content.find()

    def test_find_one(self):
        assert self.me.content.find_one()

    def test_multiple_users(self):
        user = self.client.users.create(
            username="example",
            email="example@example.com",
            password="s3cur3p@ssword",
        )
        # assert filtering limits to the provided user.
        assert self.me.content.find_one() == self.content
        assert user.content.find_one() is None
        user.lock()
