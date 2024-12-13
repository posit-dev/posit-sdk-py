from unittest.mock import Mock

import responses
from responses.matchers import json_params_matcher

from posit import connect
from posit.connect.vanities import Vanities, Vanity, VanityMixin


class TestVanityDestroy:
    @responses.activate
    def test_destroy_sends_delete_request(self):
        content_guid = "8ce6eaca-60af-4c2f-93a0-f5f3cddf5ee5"
        base_url = "https://connect.example/__api__"
        endpoint = f"{base_url}/v1/content/{content_guid}/vanity"
        mock_delete = responses.delete(endpoint)

        c = connect.Client("https://connect.example", "12345")
        vanity = Vanity(c._ctx, content_guid=content_guid, path=Mock(), created_time=Mock())

        vanity.destroy()

        assert mock_delete.call_count == 1

    @responses.activate
    def test_destroy_calls_after_destroy_callback(self):
        content_guid = "8ce6eaca-60af-4c2f-93a0-f5f3cddf5ee5"
        base_url = "https://connect.example/__api__"
        endpoint = f"{base_url}/v1/content/{content_guid}/vanity"
        responses.delete(endpoint)

        c = connect.Client("https://connect.example", "12345")
        after_destroy = Mock()
        vanity = Vanity(
            c._ctx,
            after_destroy=after_destroy,
            content_guid=content_guid,
            path=Mock(),
            created_time=Mock(),
        )

        vanity.destroy()

        assert after_destroy.call_count == 1


class TestVanitiesAll:
    @responses.activate
    def test_all_sends_get_request(self):
        base_url = "https://connect.example/__api__"
        endpoint = f"{base_url}/v1/vanities"
        mock_get = responses.get(endpoint, json=[])

        c = connect.Client("https://connect.example", "12345")
        vanities = Vanities(c._ctx)

        vanities.all()

        assert mock_get.call_count == 1


class TestVanityMixin:
    @responses.activate
    def test_vanity_getter_returns_vanity(self):
        guid = "8ce6eaca-60af-4c2f-93a0-f5f3cddf5ee5"
        base_url = "https://connect.example/__api__"
        endpoint = f"{base_url}/v1/content/{guid}/vanity"
        mock_get = responses.get(endpoint, json={"content_guid": guid, "path": "my-dashboard"})

        c = connect.Client("https://connect.example", "12345")
        content = VanityMixin(c._ctx, guid=guid)

        assert content.vanity == "my-dashboard"
        assert mock_get.call_count == 1

    @responses.activate
    def test_vanity_setter_with_string(self):
        guid = "8ce6eaca-60af-4c2f-93a0-f5f3cddf5ee5"
        base_url = "https://connect.example/__api__"
        endpoint = f"{base_url}/v1/content/{guid}/vanity"
        path = "example"
        mock_put = responses.put(
            endpoint,
            json={"content_guid": guid, "path": path},
            match=[json_params_matcher({"path": path})],
        )

        c = connect.Client("https://connect.example", "12345")
        content = VanityMixin(c._ctx, guid=guid)
        content.vanity = path
        assert content.vanity == path

        assert mock_put.call_count == 1

    @responses.activate
    def test_vanity_deleter(self):
        guid = "8ce6eaca-60af-4c2f-93a0-f5f3cddf5ee5"
        base_url = "https://connect.example/__api__"
        endpoint = f"{base_url}/v1/content/{guid}/vanity"
        mock_delete = responses.delete(endpoint)

        c = connect.Client("https://connect.example", "12345")
        content = VanityMixin(c._ctx, guid=guid)
        content._vanity = Vanity(c._ctx, path=Mock(), content_guid=guid, created_time=Mock())
        del content.vanity

        assert content._vanity is None
        assert mock_delete.call_count == 1
