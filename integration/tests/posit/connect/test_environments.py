import pytest
from packaging import version

from posit import connect

from . import CONNECT_VERSION


@pytest.mark.skipif(
    CONNECT_VERSION <= version.parse("2023.01.1"),
    reason="Environments API not available",
)
class TestContent:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.environment = cls.client.environments.create(
            title="Title", cluster_name="Kubernetes", name="Name"
        )

    @classmethod
    def teardown_class(cls):
        cls.environment.destroy()

    def test_find(self):
        uid = self.environment["guid"]
        environment = self.client.environments.find(uid)
        assert environment == self.environment

    def test_find_by(self):
        environment = self.client.environments.find_by(name="Name")
        assert environment == self.environment

    def test_update(self):
        self.environment.update(title="New Title")
        assert self.environment["title"] == "New Title"
