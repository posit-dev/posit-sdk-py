import responses

from posit.connect.client import Client

from .api import load_mock


class TestEnvironmentsFind:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce",
            json=load_mock(
                "v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce.json",
            ),
        )
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        environment = c.environments.find("25438b83-ea6d-4839-ae8e-53c52ac5f9ce")
        assert environment["id"] == "314"


class TestEnvironmentsFindBy:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/environments",
            json=load_mock(
                "v1/environments.json",
            ),
        )
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        environment = c.environments.find_by(id="314")
        assert environment
        assert environment["id"] == "314"


class TestEnvironmentsCreate:
    @responses.activate
    def test(self):
        responses.post(
            "https://connect.example/__api__/v1/environments",
            json=load_mock(
                "v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce.json",
            ),
        )
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        environment = c.environments.create(
            title="Project Alpha (R 4.1.1, Python 3.10)", name="", cluster_name=""
        )
        assert environment
        assert environment["id"] == "314"


class TestEnvironmentDestroy:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce",
            json=load_mock(
                "v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce.json",
            ),
        )

        mock_delete = responses.delete(
            "https://connect.example/__api__/v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce",
        )

        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        environment = c.environments.find("25438b83-ea6d-4839-ae8e-53c52ac5f9ce")
        assert environment["id"] == "314"

        environment.destroy()
        assert mock_delete.call_count == 1


class TestEnvironmentUpdate:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce",
            json=load_mock(
                "v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce.json",
            ),
        )

        mock_put = responses.put(
            "https://connect.example/__api__/v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce",
            json=load_mock(
                "v1/environments/25438b83-ea6d-4839-ae8e-53c52ac5f9ce.json",
            ),
        )

        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        environment = c.environments.find("25438b83-ea6d-4839-ae8e-53c52ac5f9ce")
        assert environment["id"] == "314"

        environment.update(title="test")
        assert mock_put.call_count == 1
