from posit import connect
from posit.connect.content import ContentItem, ContentItemRepository


class TestContentItemRepository:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()

    @classmethod
    def teardown_class(cls):
        assert cls.client.content.count() == 0

    @property
    def content_name(self):
        return "example"

    def create_content(self) -> ContentItem:
        return self.client.content.create(name=self.content_name)

    @property
    def repo_repository(self):
        return "posit-dev/posit-sdk-py"

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

    def test_create_get_update_delete(self):
        content = self.create_content()

        # None by default
        print("!!!!HERE!!!!")
        print(content)
        print(content.repository)

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
        updated_repo = content_repo.update(branch=ex_branch)
        assert updated_repo["branch"] == ex_branch

        assert updated_repo["repository"] == self.repo_repository
        assert updated_repo["directory"] == self.repo_directory
        assert updated_repo["polling"] is self.repo_polling

        # Delete
        content.repository.delete()
        assert content.repository is None

        # Cleanup
        content.delete()
