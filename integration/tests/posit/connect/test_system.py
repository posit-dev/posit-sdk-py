from pathlib import Path

import pytest
from packaging import version

from posit.connect import Client
from posit.connect.system import SystemRuntimeCache
from posit.connect.tasks import Task

from . import CONNECT_VERSION, fixtures


@pytest.mark.skipif(
    # Added to the v2023.05.0 milestone
    # https://github.com/rstudio/connect/pull/23148
    CONNECT_VERSION < version.parse("2023.05.0"),
    reason="Cache runtimes not implemented",
)
class TestSystem:
    @classmethod
    def setup_class(cls):
        cls.client = Client()
        cls.content_item = cls.client.content.create(name=fixtures.name())

    def test_runtime_caches(self):
        # Get current caches
        caches = self.client.system.caches.runtime.find()
        assert isinstance(caches, list)

        # Remove all caches
        caches = self.client.system.caches.runtime.find()
        for cache in caches:
            assert isinstance(cache, SystemRuntimeCache)
            none_val = cache.destroy(dry_run=True)
            assert none_val is None
            task = cache.destroy()
            assert isinstance(task, Task)
            task.wait_for()

        assert len(self.client.system.caches.runtime.find()) == 0

        # Deploy a new cache
        path = Path("../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = self.content_item.bundles.create(str(path))
        task = bundle.deploy()
        task.wait_for()

        # Check if the cache is deployed
        caches = self.client.system.caches.runtime.find()

        # Barret 2024/12:
        # Caches only showing up in Connect versions >= 2024.05.0
        # I do not know why.
        # Since we are not logic testing Connect, we can confirm our code works given more recent versions of Connect.
        if CONNECT_VERSION >= version.parse("2024.05.0"):
            assert len(caches) > 0

        # Remove all caches
        caches = self.client.system.caches.runtime.find()
        for cache in caches:
            assert isinstance(cache, SystemRuntimeCache)
            none_val = cache.destroy(dry_run=True)
            assert none_val is None
            task = cache.destroy()
            assert isinstance(task, Task)
            task.wait_for()

        assert len(self.client.system.caches.runtime.find()) == 0
