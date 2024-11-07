import pytest
import responses

from posit.connect.client import Client

from .api import load_mock  # type: ignore


class TestPackagesMixin:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/packages",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066/packages.json"),
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        content._ctx.version = None
        assert len(content.packages) == 1


class TestPackagesFind:
    @responses.activate
    def test(self):
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        with pytest.raises(NotImplementedError):
            c.packages.find("posit")


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
