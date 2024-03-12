import responses

from posit.connect.client import Client

from .api import load_mock  # type: ignore


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

        one = con.content.find_one(lambda c: c.title == "Performance Data")
        assert one.name == "Performance-Data-1671216053560"

        # Test find_one doesn't find any
        assert con.content.find_one(lambda c: c.title == "Does not exist") is None

    @responses.activate
    def test_content_get(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )
        con = Client("12345", "https://connect.example")
        get_one = con.content.get("f2f37341-e21d-3d80-c698-a935ad614066")
        assert get_one.name == "Performance-Data-1671216053560"
