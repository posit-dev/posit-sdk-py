from pathlib import Path

from posit import connect


class TestContent:
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
