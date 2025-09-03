from pathlib import Path

import pytest
from packaging import version

from posit.connect import Client
from posit.connect.system import SystemRuntimeCache
from posit.connect.tasks import Task

from . import CONNECT_VERSION


@pytest.mark.skipif(
    CONNECT_VERSION < version.parse("2024.05.0"),
    reason="Cache runtimes not implemented",
)
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
        runtimes = self.client.system.caches.runtime.find()
        assert len(runtimes) > 0

    def test_runtime_cache_destroy(self):
        # Find existing runtime caches
        runtimes: list[SystemRuntimeCache] = self.client.system.caches.runtime.find()
        assert len(runtimes) > 0

        # Get the first cache for testing
        cache = runtimes[0]
        assert isinstance(cache, SystemRuntimeCache)

        # Test dry run destroy (should return None and not actually destroy)
        result = cache.destroy(dry_run=True)
        assert result is None

        # Verify cache still exists after dry run
        runtimes_after_dry_run = self.client.system.caches.runtime.find()
        assert len(runtimes_after_dry_run) == len(runtimes)

        # Test actual destroy
        task: Task = cache.destroy()
        assert isinstance(task, Task)
        task.wait_for()

        # Verify cache was removed
        runtimes_after_destroy = self.client.system.caches.runtime.find()
        assert len(runtimes_after_destroy) == len(runtimes) - 1
