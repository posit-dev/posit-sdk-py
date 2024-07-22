from pathlib import Path

from posit import connect


class TestContent:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(name="example")

    @classmethod
    def teardown_class(cls):
        cls.content.delete()
        assert cls.client.content.count() == 0

    def test_count(self):
        assert self.client.content.count() == 1

    def test_get(self):
        assert self.client.content.get(self.content.guid) == self.content

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

    def test_restart(self):
        # create content
        content = self.client.content.create(name="example-flask-minimal")
        # create bundle
        path = Path(
            "../../../resources/bundles/example-flask-minimal/bundle.tar.gz"
        )
        path = (Path(__file__).parent / path).resolve()
        bundle = content.bundles.create(str(path))
        # deploy bundle
        task = bundle.deploy()
        task.wait_for()
        # restart content
        content.restart()
        # delete content
        content.delete()

    def test_refresh(self):
        # create content
        content = self.client.content.create(name="example-quarto-minimal")
        # create bundle
        path = Path(
            "../../../resources/bundles/example-quarto-minimal/bundle.tar.gz"
        )
        path = (Path(__file__).parent / path).resolve()
        bundle = content.bundles.create(str(path))
        # deploy bundle
        task = bundle.deploy()
        task.wait_for()
        # restart content
        task = content.restart()
        task.wait_for()
        # delete content
        content.delete()
