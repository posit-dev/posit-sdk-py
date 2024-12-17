import pytest
import responses
from responses import matchers

# from responses import matchers
from posit.connect.client import Client
from posit.connect.content import ContentItem
from posit.connect.tags import Tag

from .api import load_mock_dict, load_mock_list


class TestTags:
    @responses.activate
    def test_find_all_tags(self):
        """Check GET /v1/tags"""
        # behavior
        mock_get_tags = responses.get(
            "https://connect.example/__api__/v1/tags",
            json=load_mock_list("v1/tags.json"),
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        tags = client.tags.find()

        # assert
        assert mock_get_tags.call_count == 1
        assert len(tags) == 28

        for tag in tags:
            assert isinstance(tag, Tag)

    @responses.activate
    def test_find_tags_by_name(self):
        """Check GET /v1/tags?name=tag_name"""
        # behavior
        mock_get_tags = responses.get(
            "https://connect.example/__api__/v1/tags?name=academy",
            json=load_mock_list("v1/tags?name=academy.json"),
            match=[matchers.query_param_matcher({"name": "academy"})],
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        tags = client.tags.find(name="academy")

        # assert
        assert mock_get_tags.call_count == 1
        assert len(tags) == 1

        for tag in tags:
            assert isinstance(tag, Tag)

    @responses.activate
    def test_find_tags_by_parent(self):
        """Check GET /v1/tags?parent_id=3"""
        # behavior
        mock_get_tags = responses.get(
            "https://connect.example/__api__/v1/tags?parent_id=3",
            json=load_mock_list("v1/tags?parent_id=3.json"),
            match=[matchers.query_param_matcher({"parent_id": "3"})],
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        by_str_tags = client.tags.find(parent_id="3")
        parent_tag = Tag(client._ctx, "/v1/tags/3", id="3", name="Parent")
        by_tag_tags = client.tags.find(parent=parent_tag)

        # assert
        assert mock_get_tags.call_count == 2
        assert len(by_str_tags) == 7
        assert len(by_tag_tags) == 7

    @responses.activate
    def test_get(self):
        # behavior
        mock_get_tag = responses.get(
            "https://connect.example/__api__/v1/tags/33",
            json=load_mock_dict("v1/tags/33.json"),
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        tag = client.tags.get("33")

        # assert
        assert mock_get_tag.call_count == 1
        assert isinstance(tag, Tag)

    @responses.activate
    def test_create_tag(self):
        # behavior
        mock_create_tag = responses.post(
            "https://connect.example/__api__/v1/tags",
            json=load_mock_dict("v1/tags/33.json"),
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        tag = Tag(client._ctx, "/v1/tags/1", id="3", name="Tag")

        # invoke
        academy_tag_parent_id = client.tags.create(name="academy", parent_id=tag["id"])
        academy_tag_parent_tag = client.tags.create(name="academy", parent=tag)

        with pytest.raises(TypeError):
            client.tags.create(
                name="academy",
                parent="not a tag",  # pyright: ignore[reportArgumentType]
            )
        with pytest.raises(ValueError):
            client.tags.create(  # pyright: ignore[reportCallIssue]
                name="academy",
                parent=tag,
                parent_id="asdf",
            )

        # assert
        assert mock_create_tag.call_count == 2

        assert academy_tag_parent_id["id"] == "33"
        assert academy_tag_parent_tag["id"] == "33"


class TestTag:
    @responses.activate
    def test_parent(self):
        # behavior
        mock_get_3_tag = responses.get(
            "https://connect.example/__api__/v1/tags/3",
            json=load_mock_dict("v1/tags/3.json"),
        )
        mock_get_33_tag = responses.get(
            "https://connect.example/__api__/v1/tags/33",
            json=load_mock_dict("v1/tags/33.json"),
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        tag = client.tags.get("33")
        parent_tag = tag.parent_tag

        assert isinstance(parent_tag, Tag)
        parent_parent_tag = parent_tag.parent_tag

        # assert
        assert mock_get_3_tag.call_count == 1
        assert mock_get_33_tag.call_count == 1

        assert parent_parent_tag is None

    @responses.activate
    def test_children(self):
        # behavior
        mock_get_3_tag = responses.get(
            "https://connect.example/__api__/v1/tags/3",
            json=load_mock_dict("v1/tags/3.json"),
        )
        mock_parent_3_tags = responses.get(
            "https://connect.example/__api__/v1/tags",
            json=load_mock_list("v1/tags?parent_id=3.json"),
            match=[matchers.query_param_matcher({"parent_id": "3"})],
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        tag = client.tags.get("3")
        tag_children = tag.child_tags.find()

        # assert
        assert mock_get_3_tag.call_count == 1
        assert mock_parent_3_tags.call_count == 1

        assert len(tag_children) == 7

        for tag_child in tag_children:
            assert isinstance(tag_child, Tag)

    @responses.activate
    def test_descendants(self):
        # behavior
        mock_get_3_tag = responses.get(
            "https://connect.example/__api__/v1/tags/3",
            json=load_mock_dict("v1/tags/3.json"),
        )
        mock_all_tags = responses.get(
            "https://connect.example/__api__/v1/tags",
            json=load_mock_list("v1/tags.json"),
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        tag = client.tags.get("3")
        tag_children = tag.descendant_tags.find()

        # assert
        assert mock_get_3_tag.call_count == 1
        assert mock_all_tags.call_count == 1

        assert len(tag_children) == 21

        for tag_child in tag_children:
            assert isinstance(tag_child, Tag)

    @responses.activate
    def test_content_with_tag(self):
        # behavior
        mock_get_3_tag = responses.get(
            "https://connect.example/__api__/v1/tags/3/content",
            json=load_mock_list("v1/tags/3/content.json"),
        )
        mock_get_33_tag = responses.get(
            "https://connect.example/__api__/v1/tags/33/content",
            json=load_mock_list("v1/tags/33/content.json"),
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")
        tag3 = Tag(client._ctx, "/v1/tags/3", id="3", name="Tag3")
        tag33 = Tag(client._ctx, "/v1/tags/33", id="33", name="Tag33")

        # invoke
        tag3_content_items = tag3.content_items.find()
        tag33_content_items = tag33.content_items.find()

        # assert
        assert mock_get_3_tag.call_count == 1
        assert mock_get_33_tag.call_count == 1
        assert len(tag3_content_items) == 0
        assert len(tag33_content_items) == 5

        for content_item in tag33_content_items:
            assert isinstance(content_item, ContentItem)

    @responses.activate
    def test_destroy(self):
        # behavior
        mock_29_tag = responses.get(
            "https://connect.example/__api__/v1/tags/29",
            json=load_mock_dict("v1/tags/29.json"),
        )
        mock_29_destroy = responses.delete(
            "https://connect.example/__api__/v1/tags/29",
            json={},  # empty response
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        tag29 = client.tags.get("29")
        tag29.destroy()

        # assert
        assert mock_29_tag.call_count == 1
        assert mock_29_destroy.call_count == 1

    @responses.activate
    def test_update(self):
        # behavior
        mock_get_33_tag = responses.get(
            "https://connect.example/__api__/v1/tags/33",
            json=load_mock_dict("v1/tags/33.json"),
        )
        mock_update_33_tag = responses.patch(
            "https://connect.example/__api__/v1/tags/33",
            json=load_mock_dict("v1/tags/33-patched.json"),
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")
        tag33 = client.tags.get("33")

        # invoke
        tag33.update(name="academy-updated", parent_id=None)
        tag33.update(name="academy-updated", parent=None)

        parent_tag = Tag(client._ctx, "/v1/tags/1", id="42", name="Parent")
        tag33.update(name="academy-updated", parent=parent_tag)
        tag33.update(name="academy-updated", parent_id=parent_tag["id"])

        # assert
        assert mock_get_33_tag.call_count == 1
        assert mock_update_33_tag.call_count == 4

        # Asserting updated values are deferred to integration testing
        # to avoid agreening with the mocked data


class TestContentItemTags:
    @responses.activate
    def test_find(self):
        # behavior
        content_item_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        mock_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_item_guid}",
            json=load_mock_dict(f"v1/content/{content_item_guid}.json"),
        )
        mock_tags_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_item_guid}/tags",
            json=load_mock_list(f"v1/content/{content_item_guid}/tags.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")
        content_item = client.content.get(content_item_guid)

        # invoke
        tags = content_item.tags.find()

        # assert
        assert mock_get.call_count == 1
        assert mock_tags_get.call_count == 1
        assert len(tags) == 2

    @responses.activate
    def test_add(self):
        # behavior
        content_item_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        tag_id = "33"
        mock_content_item_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_item_guid}",
            json=load_mock_dict(f"v1/content/{content_item_guid}.json"),
        )
        mock_tag_get = responses.get(
            f"https://connect.example/__api__/v1/tags/{tag_id}",
            json=load_mock_dict(f"v1/tags/{tag_id}.json"),
        )
        mock_tags_add = responses.post(
            f"https://connect.example/__api__/v1/content/{content_item_guid}/tags",
            json={},  # empty response
        )

        # setup
        client = Client("https://connect.example", "12345")
        content_item = client.content.get(content_item_guid)

        sub_tag = client.tags.get("33")

        # invoke
        content_item.tags.add(sub_tag["id"])
        content_item.tags.add(sub_tag)

        with pytest.raises(TypeError):
            content_item.tags.add(
                123,  # pyright: ignore[reportArgumentType]
            )
        with pytest.raises(ValueError):
            content_item.tags.add("")

        # assert
        assert mock_content_item_get.call_count == 1
        assert mock_tag_get.call_count == 1
        assert mock_tags_add.call_count == 2

    @responses.activate
    def test_delete(self):
        # behavior
        content_item_guid = "f2f37341-e21d-3d80-c698-a935ad614066"
        tag_id = "33"
        mock_content_item_get = responses.get(
            f"https://connect.example/__api__/v1/content/{content_item_guid}",
            json=load_mock_dict(f"v1/content/{content_item_guid}.json"),
        )
        mock_tag_get = responses.get(
            f"https://connect.example/__api__/v1/tags/{tag_id}",
            json=load_mock_dict(f"v1/tags/{tag_id}.json"),
        )
        mock_tags_delete = responses.delete(
            f"https://connect.example/__api__/v1/content/{content_item_guid}/tags/{tag_id}",
            json={},  # empty response
        )

        # setup
        client = Client("https://connect.example", "12345")
        content_item = client.content.get(content_item_guid)

        sub_tag = client.tags.get("33")

        # invoke
        content_item.tags.delete(sub_tag["id"])
        content_item.tags.delete(sub_tag)

        with pytest.raises(TypeError):
            content_item.tags.delete(
                123,  # pyright: ignore[reportArgumentType]
            )
        with pytest.raises(ValueError):
            content_item.tags.delete("")

        # assert
        assert mock_content_item_get.call_count == 1
        assert mock_tag_get.call_count == 1
        assert mock_tags_delete.call_count == 2
