from posit import connect


class TestContent:
    def setup_class(cls):
        cls.client = connect.Client()
        cls.item = cls.client.content.create(
            name="Sample",
            description="Simple sample content for testing",
            access_type="acl",
        )

    def test_count(self):
        assert self.client.content.count() == 1

    def test_get(self):
        assert self.client.content.get(self.item.guid) == self.item

    def test_find(self):
        assert self.client.content.find()

    def test_find_one(self):
        assert self.client.content.find_one()

    def test_content_item_owner(self):
        item = self.client.content.find_one(include=None)
        owner = item.owner
        assert owner.guid == self.client.me.guid

    def test_content_item_owner_from_include(self):
        item = self.client.content.find_one(include="owner")
        owner = item.owner
        assert owner.guid == self.client.me.guid
