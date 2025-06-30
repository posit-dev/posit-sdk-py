from posit import connect

from . import fixtures


class TestEnvVars:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(
            name=fixtures.name(),
            description="Simple sample content for testing",
            access_type="acl",
        )

    def test_clear(self):
        self.content.environment_variables.create("KEY", "value")
        assert self.content.environment_variables.find() == ["KEY"]
        self.content.environment_variables.clear()
        assert self.content.environment_variables.find() == []

    def test_create(self):
        self.content.environment_variables.create("KEY", "value")
        assert self.content.environment_variables.find() == ["KEY"]

    def test_delete(self):
        self.content.environment_variables.create("KEY", "value")
        assert self.content.environment_variables.find() == ["KEY"]
        self.content.environment_variables.delete("KEY")
        assert self.content.environment_variables.find() == []

    def test_find(self):
        self.content.environment_variables.create("KEY", "value")
        assert self.content.environment_variables.find() == ["KEY"]

    def test_update(self):
        self.content.environment_variables.update(KEY="value")
        assert self.content.environment_variables.find() == ["KEY"]
