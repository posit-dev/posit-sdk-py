import requests
import responses

from responses import matchers

from posit.connect.client import Client
from posit.connect.config import Config
from posit.connect.content import ContentItem, ContentItemOwner
from posit.connect.permissions import Permissions

from .api import load_mock  # type: ignore


class TestContentOwnerAttributes:
    @classmethod
    def setup_class(cls):
        guid = "20a79ce3-6e87-4522-9faf-be24228800a4"
        config = Config(api_key="12345", url="https://connect.example/")
        session = requests.Session()
        fake_item = load_mock(f"v1/users/{guid}.json")
        cls.item = ContentItemOwner(config, session, **fake_item)

    def test_guid(self):
        assert self.item.guid == "20a79ce3-6e87-4522-9faf-be24228800a4"

    def test_username(self):
        assert self.item.username == "carlos12"

    def test_first_name(self):
        assert self.item.first_name == "Carlos"

    def test_last_name(self):
        assert self.item.last_name == "User"


class TestContentItemAttributes:
    @classmethod
    def setup_class(cls):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        config = Config(api_key="12345", url="https://connect.example/")
        session = requests.Session()
        fake_item = load_mock(f"v1/content/{guid}.json")
        cls.item = ContentItem(config, session, **fake_item)

    def test_id(self):
        assert self.item.id == "8274"

    def test_guid(self):
        assert self.item.guid == "f2f37341-e21d-3d80-c698-a935ad614066"

    def test_name(self):
        assert self.item.name == "Performance-Data-1671216053560"

    def test_title(self):
        assert self.item.title == "Performance Data"

    def test_description(self):
        assert self.item.description == ""

    def test_access_type(self):
        assert self.item.access_type == "logged_in"

    def test_connection_timeout(self):
        assert self.item.connection_timeout is None

    def test_read_timeout(self):
        assert self.item.read_timeout is None

    def test_init_timeout(self):
        assert self.item.init_timeout is None

    def test_idle_timeout(self):
        assert self.item.idle_timeout is None

    def test_max_processes(self):
        assert self.item.max_processes is None

    def test_min_processes(self):
        assert self.item.min_processes is None

    def test_max_conns_per_process(self):
        assert self.item.max_conns_per_process is None

    def test_load_factor(self):
        assert self.item.load_factor is None

    def test_cpu_request(self):
        assert self.item.cpu_request is None

    def test_cpu_limit(self):
        assert self.item.cpu_limit is None

    def test_memory_request(self):
        assert self.item.memory_request is None

    def test_memory_limit(self):
        assert self.item.memory_limit is None

    def test_amd_gpu_limit(self):
        assert self.item.amd_gpu_limit is None

    def test_nvidia_gpu_limit(self):
        assert self.item.nvidia_gpu_limit is None

    def test_created_time(self):
        assert self.item.created_time == "2022-12-16T18:40:53Z"

    def test_last_deployed_time(self):
        assert self.item.last_deployed_time == "2024-02-24T09:56:30Z"

    def test_bundle_id(self):
        assert self.item.bundle_id == "401171"

    def test_app_mode(self):
        assert self.item.app_mode == "quarto-static"

    def test_content_category(self):
        assert self.item.content_category == ""

    def test_parameterized(self):
        assert self.item.parameterized is False

    def test_cluster_name(self):
        assert self.item.cluster_name == "Local"

    def test_image_name(self):
        assert self.item.image_name is None

    def test_default_image_name(self):
        assert self.item.default_image_name is None

    def test_default_r_environment_management(self):
        assert self.item.default_r_environment_management is None

    def test_default_py_environment_management(self):
        assert self.item.default_py_environment_management is None

    def test_service_account_name(self):
        assert self.item.service_account_name is None

    def test_r_version(self):
        assert self.item.r_version is None

    def test_r_environment_management(self):
        assert self.item.r_environment_management is None

    def test_py_version(self):
        assert self.item.py_version == "3.9.17"

    def test_py_environment_management(self):
        assert self.item.py_environment_management is True

    def test_quarto_version(self):
        assert self.item.quarto_version == "1.3.340"

    def test_run_as(self):
        assert self.item.run_as is None

    def test_run_as_current_user(self):
        assert self.item.run_as_current_user is False

    def test_owner_guid(self):
        assert self.item.owner_guid == "20a79ce3-6e87-4522-9faf-be24228800a4"

    def test_content_url(self):
        assert (
            self.item.content_url
            == "https://connect.example/content/f2f37341-e21d-3d80-c698-a935ad614066/"
        )

    def test_dashboard_url(self):
        assert (
            self.item.dashboard_url
            == "https://connect.example/connect/#/apps/f2f37341-e21d-3d80-c698-a935ad614066"
        )

    def test_app_role(self):
        assert self.item.app_role == "viewer"

    def test_owner(self):
        assert "owner" not in self.item

    def test_permissions(self):
        assert isinstance(self.item.permissions, Permissions)

    def test_tags(self):
        assert self.item.tags == []


