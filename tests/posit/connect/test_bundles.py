import io

import pytest
import requests
import responses

from responses import matchers
from unittest import mock

from posit.connect import Client
from posit.connect.config import Config
from posit.connect.bundles import Bundle

from .api import load_mock, get_path  # type: ignore


class TestBundleProperties:
    def setup_class(cls):
        config = Config(api_key="12345", url="https://connect.example/")
        session = requests.Session()
        cls.bundle = Bundle(
            config,
            session,
            **load_mock(
                f"v1/content/f2f37341-e21d-3d80-c698-a935ad614066/bundles/101.json"
            ),
        )

    def test_id(self):
        assert self.bundle.id == "101"

    def test_content_guid(self):
        assert (
            self.bundle.content_guid == "f2f37341-e21d-3d80-c698-a935ad614066"
        )

    def test_created_time(self):
        assert self.bundle.created_time == "2006-01-02T15:04:05Z07:00"

    def test_cluster_name(self):
        assert self.bundle.cluster_name == "Local"

    def test_image_name(self):
        assert self.bundle.image_name == "Local"

    def test_r_version(self):
        assert self.bundle.r_version == "3.5.1"

    def test_r_environment_management(self):
        assert self.bundle.r_environment_management == True

    def test_py_version(self):
        assert self.bundle.py_version == "3.8.2"

    def test_py_environment_management(self):
        assert self.bundle.py_environment_management == True

    def test_quarto_version(self):
        assert self.bundle.quarto_version == "0.2.22"

    def test_active(self):
        assert self.bundle.active == False

    def test_size(self):
        assert self.bundle.size == 1000000

    def test_metadata_source(self):
        assert self.bundle.metadata.source == "string"

    def test_metadata_source_repo(self):
        assert self.bundle.metadata.source_repo == "string"

    def test_metadata_source_branch(self):
        assert self.bundle.metadata.source_branch == "string"

    def test_metadata_source_commit(self):
        assert self.bundle.metadata.source_commit == "string"

    def test_metadata_archive_md5(self):
        assert (
            self.bundle.metadata.archive_md5
            == "37324238a80595c453c706b22adb83d3"
        )

    def test_metadata_archive_sha1(self):
        assert (
            self.bundle.metadata.archive_sha1
            == "a2f7d13d87657df599aeeabdb70194d508cfa92f"
        )


class TestBundleDelete:
    @responses.activate
    def test(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        bundle_id = "101"

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundle_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}",
            json=load_mock(
                f"v1/content/{content_guid}/bundles/{bundle_id}.json"
            ),
        )

        mock_bundle_delete = responses.delete(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}",
        )

        # setup
        c = Client("12345", "https://connect.example")
        bundle = c.content.get(content_guid).bundles.get(bundle_id)

        # invoke
        bundle.delete()

        # assert
        assert mock_content_get.call_count == 1
        assert mock_bundle_get.call_count == 1
        assert mock_bundle_delete.call_count == 1


class TestBundleDeploy:
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

        mock_bundle_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}",
            json=load_mock(
                f"v1/content/{content_guid}/bundles/{bundle_id}.json"
            ),
        )

        mock_bundle_deploy = responses.post(
            f"https://connect.example/__api__/v1/content/{content_guid}/deploy",
            match=[matchers.json_params_matcher({"bundle_id": bundle_id})],
            json={"task_id": task_id},
        )

        mock_tasks_get = responses.get(
            f"https://connect.example/__api__/v1/tasks/{task_id}",
            json=load_mock(f"v1/tasks/{task_id}.json"),
        )

        # setup
        c = Client("12345", "https://connect.example")
        bundle = c.content.get(content_guid).bundles.get(bundle_id)

        # invoke
        task = bundle.deploy()

        # assert
        task.id == task_id
        assert mock_content_get.call_count == 1
        assert mock_bundle_get.call_count == 1
        assert mock_bundle_deploy.call_count == 1
        assert mock_tasks_get.call_count == 1


