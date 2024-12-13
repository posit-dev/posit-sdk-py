from pathlib import Path

import pytest
from packaging import version

from posit.connect import Client
from posit.connect.system import SystemRuntimeCache
from posit.connect.tasks import Task

from . import CONNECT_VERSION


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
        assert cls.client.content.count() == 0
        cls.content_item = cls.client.content.create(name="Content_A")

    # Copied from from integration/tests/posit/connect/test_packages.py
    def _deploy_python_bundle(self):
        path = Path("../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = self.content_item.bundles.create(str(path))
        task = bundle.deploy()
        task.wait_for()

    def _remove_all_caches(self):
        caches: list[SystemRuntimeCache] = self.client.system.caches.runtime.find()
        for cache in caches:
            assert isinstance(cache, SystemRuntimeCache)
            none_val = cache.destroy(dry_run=True)
            assert none_val is None
            task: Task = cache.destroy()
            assert isinstance(task, Task)
            task.wait_for()
        assert len(self.client.system.caches.runtime.find()) == 0

    @classmethod
    def teardown_class(cls):
        cls.content_item.delete()
        assert cls.client.content.count() == 0

    def test_runtime_caches(self):
        # Get current caches
        caches: list[SystemRuntimeCache] = self.client.system.caches.runtime.find()
        assert isinstance(caches, list)

        # Remove all caches
        self._remove_all_caches()

        # Deploy a new cache
        self._deploy_python_bundle()

        # Check if the cache is deployed
        caches = self.client.system.caches.runtime.find()

        # Barret 2024/12:
        # Caches only showing up in Connect versions >= 2024.05.0
        # I do not know why.
        # Since we are not logic testing Connect, we can confirm our code works given more recent versions of Connect.
        if CONNECT_VERSION >= version.parse("2024.05.0"):
            assert len(caches) > 0

        # Remove all caches
        self._remove_all_caches()
