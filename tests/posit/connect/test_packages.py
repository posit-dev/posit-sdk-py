import responses

from posit.connect.client import Client

from .api import load_mock


class TestPackagesFindBy:
    @responses.activate
    def test(self):
        mock_get = responses.get(
            "https://connect.example/__api__/v1/packages",
            json=load_mock("v1/packages.json"),
        )

        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        package = c.packages.find_by(name="posit")
        assert package
        assert package["name"] == "posit"
        assert mock_get.call_count == 1

    @responses.activate
    def test_with_content_fields(self):
        mock_get = responses.get(
            "https://connect.example/__api__/v1/packages",
            json=load_mock("v1/packages.json"),
        )

        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # Test with content_id and content_guid (new fields)
        package = c.packages.find_by(name="posit", content_id="123", content_guid="abcd-1234")
        assert package
        assert package["name"] == "posit"
        assert mock_get.call_count == 1

        # Test with app_id and app_guid (deprecated fields)
        package = c.packages.find_by(name="posit", app_id="123", app_guid="abcd-1234")
        assert package
        assert package["name"] == "posit"
        assert mock_get.call_count == 2
