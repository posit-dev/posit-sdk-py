import responses

from posit.connect.client import Client
from posit.connect.storage import (
    ContentStorageDetail,
    ContentStorageItem,
    ServerStorage,
)

from .api import load_mock_dict


class TestSystemStorage:
    @responses.activate
    def test_storage(self):
        mock_get = responses.get(
            "https://connect.example/__api__/v1/system/storage",
            json=load_mock_dict("v1/system/storage.json"),
        )

        client = Client("https://connect.example", "12345")
        client._ctx.version = None

        storage = client.system.storage

        assert isinstance(storage, ServerStorage)
        assert storage["bundles"]["count"] == 12
        assert storage["bundles"]["content_count"] == 4
        assert storage["bundles"]["bytes_total"] == 1048576
        assert mock_get.call_count == 1


class TestContentStorage:
    @responses.activate
    def test_find(self):
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content/storage",
            json=load_mock_dict("v1/content/storage.json"),
        )

        client = Client("https://connect.example", "12345")
        client._ctx.version = None

        items = client.content.storage.find()

        assert len(items) == 2
        for item in items:
            assert isinstance(item, ContentStorageItem)
        assert items[0]["content_name"] == "example-shiny-app"
        assert items[0]["bundles"]["bytes_total"] == 524288
        assert items[1]["content_title"] is None
        assert mock_get.call_count == 1

    @responses.activate
    def test_find_paginates_all_pages(self):
        mock_page1 = responses.get(
            "https://connect.example/__api__/v1/content/storage",
            json=load_mock_dict("v1/content/storage-page1.json"),
            match=[responses.matchers.query_param_matcher({"page_number": 1, "page_size": 500})],
        )
        mock_page2 = responses.get(
            "https://connect.example/__api__/v1/content/storage",
            json=load_mock_dict("v1/content/storage-page2.json"),
            match=[responses.matchers.query_param_matcher({"page_number": 2, "page_size": 500})],
        )

        client = Client("https://connect.example", "12345")
        client._ctx.version = None

        items = client.content.storage.find()

        # Results from both pages are concatenated, in page order.
        assert len(items) == 2
        assert items[0]["content_guid"] == "f2f37341-e21d-3d80-c698-a935ad614066"
        assert items[1]["content_guid"] == "8f9e2c9b-1a3d-4e5f-9c8e-1f2b3c4d5e6f"
        assert mock_page1.call_count == 1
        assert mock_page2.call_count == 1

    @responses.activate
    def test_find_with_sort_and_order(self):
        mock_get = responses.get(
            "https://connect.example/__api__/v1/content/storage",
            json=load_mock_dict("v1/content/storage.json"),
            match=[
                responses.matchers.query_param_matcher(
                    {
                        "sort": "bytes_total",
                        "order": "desc",
                        "page_number": 1,
                        "page_size": 500,
                    }
                )
            ],
        )

        client = Client("https://connect.example", "12345")
        client._ctx.version = None

        items = client.content.storage.find(sort="bytes_total", order="desc")

        assert len(items) == 2
        assert mock_get.call_count == 1


class TestContentItemStorage:
    @responses.activate
    def test_find(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        mock_get_content = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock_dict(f"v1/content/{guid}.json"),
        )
        mock_get_storage = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}/storage",
            json=load_mock_dict(f"v1/content/{guid}/storage.json"),
        )

        client = Client("https://connect.example", "12345")
        client._ctx.version = None

        content = client.content.get(guid)
        storage = content.storage

        assert isinstance(storage, ContentStorageDetail)
        assert storage["content_guid"] == guid
        assert storage["bundle_count"] == 3
        assert len(storage["bundles"]) == 3
        assert storage["bundles"][0]["is_active"] is True
        assert mock_get_content.call_count == 1
        assert mock_get_storage.call_count == 1
