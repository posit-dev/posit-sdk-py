from posit import connect

from . import fixtures


class TestTags:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.A = cls.client.content.create(name=fixtures.name())
        cls.B = cls.client.content.create(name=fixtures.name())
        cls.C = cls.client.content.create(name=fixtures.name())

    def test_tags_find(self):
        tags = self.client.tags.find()
        assert len(tags) == 0

    def test_tags_create_destroy(self):
        a = self.client.tags.create(name=fixtures.name())
        b = self.client.tags.create(name=fixtures.name())
        c = self.client.tags.create(name=fixtures.name(), parent=a)

        assert len(self.client.tags.find()) == 3

        a.destroy()
        b.destroy()

        assert len(self.client.tags.find()) == 0

    def test_tag_descendants(self):
        a = self.client.tags.create(name=fixtures.name())
        b = self.client.tags.create(name=fixtures.name())
        c = self.client.tags.create(name=fixtures.name(), parent=a)
        d = self.client.tags.create(name=fixtures.name(), parent=c)

        assert a.descendant_tags.find() == [c, d]

        assert len(b.descendant_tags.find()) == 0
        assert c.descendant_tags.find() == [d]

        # cleanup
        a.destroy()
        b.destroy()
        assert len(self.client.tags.find()) == 0

    def test_tag_children(self):
        a = self.client.tags.create(name=fixtures.name())
        b = self.client.tags.create(name=fixtures.name())
        c = self.client.tags.create(name=fixtures.name(), parent=a)
        d = self.client.tags.create(name=fixtures.name(), parent=c)

        assert a.child_tags.find() == [c]
        assert b.child_tags.find() == []
        assert c.child_tags.find() == [d]

        # cleanup
        a.destroy()
        b.destroy()
        assert len(self.client.tags.find()) == 0

    def test_tag_parent(self):
        a = self.client.tags.create(name=fixtures.name())
        b = self.client.tags.create(name=fixtures.name())
        c = self.client.tags.create(name=fixtures.name(), parent=a)
        d = self.client.tags.create(name=fixtures.name(), parent=c)

        assert a.parent_tag is None
        assert b.parent_tag is None
        assert c.parent_tag == a
        assert d.parent_tag == c

        # cleanup
        a.destroy()
        b.destroy()
        assert len(self.client.tags.find()) == 0

    def test_content_item_tags(self):
        root = self.client.tags.create(name=fixtures.name())
        a = self.client.tags.create(name=fixtures.name(), parent=root)
        b = self.client.tags.create(name=fixtures.name(), parent=root)
        c = self.client.tags.create(name=fixtures.name(), parent=a)
        d = self.client.tags.create(name=fixtures.name(), parent=c)

        assert len(self.A.tags.find()) == 0

        self.A.tags.add(d)
        self.A.tags.add(b)

        # b, d, c (parent of d), a (parent of c)
        # d + c
        # root is considered a "category" and is "not a tag"
        assert len(self.A.tags.find()) == 4

        # Removes b
        self.A.tags.delete(b)
        assert len(self.A.tags.find()) == 4 - 1

        # Removes c and d (parent of c)
        self.A.tags.delete(c)
        assert len(self.A.tags.find()) == 4 - 1 - 2

        # cleanup
        root.destroy()
        assert len(self.client.tags.find()) == 0

    def test_tag_content_items(self):
        root = self.client.tags.create(name=fixtures.name())
        a = self.client.tags.create(name=fixtures.name(), parent=root)
        b = self.client.tags.create(name=fixtures.name(), parent=root)
        c = self.client.tags.create(name=fixtures.name(), parent=a)
        d = self.client.tags.create(name=fixtures.name(), parent=c)

        assert len(a.content_items.find()) == 0
        assert len(b.content_items.find()) == 0
        assert len(c.content_items.find()) == 0
        assert len(d.content_items.find()) == 0

        self.A.tags.add(d)
        self.A.tags.add(b)

        self.B.tags.add(a)
        self.B.tags.add(c)

        self.C.tags.add(c)

        assert len(self.A.tags.find()) == 4
        assert len(self.B.tags.find()) == 2
        assert len(self.C.tags.find()) == 2

        assert len(a.content_items.find()) == 3
        assert len(b.content_items.find()) == 1
        assert len(c.content_items.find()) == 3

        # Make sure unique content items are found
        content_items = a.content_items.find()
        assert len(content_items) == 3

        content_item_guids = {content_item["guid"] for content_item in content_items}
        assert content_item_guids == {
            self.A["guid"],
            self.B["guid"],
            self.C["guid"],
        }

        # Update tag
        name = fixtures.name()
        d.update(name=name)
        assert d["name"] == name
        assert self.client.tags.get(d["id"])["name"] == name

        d.update(parent=b)
        assert d["parent_id"] == b["id"]
        assert self.client.tags.get(d["id"])["parent_id"] == b["id"]

        # Cleanup
        self.A.tags.delete(root)
        self.B.tags.delete(root)
        self.C.tags.delete(root)

        assert len(a.content_items.find()) == 0
        assert len(b.content_items.find()) == 0
        assert len(c.content_items.find()) == 0
        assert len(d.content_items.find()) == 0

        root.destroy()
        assert len(self.client.tags.find()) == 0
