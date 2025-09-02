from pathlib import Path

import pytest
from packaging import version

from posit.connect import Client

from . import CONNECT_VERSION


# @pytest.mark.skipif(
#     CONNECT_VERSION < version.parse("2024.05.0"),
#     reason="Cache runtimes not implemented",
# )
class TestSystem:
    @classmethod
    def setup_class(cls):
        cls.client = Client()
        cls.content = cls.client.content.create(name=cls.__name__)
        path = Path("../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = cls.content.bundles.create(str(path))
        task = bundle.deploy()
        task.wait_for()

    @classmethod
    def teardown_class(cls):
        cls.content.delete()

    def test_runtime_caches(self):
        caches = self.client.system.caches.runtime.find()
        assert len(caches) > 0
