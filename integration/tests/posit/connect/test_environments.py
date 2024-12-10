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

    @classmethod
    def teardown_class(cls):
        pass

    def test(self):
        environment = self.client.environments.create(
            title="original-title", name="test", cluster_name="Kubernetes"
        )

        assert environment["title"] == "original-title"

        assert len(self.client.environments.reload()) == 1

        environment.update(title="new-title")
        assert environment["title"] == "new-title"

        environment = self.client.environments.find_by(title="new-title")
        assert environment
        assert environment["title"] == "new-title"

        environment.destroy()
        environment = self.client.environments.find_by(title="new-title")
        assert environment is None

        assert len(self.client.environments.reload()) == 0
