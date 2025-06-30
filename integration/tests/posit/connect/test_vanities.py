import uuid

from posit import connect


class TestVanities:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()

    def test_all(self):
        unique_name = f"example-{uuid.uuid4().hex[:8]}"
        content = self.client.content.create(name=unique_name)

        # None by default
        vanities = self.client.vanities.all()
        assert len(vanities) == 0

        # Set
        content.vanity = "example"

        # Get
        vanities = self.client.vanities.all()
        assert len(vanities) == 1

        # Cleanup
        content.delete()

        vanities = self.client.vanities.all()
        assert len(vanities) == 0

    def test_property(self):
        unique_name = f"example-{uuid.uuid4().hex[:8]}"
        content = self.client.content.create(name=unique_name)

        # None by default
        assert content.vanity is None

        # Set
        content.vanity = "example"

        # Get
        vanity = content.vanity
        assert vanity == "/example/"

        # Delete
        del content.vanity
        assert content.vanity is None

        # Cleanup
        content.delete()

    def test_destroy(self):
        unique_name = f"example-{uuid.uuid4().hex[:8]}"
        content = self.client.content.create(name=unique_name)

        # None by default
        assert content.vanity is None

        # Set
        content.vanity = "example"

        # Get
        vanity = content.find_vanity()
        assert vanity
        assert vanity["path"] == "/example/"

        # Delete
        vanity.destroy()
        content.reset_vanity()
        assert content.vanity is None

        # Cleanup
        content.delete()