class TestContentItemGetContentOwner:
    @responses.activate
    def test_owner(self):
        mock_content = load_mock(
            "v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"
        )
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=mock_content,
        )

        mock_user_get = responses.get(
            f"https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock(
                f"v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"
            ),
        )

        c = Client("12345", "https://connect.example")
        item = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")
        owner = item.owner
        assert owner.guid == "20a79ce3-6e87-4522-9faf-be24228800a4"

        # load a second time, assert tha owner is loaded from cached result
        owner = item.owner
        assert owner.guid == "20a79ce3-6e87-4522-9faf-be24228800a4"
        assert mock_user_get.call_count == 1


class TestContentItemDelete:
    @responses.activate
    def test(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_delete = responses.delete(
            f"https://connect.example/__api__/v1/content/{guid}"
        )

        # setup
        config = Config(api_key="12345", url="https://connect.example/")
        session = requests.Session()
        fake_item = load_mock(f"v1/content/{guid}.json")
        item = ContentItem(config, session, **fake_item)

        # invoke
        item.delete()

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
        c = Client("12345", "https://connect.example")
        content = c.content.get(content_guid)

        # invoke
        task = content.deploy()

        # assert
        task.id == task_id
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
        con = Client("12345", "https://connect.example")
        content = con.content.get(guid)
        assert content.guid == guid

        new_name = "New Name"
        fake_content = load_mock(f"v1/content/{guid}.json")
        fake_content.update(name=new_name)
        responses.patch(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=fake_content,
        )

        content.update(name=new_name)
        assert content.name == new_name


class TestContentCreate:
    @responses.activate
    def test(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        fake_content_item = load_mock(f"v1/content/{guid}.json")

        # behavior
        responses.post(
            f"https://connect.example/__api__/v1/content",
            json=load_mock(f"v1/content/{guid}.json"),
            match=[
                matchers.json_params_matcher(
                    {"name": fake_content_item["name"]}
                )
            ],
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example/")

        # invoke
        content_item = client.content.create(name=fake_content_item["name"])

        # assert
        assert content_item.name == fake_content_item["name"]


class TestContentsFind:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({"include": "owner,tags"})],
        )

        # setup
        client = Client("12345", "https://connect.example")

        # invoke
        content = client.content.find()

        #  assert
        assert mock_get.call_count == 1
        assert len(content) == 3
        assert content[0].name == "team-admin-dashboard"
        assert content[1].name == "Performance-Data-1671216053560"
        assert content[2].name == "My-Streamlit-app"

    @responses.activate
    def test_params_include(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({"include": "tags"})],
        )

        # setup
        client = Client("12345", "https://connect.example")

        # invoke
        client.content.find(include="tags")

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
        client = Client("12345", "https://connect.example")

        # invoke
        client.content.find(include=None)

        #  assert
        assert mock_get.call_count == 1


class TestContentsFindOne:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({"include": "owner,tags"})],
        )

        # setup
        client = Client("12345", "https://connect.example")

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
            match=[
                matchers.query_param_matcher(
                    {"owner_guid": owner_guid, "include": "owner,tags"}
                )
            ],
        )

        # setup
        client = Client("12345", "https://connect.example")

        # invoke
        content_item = client.content.find_one(owner_guid=owner_guid)

        #  assert
        assert mock_get.call_count == 1
        assert content_item
        assert content_item.owner_guid == owner_guid

    @responses.activate
    def test_name(self):
        # data
        name = "team-admin-dashboard"

        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[
                matchers.query_param_matcher(
                    {"name": name, "include": "owner,tags"}
                )
            ],
        )

        # setup
        client = Client("12345", "https://connect.example")

        # invoke
        content_item = client.content.find_one(name=name)

        #  assert
        assert mock_get.call_count == 1
        assert content_item
        assert content_item.name == name

    @responses.activate
    def test_params_include(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
            match=[matchers.query_param_matcher({"include": "tags"})],
        )

        # setup
        client = Client("12345", "https://connect.example")

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
        client = Client("12345", "https://connect.example")

        # invoke
        client.content.find_one(include=None)

        #  assert
        assert mock_get.call_count == 1


class TestContentsGet:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock(
                "v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"
            ),
        )
        con = Client("12345", "https://connect.example")
        get_one = con.content.get("f2f37341-e21d-3d80-c698-a935ad614066")
        assert get_one.name == "Performance-Data-1671216053560"


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
