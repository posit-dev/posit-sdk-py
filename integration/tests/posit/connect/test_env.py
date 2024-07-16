from posit import connect


class TestEnvVars:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(
            name="Sample",
            description="Simple sample content for testing",
            access_type="acl",
        )

    @classmethod
    def teardown_class(cls):
        cls.content.delete()
        assert cls.client.content.count() == 0

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
