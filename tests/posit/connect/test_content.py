import responses

from responses import matchers

from posit.connect.client import Client
from posit.connect.content import ContentItem

from .api import load_mock  # type: ignore


class TestContent:
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
            match=[matchers.json_params_matcher({"name": fake_content_item["name"]})],
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example/")

        # invoke
        content_item = client.content.create(name=fake_content_item["name"])

        # assert
        assert content_item.name == fake_content_item["name"]


class TestContents:
    @responses.activate
    def test_get_all_content(self):
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )
        con = Client("12345", "https://connect.example")
        all_content = con.content.find()
        assert len(all_content) == 3
        assert [c.name for c in all_content] == [
            "team-admin-dashboard",
            "Performance-Data-1671216053560",
            "My-Streamlit-app",
        ]

    @responses.activate
    def test_content_find_one(self):
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )
        con = Client("12345", "https://connect.example")

        one = con.content.find_one()
        assert isinstance(one, ContentItem)
        assert one.name == "team-admin-dashboard"

    @responses.activate
    def test_content_get(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )
        con = Client("12345", "https://connect.example")
        get_one = con.content.get("f2f37341-e21d-3d80-c698-a935ad614066")
        assert get_one.name == "Performance-Data-1671216053560"

    @responses.activate
    def test_count(self):
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=load_mock("v1/content.json"),
        )
        con = Client(api_key="12345", url="https://connect.example/")
        count = con.content.count()
        assert count == 3
