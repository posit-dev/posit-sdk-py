import pytest
from packaging import version

from posit import connect

from . import CONNECT_VERSION


@pytest.mark.skipif(
    CONNECT_VERSION < version.parse("2023.05.0"),
    reason="Environments API unavailable",
)
class TestEnvironments:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.environment = cls.client.environments.create(
            title="title",
            name="name",
            cluster_name="Kubernetes",
        )

    @classmethod
    def teardown_class(cls):
        cls.environment.destroy()
        assert len(cls.client.environments) == 0

    def test_find(self):
        uid = self.environment["guid"]
        environment = self.client.environments.find(uid)
        assert environment == self.environment

    def test_find_by(self):
        environment = self.client.environments.find_by(name="name")
        assert environment == self.environment

    def test_update(self):
        assert self.environment["title"] == "title"
        self.environment.update(title="new-title")
        assert self.environment["title"] == "new-title"
