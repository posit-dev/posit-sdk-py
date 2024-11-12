import responses
from responses import matchers

from posit.connect.client import Client

from ..api import load_mock, load_mock_dict


class TestIntegrationDelete:
    @responses.activate
    def test(self):
        guid = "22644575-a27b-4118-ad06-e24459b05126"

        # behavior
        responses.get(
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}",
            json=load_mock(f"v1/oauth/integrations/{guid}.json"),
        )

        mock_delete = responses.delete(
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}",
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        integration = c.oauth.integrations.get(guid)

        # invoke
        integration.delete()

        # assert
        assert mock_delete.call_count == 1


class TestIntegrationUpdate:
    @responses.activate
    def test(self):
        # data
        guid = "22644575-a27b-4118-ad06-e24459b05126"
        responses.get(
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}",
            json=load_mock(f"v1/oauth/integrations/{guid}.json"),
        )

        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        integration = c.oauth.integrations.get(guid)
        assert integration["guid"] == guid

        new_name = "New Name"

        fake_integration = load_mock_dict(f"v1/oauth/integrations/{guid}.json")
        fake_integration.update(name=new_name)
        assert fake_integration["name"] == new_name

        mock_update = responses.patch(
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}",
            json=fake_integration,
        )

        integration.update(name=new_name)
        assert mock_update.call_count == 1
        assert integration["name"] == new_name


class TestIntegrationsCreate:
    @responses.activate
    def test(self):
        # data
        guid = "22644575-a27b-4118-ad06-e24459b05126"
        fake_integration = load_mock_dict(f"v1/oauth/integrations/{guid}.json")

        # behavior
        mock_create = responses.post(
            "https://connect.example/__api__/v1/oauth/integrations",
            json=load_mock(f"v1/oauth/integrations/{guid}.json"),
            match=[
                matchers.json_params_matcher(
                    {
                        "name": fake_integration["name"],
                        "description": fake_integration["description"],
                        "template": fake_integration["template"],
                        "config": fake_integration["config"],
                    },
                ),
            ],
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # invoke
        integration = c.oauth.integrations.create(
            name=fake_integration["name"],
            description=fake_integration["description"],
            template=fake_integration["template"],
            config=fake_integration["config"],
        )

        # assert
        assert mock_create.call_count == 1
        assert integration["name"] == fake_integration["name"]
        assert integration["description"] == fake_integration["description"]
        assert integration["template"] == fake_integration["template"]
        assert integration["config"] == fake_integration["config"]


class TestIntegrationsFind:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/oauth/integrations",
            json=load_mock("v1/oauth/integrations.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # invoke
        integrations = c.oauth.integrations.find()

        # assert
        assert mock_get.call_count == 1
        assert len(integrations) == 2
        assert integrations[0]["id"] == "3"
        assert integrations[1]["id"] == "4"


class TestIntegrationsGet:
    @responses.activate
    def test(self):
        guid = "22644575-a27b-4118-ad06-e24459b05126"

        # behavior
        mock_get = responses.get(
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}",
            json=load_mock(f"v1/oauth/integrations/{guid}.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        integration = c.oauth.integrations.get(guid)

        assert mock_get.call_count == 1
        assert integration["guid"] == guid
