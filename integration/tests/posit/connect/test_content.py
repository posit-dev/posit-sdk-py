from pathlib import Path

import pytest
from packaging import version

from posit import connect

from . import CONNECT_VERSION, fixtures


class TestContent:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create()

    def test_count(self):
        # Assert that count works. We don't care what the count is.
        assert self.client.content.count()

    def test_get(self):
        assert self.client.content.get(self.content["guid"]) == self.content

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
        content = self.client.content.create(name=fixtures.name())
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
        content = self.client.content.create(name=fixtures.name())
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
