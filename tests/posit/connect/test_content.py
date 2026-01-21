import pytest
import responses
from responses import matchers

from posit.connect.client import Client
from posit.connect.content import ContentItem
from posit.connect.resources import _Resource

from .api import load_mock, load_mock_dict


class TestContentItemGetContentOwner:
    @responses.activate
    def test_owner(self):
        mock_content = load_mock_dict("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json")
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=mock_content,
        )

        mock_user_get = responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )

        c = Client("https://connect.example", "12345")
        item = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")
        owner = item.owner
        assert owner["guid"] == "20a79ce3-6e87-4522-9faf-be24228800a4"

        # load a second time, assert tha owner is loaded from cached result
        owner = item.owner
        assert owner["guid"] == "20a79ce3-6e87-4522-9faf-be24228800a4"
        assert mock_user_get.call_count == 1


class TestContentItemDelete:
    @responses.activate
    def test(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        mock_delete = responses.delete(f"https://connect.example/__api__/v1/content/{guid}")

        # setup
        c = Client("https://connect.example", "12345")
        content = c.content.get(guid)

        # invoke
        content.delete()

        # assert
        assert mock_delete.call_count == 1


class TestContentDeploy:
    @responses.activate
    def test(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        bundle_id = "101"
        task_id = "jXhOhdm5OOSkGhJw"

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_content_deploy = responses.post(
            f"https://connect.example/__api__/v1/content/{content_guid}/deploy",
            match=[matchers.json_params_matcher({"bundle_id": None})],
            json={"task_id": task_id},
        )

        mock_tasks_get = responses.get(
            f"https://connect.example/__api__/v1/tasks/{task_id}",
            json=load_mock(f"v1/tasks/{task_id}.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        content = c.content.get(content_guid)

        # invoke
        task = content.deploy()

        # assert
        assert task["id"] == task_id
        assert mock_content_get.call_count == 1
        assert mock_content_deploy.call_count == 1
        assert mock_tasks_get.call_count == 1


class TestContentUpdate:
    @responses.activate
    def test_update(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )
        con = Client("https://connect.example", "12345")
        content = con.content.get(guid)
        assert content["guid"] == guid

        new_name = "New Name"
        fake_content = load_mock_dict(f"v1/content/{guid}.json")
        fake_content.update(name=new_name)
        responses.patch(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=fake_content,
        )

        content.update(name=new_name)
        assert content["name"] == new_name


class TestContentCreate:
    @responses.activate
    def test(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_content_item = load_mock_dict(f"v1/content/{guid}.json")

        # behavior
        responses.post(
            "https://connect.example/__api__/v1/content",
            json=load_mock(f"v1/content/{guid}.json"),
            match=[matchers.json_params_matcher({"name": fake_content_item["name"]})],
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example/")

        # invoke
        fake_name = fake_content_item["name"]
        assert isinstance(fake_name, str)
        content_item = client.content.create(name=fake_name)

        # assert
        assert content_item["name"] == fake_content_item["name"]


class TestContentsFind:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        content = client.content.find()

        # assert
        assert mock_get.call_count == 1
        assert len(content) == 3
        assert content[0]["name"] == "team-admin-dashboard"
        assert content[1]["name"] == "Performance-Data-1671216053560"
        assert content[2]["name"] == "My-Streamlit-app"

    @responses.activate
    def test_params_include_string(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({"include": "tags"})],
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        client.content.find(include="tags")

        #  assert
        assert mock_get.call_count == 1

    @responses.activate
    def test_params_include_list(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({"include": "tags,owner"})],
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        client.content.find(include=["tags", "owner"])

        #  assert
        assert mock_get.call_count == 1

    @responses.activate
    def test_params_include_none(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({})],
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        client.content.find(include=None)

        #  assert
        assert mock_get.call_count == 1


class TestContentsFindBy:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        content = client.content.find_by(name="team-admin-dashboard")

        # assert
        assert mock_get.call_count == 1
        assert content
        assert content["name"] == "team-admin-dashboard"

    @responses.activate
    def test_miss(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        content = client.content.find_by(name="does-not-exist")

        # assert
        assert mock_get.call_count == 1
        assert content is None


class TestContentsFindOne:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        content_item = client.content.find_one()

        #  assert
        assert mock_get.call_count == 1
        assert content_item

    @responses.activate
    def test_owner_guid(self):
        # data
        owner_guid = "a01792e3-2e67-402e-99af-be04a48da074"

        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        content_item = client.content.find_one(owner_guid=owner_guid)

        #  assert
        assert mock_get.call_count == 1
        assert content_item
        assert content_item["owner_guid"] == owner_guid

    @responses.activate
    def test_name(self):
        # data
        name = "team-admin-dashboard"

        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        content_item = client.content.find_one(name=name)

        #  assert
        assert mock_get.call_count == 1
        assert content_item
        assert content_item["name"] == name

    @responses.activate
    def test_params_include_string(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({"include": "tags"})],
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        client.content.find_one(include="tags")

        #  assert
        assert mock_get.call_count == 1

    @responses.activate
    def test_params_include_none(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({})],
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        client.content.find_one(include=None)

        #  assert
        assert mock_get.call_count == 1


class TestContentsGet:
    @responses.activate
    def test(self):
        # All calls to get() should automatically include all available optional fields
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
            match=[matchers.query_param_matcher({"include": "owner,tags,vanity_url"})],
        )
        con = Client("https://connect.example", "12345")
        get_one = con.content.get("f2f37341-e21d-3d80-c698-a935ad614066")
        assert get_one["name"] == "Performance-Data-1671216053560"


class TestContentCurrent:
    @responses.activate
    def test_with_env_var(self, monkeypatch):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        monkeypatch.setenv("CONNECT_CONTENT_GUID", guid)

        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
            match=[matchers.query_param_matcher({"include": "owner,tags,vanity_url"})],
        )
        c = Client("https://connect.example", "12345")
        content_item = c.content.get()
        assert content_item["guid"] == guid

    def test_without_env_var(self, monkeypatch):
        monkeypatch.delenv("CONNECT_CONTENT_GUID", raising=False)
        c = Client("https://connect.example", "12345")
        with pytest.raises(
            RuntimeError, match="CONNECT_CONTENT_GUID environment variable is not set."
        ):
            _ = c.content.get()


class TestContentsCount:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )
        con = Client(api_key="12345", url="https://connect.example/")
        count = con.content.count()
        assert count == 3


class TestRender:
    @responses.activate
    def test(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        get_content = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        patch_content = responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        get_variants = responses.get(
            f"https://connect.example.com/__api__/applications/{guid}/variants",
            json=load_mock(f"applications/{guid}/variants.json"),
        )

        post_render = responses.post(
            "https://connect.example.com/__api__/variants/6627/render",
            json=load_mock("variants/6627/render.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        task = content.render()

        # assert
        assert task is not None
        assert get_content.call_count == 1
        assert patch_content.call_count == 1
        assert get_variants.call_count == 1
        assert post_render.call_count == 1

    @responses.activate
    def test_app_mode_is_other(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fixture_content = load_mock_dict(f"v1/content/{guid}.json")
        fixture_content.update(app_mode="other")

        # behavior
        responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=fixture_content,
        )

        responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=fixture_content,
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        with pytest.raises(ValueError):
            content.render()

    @responses.activate
    def test_missing_default(self):
        responses.get(
            "https://connect.example.com/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.patch(
            "https://connect.example.com/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.get(
            "https://connect.example.com/__api__/applications/f2f37341-e21d-3d80-c698-a935ad614066/variants",
            json=[],
        )

        c = Client("https://connect.example.com", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")
        with pytest.raises(RuntimeError):
            content.render()


class TestRestart:
    @responses.activate
    def test(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fixture_content = load_mock_dict(f"v1/content/{guid}.json")
        fixture_content.update(app_mode="api")

        # behavior
        mock_get_content = mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=fixture_content,
        )

        mock_patch_content = responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=fixture_content,
        )

        mock_patch_environment = responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}/environment",
        )

        mock_get_content_page = responses.get(
            f"https://connect.example.com/content/{guid}",
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        task = content.restart()

        # assert
        assert task is None
        assert mock_get_content.call_count == 1
        assert mock_patch_content.call_count == 1
        assert mock_patch_environment.call_count == 2
        assert mock_get_content_page.call_count == 1

    @responses.activate
    def test_app_mode_is_other(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fixture_content = load_mock_dict(f"v1/content/{guid}.json")
        fixture_content.update(app_mode="other")

        # behavior
        mock_get_content = mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=fixture_content,
        )

        mock_patch_content = responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=fixture_content,
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        with pytest.raises(ValueError):
            content.restart()

        # assert
        assert mock_get_content.call_count == 1
        assert mock_patch_content.call_count == 1


class TestLockfile:
    def test_from_response(self):
        from posit.connect.content import Lockfile

        generated_by = "connect; python=3.11.4"
        content = "bottle==0.12.25"

        lockfile = Lockfile._from_response(generated_by, content)

        assert lockfile.generated_by == generated_by
        assert lockfile.python_version == "3.11.4"
        assert lockfile.text == content

    def test_from_response_invalid_header(self):
        from posit.connect.content import Lockfile

        # Missing python version
        with pytest.raises(ValueError, match="Failed to parse Python version"):
            Lockfile._from_response("connect", "content")

        # Invalid format
        with pytest.raises(ValueError, match="Failed to parse Python version"):
            Lockfile._from_response("connect; python=invalid", "content")

    def test_write(self, tmp_path):
        from posit.connect.content import Lockfile

        lockfile = Lockfile(
            generated_by="connect; python=3.11.4",
            python_version="3.11.4",
            text="bottle==0.12.25\nflask==2.0.0\n",
        )

        output_path = tmp_path / "requirements.txt.lock"
        lockfile.write(str(output_path))

        assert output_path.exists()
        assert output_path.read_text() == "bottle==0.12.25\nflask==2.0.0\n"


class TestContentGetLockfile:
    @responses.activate
    def test_get_lockfile_success(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        lockfile_content = """# This file is autogenerated by pip-compile with Python 3.11
bottle==0.12.25
    # via -r requirements.txt
"""

        # behavior
        responses.get(
            "https://connect.example/__api__/server_settings",
            json={"version": "2025.12.0"},
        )

        mock_get_content = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        mock_get_lockfile = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}/lockfile",
            body=lockfile_content,
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Content-Disposition": f'attachment; filename="{guid}-requirements.txt.lock"',
                "Generated-By": "connect; python=3.11.4",
            },
        )

        # setup
        client = Client("https://connect.example", "12345")
        content = client.content.get(guid)

        # invoke
        lockfile = content.get_lockfile()

        # assert
        assert lockfile.generated_by == "connect; python=3.11.4"
        assert lockfile.python_version == "3.11.4"
        assert lockfile.text == lockfile_content
        assert mock_get_content.call_count == 1
        assert mock_get_lockfile.call_count == 1

    @responses.activate
    def test_get_lockfile_version_check(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior - older version that doesn't support lockfile endpoint
        responses.get(
            "https://connect.example/__api__/server_settings",
            json={"version": "2024.11.0"},
        )

        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")
        content = client.content.get(guid)

        # invoke & assert
        with pytest.raises(
            RuntimeError,
            match="This API is not available in Connect version 2024.11.0. Please upgrade to version 2025.12.0 or later.",
        ):
            content.get_lockfile()

    @responses.activate
    def test_get_lockfile_no_python_environment(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        responses.get(
            "https://connect.example/__api__/server_settings",
            json={"version": "2025.12.0"},
        )

        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        # Mock 400 error for content without managed Python environment
        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}/lockfile",
            status=400,
            json={
                "code": 1,
                "error": "Content does not have a managed Python environment",
            },
        )

        # setup
        client = Client("https://connect.example", "12345")
        content = client.content.get(guid)

        # invoke & assert
        from posit.connect.errors import ClientError

        with pytest.raises(ClientError) as exc_info:
            content.get_lockfile()
        assert "Content does not have a managed Python environment" in str(exc_info.value)

    @responses.activate
    def test_get_lockfile_missing_generated_by_header(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        lockfile_content = "bottle==0.12.25"

        # behavior
        responses.get(
            "https://connect.example/__api__/server_settings",
            json={"version": "2025.12.0"},
        )

        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        # Mock response without Generated-By header (server error case)
        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}/lockfile",
            body=lockfile_content,
            headers={
                "Content-Type": "text/plain; charset=utf-8",
            },
        )

        # setup
        client = Client("https://connect.example", "12345")
        content = client.content.get(guid)

        # invoke & assert
        with pytest.raises(ValueError, match="Server response missing 'Generated-By' header"):
            content.get_lockfile()

    @responses.activate
    def test_get_lockfile_invalid_generated_by_header(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        lockfile_content = "bottle==0.12.25"

        # behavior
        responses.get(
            "https://connect.example/__api__/server_settings",
            json={"version": "2025.12.0"},
        )

        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        # Mock response with invalid Generated-By header (missing python version)
        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}/lockfile",
            body=lockfile_content,
            headers={
                "Content-Type": "text/plain; charset=utf-8",
                "Generated-By": "connect",
            },
        )

        # setup
        client = Client("https://connect.example", "12345")
        content = client.content.get(guid)

        # invoke & assert
        with pytest.raises(ValueError, match="Failed to parse Python version"):
            content.get_lockfile()


class TestContentRepository:
    base_url = "http://connect.example"
    client = Client(base_url, "12345")

    @property
    def content_guid(self):
        return "f2f37341-e21d-3d80-c698-a935ad614066"

    @property
    def content_item(self):
        return ContentItem(self.ctx, guid=self.content_guid)

    @property
    def endpoint(self):
        return f"{self.base_url}/__api__/v1/content/{self.content_guid}/repository"

    @property
    def ctx(self):
        return self.client._ctx

    def mock_repository_info(self):
        content_item = self.content_item

        mock_get = responses.get(
            self.endpoint,
            json=load_mock_dict(f"v1/content/{self.content_guid}/repository.json"),
        )
        repository_info = content_item.repository

        assert isinstance(repository_info, _Resource)
        assert mock_get.call_count == 1

        return repository_info

    @responses.activate
    def test_repository_getter_returns_repository(self):
        # Performs assertions in helper property method
        self.mock_repository_info()

    @responses.activate
    def test_repository_update(self):
        repository_info = self.mock_repository_info()

        mock_patch = responses.patch(
            self.endpoint,
            json=load_mock_dict(f"v1/content/{self.content_guid}/repository_patch.json"),
        )
        repository_info.update(branch="testing-main")
        assert mock_patch.call_count == 1

        for key, value in repository_info.items():
            if key == "branch":
                assert repository_info[key] == "testing-main"
            else:
                assert repository_info[key] == value

    @responses.activate
    def test_repository_delete(self):
        repository_info = self.mock_repository_info()

        mock_delete = responses.delete(self.endpoint)
        repository_info.destroy()

        assert mock_delete.call_count == 1
