import pytest
from packaging import version

from posit import connect
from posit.connect.content import ContentItem
from posit.connect.repository import ContentItemRepository

from . import CONNECT_VERSION


class TestContentItemRepository:
    content: ContentItem

    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.content = cls.client.content.create(name="example")

    @classmethod
    def teardown_class(cls):
        cls.content.delete()
        assert cls.client.content.count() == 0

    @property
    def repo_repository(self):
        return "https://github.com/posit-dev/posit-sdk-py"

    @property
    def repo_branch(self):
        return "1dacc4dd"

    @property
    def repo_directory(self):
        return "integration/resources/connect/bundles/example-quarto-minimal"

    @property
    def repo_polling(self):
        return False

    @property
    def default_repository(self):
        return {
            "repository": self.repo_repository,
            "branch": self.repo_branch,
            "directory": self.repo_directory,
            "polling": self.repo_polling,
        }

    @pytest.mark.skipif(
        # Added to the v2022.12.0 milestone
        # https://github.com/rstudio/connect/issues/22242#event-7859377097
        CONNECT_VERSION < version.parse("2022.12.0"),
        reason="Repository routes not implemented",
    )
    def test_create_get_update_delete(self):
        content = self.content

        # None by default
        assert content.repository is None

        # Create
        new_repo = content.create_repository(**self.default_repository)

        # Get
        content_repo = content.repository
        assert content_repo is not None

        def assert_repo(r: ContentItemRepository):
            assert isinstance(content_repo, ContentItemRepository)
            assert r["repository"] == self.repo_repository
            assert r["branch"] == self.repo_branch
            assert r["directory"] == self.repo_directory
            assert r["polling"] is self.repo_polling

        assert_repo(new_repo)
        assert_repo(content_repo)

        # Update
        ex_branch = "main"
        content_repo.update(branch=ex_branch)
        assert content_repo["branch"] == ex_branch

        assert content_repo["repository"] == self.repo_repository
        assert content_repo["directory"] == self.repo_directory
        assert content_repo["polling"] is self.repo_polling

        # Delete
        content_repo.destroy()
        assert content.repository is None
