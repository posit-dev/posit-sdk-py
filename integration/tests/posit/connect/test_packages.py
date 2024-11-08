from pathlib import Path

import pytest
from packaging import version

from posit import connect

from . import CONNECT_VERSION


@pytest.mark.skipif(
    CONNECT_VERSION < version.parse("2024.10.0-dev"),
    reason="Packages API unavailable",
)
class TestPackages:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(name=cls.__name__)
        path = Path("../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = cls.content.bundles.create(str(path))
        task = bundle.deploy()
        task.wait_for()

    @classmethod
    def teardown_class(cls):
        cls.content.delete()

    def test(self):
        assert self.client.packages
        assert self.content.packages

    def test_find_by(self):
        package = self.client.packages.find_by(name="flask")
        assert package
        assert package["name"] == "flask"

        package = self.content.packages.find_by(name="flask")
        assert package
        assert package["name"] == "flask"
