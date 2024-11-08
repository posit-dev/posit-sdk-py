from posit import connect


class TestGroups:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.item = cls.client.groups.create(name="Friends")

    @classmethod
    def teardown_class(cls):
        cls.item.delete()
        assert cls.client.groups.count() == 0

    def test_count(self):
        assert self.client.groups.count() == 1

    def test_get(self):
        assert self.client.groups.get(self.item["guid"])

    def test_find(self):
        assert self.client.groups.find() == [self.item]

    def test_find_one(self):
        assert self.client.groups.find_one() == self.item
