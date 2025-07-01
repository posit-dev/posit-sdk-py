from posit import connect


class TestGroups:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.group = cls.client.groups.create(name="Friends")

    @classmethod
    def teardown_class(cls):
        cls.group.delete()
        assert cls.client.groups.count() == 0

    def test_count(self):
        assert self.client.groups.count() == 1

    def test_get(self):
        assert self.client.groups.get(self.group["guid"])

    def test_find(self):
        assert self.client.groups.find() == [self.group]

    def test_find_one(self):
        assert self.client.groups.find_one() == self.group
