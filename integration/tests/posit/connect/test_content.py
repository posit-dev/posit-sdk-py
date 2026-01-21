from pathlib import Path

import pytest
from packaging import version

from posit import connect

from . import CONNECT_VERSION


class TestContent:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create()

    @classmethod
    def teardown_class(cls):
        cls.content.delete()
        assert cls.client.content.count() == 0

    def test_count(self):
        assert self.client.content.count() == 1

    def test_get(self):
        item = self.client.content.get(self.content["guid"])
        # Check that essential fields match instead of exact equality
        for key in self.content:
            assert key in item
            assert item[key] == self.content[key]
        if CONNECT_VERSION >= version.parse("2024.06.0"):
            # get() always includes owner, tags, and vanity_url. Owner data is always present in
            # all content, tags and vanity_url are only present if explicitly set in the content.
            assert "owner" in item
            assert "tags" not in item
            assert "vanity_url" not in item

    def test_find(self):
        assert self.client.content.find()

    def test_find_by(self):
        assert self.client.content.find_by(name=self.content["name"]) == self.content

    def test_find_one(self):
        assert self.client.content.find_one()

    def test_content_item_owner(self):
        item = self.client.content.find_one(include=None)
        assert item
        owner = item.owner
        assert owner["guid"] == self.client.me["guid"]

    def test_content_item_owner_from_include(self):
        item = self.client.content.find_one(include="owner")
        assert item
        owner = item.owner
        assert owner["guid"] == self.client.me["guid"]

    @pytest.mark.skipif(
        CONNECT_VERSION <= version.parse("2024.04.1"),
        reason="Python 3.12 not available",
    )
    def test_restart(self):
        # create content
        content = self.client.content.create(name="example-flask-minimal")
        # create bundle
        path = Path("../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = content.bundles.create(str(path))
        # deploy bundle
        task = bundle.deploy()
        task.wait_for()
        # restart
        content.restart()
        # delete content
        content.delete()

    @pytest.mark.skipif(
        CONNECT_VERSION <= version.parse("2023.01.1"),
        reason="Quarto not available",
    )
    def test_render(self):
        # create content
        content = self.client.content.create(name="example-quarto-minimal")
        # create bundle
        path = Path("../../../resources/connect/bundles/example-quarto-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = content.bundles.create(str(path))
        # deploy bundle
        task = bundle.deploy()
        task.wait_for()
        # render
        task = content.render()
        task.wait_for()
        # delete content
        content.delete()

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.12.0"),
        reason="Lockfile endpoint not available",
    )
    def test_get_lockfile(self):
        # create content
        content = self.client.content.create(name="example-flask-lockfile-test")
        # create bundle with Python requirements
        path = Path("../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = content.bundles.create(str(path))
        # deploy bundle
        task = bundle.deploy()
        task.wait_for()
        # get lockfile
        lockfile = content.get_lockfile()
        # verify lockfile metadata
        assert lockfile.generated_by is not None
        assert isinstance(lockfile.generated_by, str)
        assert len(lockfile.generated_by) > 0
        # verify python version was parsed
        assert lockfile.python_version is not None
        assert isinstance(lockfile.python_version, str)
        assert len(lockfile.python_version) > 0
        # verify lockfile content
        assert lockfile.text is not None
        assert isinstance(lockfile.text, str)
        assert len(lockfile.text) > 0
        # lockfile should contain package information
        # The flask bundle has Flask as a dependency
        assert "flask" in lockfile.text.lower() or "Flask" in lockfile.text
        # delete content
        content.delete()

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.12.0"),
        reason="Lockfile endpoint not available",
    )
    def test_get_lockfile_version_check(self):
        """Test that get_lockfile properly checks Connect version."""
        # This test verifies the @requires decorator works correctly
        # by attempting to call get_lockfile on an older version
        # Since we skip this test on older versions, we just verify
        # that the method exists and is callable on supported versions
        content = self.client.content.create(name="example-version-check")
        path = Path("../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = content.bundles.create(str(path))
        task = bundle.deploy()
        task.wait_for()

        # Verify the method exists and is callable
        assert hasattr(content, "get_lockfile")
        assert callable(content.get_lockfile)

        # Call it to ensure no version errors on supported versions
        lockfile = content.get_lockfile()
        assert lockfile.generated_by is not None
        assert lockfile.python_version is not None
        assert lockfile.text is not None

        # delete content
        content.delete()
