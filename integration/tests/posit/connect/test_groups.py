from posit import connect

from . import fixtures


class TestGroups:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.item = cls.client.groups.create(name=fixtures.name())

    def test_count(self):
        # Assert that count works. We don't care what the count is.
        assert self.client.groups.count()

    def test_get(self):
        assert self.client.groups.get(self.item["guid"])

    def test_find(self):
        groups = self.client.groups.find()
        group_guids = {group["guid"] for group in groups}
        assert self.item["guid"] in group_guids

    def test_find_one(self):
        found_group = self.client.groups.find_one()
        assert found_group is not None
