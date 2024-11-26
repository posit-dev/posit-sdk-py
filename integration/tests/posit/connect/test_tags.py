from typing import TYPE_CHECKING

import pytest
from packaging import version

from posit import connect

from . import CONNECT_VERSION

if TYPE_CHECKING:
    from posit.connect.content import ContentItem


# add integration tests here!
@pytest.mark.skipif(
    CONNECT_VERSION < version.parse("2024.10.0-dev"),
    reason="Packages API unavailable",
)
class TestTags:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.contentA = cls.client.content.create(name=cls.__name__)
        cls.contentB = cls.client.content.create(name=cls.__name__)
        cls.contentC = cls.client.content.create(
            name=cls.__name__,
        )

    @classmethod
    def teardown_class(cls):
        assert len(cls.client.tags.find()) == 0

    def test_tags_find(self):
        tags = self.client.tags.find()
        assert len(tags) == 0

    def test_tags_create_destroy(self):
        tagA = self.client.tags.create(name="tagA")
        tagB = self.client.tags.create(name="tagB")
        tagC = self.client.tags.create(name="tagC", parent=self.tagA)

        assert len(self.client.tags.find()) == 3

        tagA.destroy()
        tagB.destroy()
        ## Deleted when tag A is deleted
        # tagC.destroy()

        assert len(self.client.tags.find()) == 0

    def test_tag_descendants(self):
        # Have created tags persist
        self.tagA = self.client.tags.create(name="tagA")
        self.tagB = self.client.tags.create(name="tagB")
        self.tagC = self.client.tags.create(name="tagC", parent=self.tagA)
        self.tagD = self.client.tags.create(name="tagD", parent=self.tagC)

        assert self.tagA.descendant_tags.find() == [self.tagC, self.tagD]

        assert len(self.tagB.descendant_tags.find()) == 0
        assert len(self.tagC.descendant_tags.find()) == [self.tagD]

    def test_tag_children(self):
        assert self.tagA.children_tags.find() == [self.tagC]
        assert self.tagB.children_tags.find() == []
        assert self.tagC.children_tags.find() == [self.tagD]

    def test_tag_parent(self):
        assert self.tagA.parent_tag is None
        assert self.tagB.parent_tag is None
        assert self.tagC.parent_tag == self.tagA
        assert self.tagD.parent_tag == self.tagC

    def test_content_a_tags(self):
        assert len(self.contentA.tags.find()) == 0

        self.contentA.tags.add(self.tagA)
        self.contentA.tags.add(self.tagB)

        # tagB, tagC, tagA (parent of tagC)
        assert len(self.contentA.tags.find()) == 3

        self.contentA.tags.delete(self.tagB)
        assert len(self.contentA.tags.find()) == 2

        # Removes tagC and tagA (parent of tagC)
        self.contentA.tags.delete(self.tagA)
        assert len(self.contentA.tags.find()) == 0

    def test_tags_content_items(self):
        assert len(self.tagA.content_items.find()) == 0
        assert len(self.tagB.content_items.find()) == 0
        assert len(self.tagC.content_items.find()) == 0

        self.contentA.tags.add(self.tagA)
        self.contentA.tags.add(self.tagB)

        self.contentB.tags.add(self.tagA)
        self.contentB.tags.add(self.tagC)

        self.contentC.tags.add(self.tagC)

        assert len(self.contentA.tags.find()) == 2
        assert len(self.contentB.tags.find()) == 2
        assert len(self.contentC.tags.find()) == 1

        assert len(self.tagA.content_items.find()) == 2
        assert len(self.tagB.content_items.find()) == 1
        assert len(self.tagC.content_items.find()) == 2

        # Make sure unique content items are found
        content_items_list: list[ContentItem] = []
        for tag in [self.tagA, *self.tagA.descendant_tags.find()]:
            content_items_list.extend(tag.content_items.find())
        # Get unique items
        content_items_list = list(set(content_items_list))

        assert content_items_list == [self.contentA, self.contentB, self.contentC]

        self.contentA.tags.delete(self.tagA, self.tagB)
        self.contentB.tags.delete(self.tagA)
        self.contentC.tags.delete(self.tagC)

        assert len(self.tagA.content_items.find()) == 0
        assert len(self.tagB.content_items.find()) == 0
        assert len(self.tagC.content_items.find()) == 0
