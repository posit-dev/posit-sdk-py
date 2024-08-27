from posit import connect


class TestTags:
    def setup_class(cls):
        cls.client = connect.Client()
        cls.balbo = cls.client.tags.create(name="Balbo Baggins")

    def teardown_class(cls):
        cls.balbo.delete()

    def test_count(self):
        assert self.client.tags.count() == 1

    def test_get(self):
        assert self.client.tags.get(self.balbo.id)

    def test_find(self):
        assert self.client.tags.find() == [self.balbo]

    def test_find_one(self):
        assert self.client.tags.find_one() == self.balbo

    def test_update(self):
        frodo = self.client.tags.create(name="Frodo Baggins")
        frodo.update(name="Mr. Underhill")
        assert frodo.name == "Mr. Underhill"
        assert self.client.tags.get(frodo.id).name == "Mr. Underhill"
        frodo.update(name="Frodo Baggins")
        frodo.delete()

    def test_relationships(self):
        balbo = self.balbo
        mungo = balbo.create_child(name="Mungo Baggins")
        largo = mungo.create_child(name="Largo Baggins")
        fosco = largo.create_child(name="Fosco Baggins")
        drogo = fosco.create_child(name="Drogo Baggins")
        frodo = drogo.create_child(name="Frodo Baggins")

        assert balbo.children == [mungo]
        assert mungo.children == [largo]
        assert largo.children == [fosco]
        assert fosco.children == [drogo]
        assert drogo.children == [frodo]

        assert frodo.parent == drogo
        assert drogo.parent == fosco
        assert fosco.parent == largo
        assert largo.parent == mungo
        assert mungo.parent == balbo
        # there and back again...
