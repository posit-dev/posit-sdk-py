from posit import connect


class TestTags:
    def setup_class(cls):
        cls.client = connect.Client()
        cls.tag = cls.client.tags.create(name="example")

    def teardown_class(cls):
        cls.tag.delete()

    def test_get(self):
        assert self.client.tags.get(self.tag.id)

    def test_find(self):
        assert self.client.tags.find() == [self.tag]

    def test_find_one(self):
        assert self.client.tags.find_one() == self.tag

    def test_update(self):
        self.tag.update(name="updated")
        assert self.tag["name"] == "updated"
        self.tag.update(name="example")
