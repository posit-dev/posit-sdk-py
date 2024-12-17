from posit import connect


class TestTags:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.contentA = cls.client.content.create(name="Content_A")
        cls.contentB = cls.client.content.create(name="Content_B")
        cls.contentC = cls.client.content.create(name="Content_C")

    @classmethod
    def teardown_class(cls):
        assert len(cls.client.tags.find()) == 0
        cls.contentA.delete()
        cls.contentB.delete()
        cls.contentC.delete()
        assert len(cls.client.content.find()) == 0

    def test_tags_find(self):
        tags = self.client.tags.find()
        assert len(tags) == 0

    def test_tags_create_destroy(self):
        tagA = self.client.tags.create(name="tagA")
        tagB = self.client.tags.create(name="tagB")
        tagC = self.client.tags.create(name="tagC", parent=tagA)

        assert len(self.client.tags.find()) == 3

        tagA.destroy()
        tagB.destroy()
        ## Deleted when tag A is deleted
        # tagC.destroy()

        assert len(self.client.tags.find()) == 0

    def test_tag_descendants(self):
        tagA = self.client.tags.create(name="tagA")
        tagB = self.client.tags.create(name="tagB")
        tagC = self.client.tags.create(name="tagC", parent=tagA)
        tagD = self.client.tags.create(name="tagD", parent=tagC)

        assert tagA.descendant_tags.find() == [tagC, tagD]

        assert len(tagB.descendant_tags.find()) == 0
        assert tagC.descendant_tags.find() == [tagD]

        # cleanup
        tagA.destroy()
        tagB.destroy()
        assert len(self.client.tags.find()) == 0

    def test_tag_children(self):
        tagA = self.client.tags.create(name="tagA_children")
        tagB = self.client.tags.create(name="tagB_children")
        tagC = self.client.tags.create(name="tagC_children", parent=tagA)
        tagD = self.client.tags.create(name="tagD_children", parent=tagC)

        assert tagA.child_tags.find() == [tagC]
        assert tagB.child_tags.find() == []
        assert tagC.child_tags.find() == [tagD]

        # cleanup
        tagA.destroy()
        tagB.destroy()
        assert len(self.client.tags.find()) == 0

    def test_tag_parent(self):
        tagA = self.client.tags.create(name="tagA_parent")
        tagB = self.client.tags.create(name="tagB_parent")
        tagC = self.client.tags.create(name="tagC_parent", parent=tagA)
        tagD = self.client.tags.create(name="tagD_parent", parent=tagC)

        assert tagA.parent_tag is None
        assert tagB.parent_tag is None
        assert tagC.parent_tag == tagA
        assert tagD.parent_tag == tagC

        # cleanup
        tagA.destroy()
        tagB.destroy()
        assert len(self.client.tags.find()) == 0

    def test_content_item_tags(self):
        tagRoot = self.client.tags.create(name="tagRoot_content_item_tags")
        tagA = self.client.tags.create(name="tagA_content_item_tags", parent=tagRoot)
        tagB = self.client.tags.create(name="tagB_content_item_tags", parent=tagRoot)
        tagC = self.client.tags.create(name="tagC_content_item_tags", parent=tagA)
        tagD = self.client.tags.create(name="tagD_content_item_tags", parent=tagC)

        assert len(self.contentA.tags.find()) == 0

        self.contentA.tags.add(tagD)
        self.contentA.tags.add(tagB)

        # tagB, tagD, tagC (parent of tagD), tagA (parent of tagC)
        # tagD + tagC
        # tagRoot is considered a "category" and is "not a tag"
        assert len(self.contentA.tags.find()) == 4

        # Removes tagB
        self.contentA.tags.delete(tagB)
        assert len(self.contentA.tags.find()) == 4 - 1

        # Removes tagC and tagD (parent of tagC)
        self.contentA.tags.delete(tagC)
        assert len(self.contentA.tags.find()) == 4 - 1 - 2

        # cleanup
        tagRoot.destroy()
        assert len(self.client.tags.find()) == 0

    def test_tag_content_items(self):
        tagRoot = self.client.tags.create(name="tagRoot_tag_content_items")
        tagA = self.client.tags.create(name="tagA_tag_content_items", parent=tagRoot)
        tagB = self.client.tags.create(name="tagB_tag_content_items", parent=tagRoot)
        tagC = self.client.tags.create(name="tagC_tag_content_items", parent=tagA)
        tagD = self.client.tags.create(name="tagD_tag_content_items", parent=tagC)

        assert len(tagA.content_items.find()) == 0
        assert len(tagB.content_items.find()) == 0
        assert len(tagC.content_items.find()) == 0
        assert len(tagD.content_items.find()) == 0

        self.contentA.tags.add(tagD)
        self.contentA.tags.add(tagB)

        self.contentB.tags.add(tagA)
        self.contentB.tags.add(tagC)

        self.contentC.tags.add(tagC)

        assert len(self.contentA.tags.find()) == 4
        assert len(self.contentB.tags.find()) == 2
        assert len(self.contentC.tags.find()) == 2

        assert len(tagA.content_items.find()) == 3
        assert len(tagB.content_items.find()) == 1
        assert len(tagC.content_items.find()) == 3

        # Make sure unique content items are found
        content_items = tagA.content_items.find()
        assert len(content_items) == 3

        content_item_guids = {content_item["guid"] for content_item in content_items}
        assert content_item_guids == {
            self.contentA["guid"],
            self.contentB["guid"],
            self.contentC["guid"],
        }

        # Update tag
        tagD.update(name="tagD_updated")
        assert tagD["name"] == "tagD_updated"
        assert self.client.tags.get(tagD["id"])["name"] == "tagD_updated"

        tagD.update(parent=tagB)
        assert tagD["parent_id"] == tagB["id"]
        assert self.client.tags.get(tagD["id"])["parent_id"] == tagB["id"]

        # Cleanup
        self.contentA.tags.delete(tagRoot)
        self.contentB.tags.delete(tagRoot)
        self.contentC.tags.delete(tagRoot)

        assert len(tagA.content_items.find()) == 0
        assert len(tagB.content_items.find()) == 0
        assert len(tagC.content_items.find()) == 0
        assert len(tagD.content_items.find()) == 0

        tagRoot.destroy()
        assert len(self.client.tags.find()) == 0