class TestBundleDownload:
    @mock.patch("builtins.open", new_callable=mock.mock_open)
    @responses.activate
    def test_output_as_str(self, mock_file: mock.MagicMock):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        bundle_id = "101"
        path = get_path(
            f"v1/content/{content_guid}/bundles/{bundle_id}/download/bundle.tar.gz"
        )

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundle_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}",
            json=load_mock(
                f"v1/content/{content_guid}/bundles/{bundle_id}.json"
            ),
        )

        mock_bundle_download = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}/download",
            body=path.read_bytes(),
        )

        # setup
        c = Client("12345", "https://connect.example")
        bundle = c.content.get(content_guid).bundles.get(bundle_id)

        # invoke
        bundle.download("pathname")

        # assert
        assert mock_content_get.call_count == 1
        assert mock_bundle_get.call_count == 1
        assert mock_bundle_download.call_count == 1
        mock_file.assert_called_once_with("pathname", "wb")

    @responses.activate
    def test_output_as_io(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        bundle_id = "101"
        path = get_path(
            f"v1/content/{content_guid}/bundles/{bundle_id}/download/bundle.tar.gz"
        )

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundle_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}",
            json=load_mock(
                f"v1/content/{content_guid}/bundles/{bundle_id}.json"
            ),
        )

        mock_bundle_download = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}/download",
            body=path.read_bytes(),
        )

        # setup
        c = Client("12345", "https://connect.example")
        bundle = c.content.get(content_guid).bundles.get(bundle_id)

        # invoke
        file = io.BytesIO()
        buffer = io.BufferedWriter(file)
        bundle.download(buffer)
        buffer.seek(0)

        # assert
        assert mock_content_get.call_count == 1
        assert mock_bundle_get.call_count == 1
        assert mock_bundle_download.call_count == 1
        assert file.read() == path.read_bytes()

    @responses.activate
    def test_invalid_arguments(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        bundle_id = "101"
        path = get_path(
            f"v1/content/{content_guid}/bundles/{bundle_id}/download/bundle.tar.gz"
        )

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundle_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}",
            json=load_mock(
                f"v1/content/{content_guid}/bundles/{bundle_id}.json"
            ),
        )

        mock_bundle_download = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}/download",
            body=path.read_bytes(),
        )

        # setup
        c = Client("12345", "https://connect.example")
        bundle = c.content.get(content_guid).bundles.get(bundle_id)

        # invoke
        with pytest.raises(TypeError):
            bundle.download(None)

        # assert
        assert mock_content_get.call_count == 1
        assert mock_bundle_get.call_count == 1


class TestBundlesCreate:
    @responses.activate
    def test(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        bundle_id = "101"
        pathname = get_path(
            f"v1/content/{content_guid}/bundles/{bundle_id}/download/bundle.tar.gz"
        )

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundle_post = responses.post(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles",
            json=load_mock(
                f"v1/content/{content_guid}/bundles/{bundle_id}.json"
            ),
        )

        # setup
        c = Client("12345", "https://connect.example")
        content = c.content.get(content_guid)

        # invoke
        data = pathname.read_bytes()
        bundle = content.bundles.create(data)

        # # assert
        assert bundle.id == "101"
        assert mock_content_get.call_count == 1
        assert mock_bundle_post.call_count == 1

    @responses.activate
    def test_kwargs_pathname(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        bundle_id = "101"
        pathname = get_path(
            f"v1/content/{content_guid}/bundles/{bundle_id}/download/bundle.tar.gz"
        )

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundle_post = responses.post(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles",
            json=load_mock(
                f"v1/content/{content_guid}/bundles/{bundle_id}.json"
            ),
        )

        # setup
        c = Client("12345", "https://connect.example")
        content = c.content.get(content_guid)

        # invoke
        pathname = str(pathname.absolute())
        bundle = content.bundles.create(pathname)

        # # assert
        assert bundle.id == "101"
        assert mock_content_get.call_count == 1
        assert mock_bundle_post.call_count == 1

    @responses.activate
    def test_invalid_arguments(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        # setup
        c = Client("12345", "https://connect.example")
        content = c.content.get(content_guid)

        # invoke
        with pytest.raises(TypeError):
            content.bundles.create(None)


class TestBundlesFind:
    @responses.activate
    def test(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundles_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles",
            json=load_mock(f"v1/content/{content_guid}/bundles.json"),
        )

        # setup
        c = Client("12345", "https://connect.example")

        # invoke
        bundles = c.content.get(content_guid).bundles.find()

        # assert
        assert mock_content_get.call_count == 1
        assert mock_bundles_get.call_count == 1
        assert len(bundles) == 1
        assert bundles[0].id == "101"


class TestBundlesFindOne:
    @responses.activate
    def test(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundles_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles",
            json=load_mock(f"v1/content/{content_guid}/bundles.json"),
        )

        # setup
        c = Client("12345", "https://connect.example")

        # invoke
        bundle = c.content.get(content_guid).bundles.find_one()

        # assert
        assert mock_content_get.call_count == 1
        assert mock_bundles_get.call_count == 1
        assert bundle.id == "101"


class TestBundlesGet:
    @responses.activate
    def test(self):
        content_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        bundle_id = "101"

        # behavior
        mock_content_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json=load_mock(f"v1/content/{content_guid}.json"),
        )

        mock_bundle_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/bundles/{bundle_id}",
            json=load_mock(
                f"v1/content/{content_guid}/bundles/{bundle_id}.json"
            ),
        )

        # setup
        c = Client("12345", "https://connect.example")

        # invoke
        bundle = c.content.get(content_guid).bundles.get(bundle_id)

        # assert
        assert mock_content_get.call_count == 1
        assert mock_bundle_get.call_count == 1
        assert bundle.id == bundle_id
