from pathlib import Path

import pytest
from packaging import version

from posit import connect

from . import CONNECT_VERSION


@pytest.mark.skipif(
    CONNECT_VERSION <= version.parse("2023.01.1"),
    reason="Quarto not available",
)
class TestJobs:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(name="example-quarto-minimal")

    @classmethod
    def teardown_class(cls):
        cls.content.delete()
        assert cls.client.content.count() == 0

    def test(self):
        content = self.content

        path = Path("../../../resources/connect/bundles/example-quarto-minimal/bundle.tar.gz")
        path = Path(__file__).parent / path
        path = path.resolve()
        path = str(path)

        bundle = content.bundles.create(path)
        bundle.deploy()

        jobs = content.jobs
        assert len(jobs) == 1

    def test_find_by(self):
        content = self.content

        path = Path("../../../resources/connect/bundles/example-quarto-minimal/bundle.tar.gz")
        path = Path(__file__).parent / path
        path = path.resolve()
        path = str(path)

        bundle = content.bundles.create(path)
        task = bundle.deploy()
        task.wait_for()

        jobs = content.jobs
        assert len(jobs) != 0

        job = jobs[0]
        key = job["key"]
        assert content.jobs.find_by(key=key) == job
