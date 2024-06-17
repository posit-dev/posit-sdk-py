from posit import connect


class TestAttributeContent:
    """Checks behavior of the content attribute."""

    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.user = cls.client.me
        cls.user.content.create(
            name="Sample",
            description="Simple sample content for testing",
            access_type="acl",
        )

    @classmethod
    def teardown_class(cls):
        assert cls.user.content.find_one().delete() is None
        assert cls.user.content.count() == 0

    def test_count(self):
        assert self.user.content.count() == 1

    def test_find(self):
        assert self.user.content.find()

    def test_find_one(self):
        assert self.user.content.find_one()
