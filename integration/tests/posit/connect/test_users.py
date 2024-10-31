from posit import connect


class TestUser:
    @classmethod
    def setup_class(cls):
        cls.client = client = connect.Client()
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
        # aron, bill, cole, and me
        assert self.client.users.count() == 4

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
