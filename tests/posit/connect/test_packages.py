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
