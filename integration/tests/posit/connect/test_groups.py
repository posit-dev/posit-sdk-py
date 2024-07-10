import pytest

from posit import connect


class TestGroups:
    def setup_class(cls):
        cls.client = connect.Client()
        cls.item = cls.client.groups.create(name="Friends")

    def teardown_class(cls):
        cls.item.delete()
        assert cls.client.groups.count() == 0

    def test_count(self):
        assert self.client.groups.count() == 1
        assert self.client.groups.count(prefix="f") == 1
        assert self.client.groups.count(prefix="miss") == 0

    def test_get(self):
        assert self.client.groups.get(self.item.guid)

    def test_find(self):
        assert self.client.groups.find() == [self.item]
        assert self.client.groups.find(prefix="f") == [self.item]
        assert self.client.groups.find(prefix="miss") == []

    def test_find_one(self):
        assert self.client.groups.find_one() == self.item
        assert self.client.groups.find_one(prefix="f") == self.item
        assert self.client.groups.find_one(prefix="miss") is None

    def test_remote(self):
        with pytest.raises(connect.errors.ClientError):
            self.client.groups.find(remote=True)
