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
        groups = self.client.groups.find()
        assert len(groups) == 1
        for key, value in self.group.items():
            assert groups[0][key] == value

    def test_find_one(self):
        group = self.client.groups.find_one()
        assert group is not None
        for key, value in self.group.items():
            assert group[key] == value
