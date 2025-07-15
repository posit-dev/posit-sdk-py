import responses
from responses import matchers

from posit.connect.client import Client
from posit.connect.oauth import types

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
        assert len(integrations) == 3
        assert integrations[0]["id"] == "3"
        assert integrations[1]["id"] == "4"
        assert integrations[2]["id"] == "5"


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


class TestIntegrationsFindBy:
    @responses.activate
    def test(self):
        # behavior
        responses.get(
            "https://connect.example/__api__/v1/oauth/integrations",
            json=load_mock("v1/oauth/integrations.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        integrations = c.oauth.integrations

        # invoke and assert
        # by guid
        found = integrations.find_by(guid="22644575-a27b-4118-ad06-e24459b05126")
        assert found is not None
        assert found["guid"] == "22644575-a27b-4118-ad06-e24459b05126"

        # by name (exact match)
        found = integrations.find_by(name="^keycloak integration$")
        assert found is not None
        assert found["name"] == "keycloak integration"

        # by name (partial match) - should find first match
        found = integrations.find_by(name="keycloak")
        assert found is not None
        assert found["name"] == "keycloak integration"

        # by description (exact match)
        found = integrations.find_by(description="^integration description$")
        assert found is not None
        assert found["description"] == "integration description"

        # by description (partial match)
        found = integrations.find_by(description="another")
        assert found is not None
        assert found["description"] == "another integration description"

        # by integration_type
        found = integrations.find_by(integration_type=types.OAuthIntegrationType.CUSTOM)
        assert found is not None
        assert found["template"] == "custom"
        assert found["name"] == "keycloak integration"  # first one

        found = integrations.find_by(integration_type="custom")
        assert found is not None
        assert found["template"] == "custom"
        assert found["name"] == "keycloak integration"  # first one

        # by auth_type (no match)
        found = integrations.find_by(auth_type=types.OAuthIntegrationAuthType.VIEWER)
        assert found is None

        found = integrations.find_by(auth_type="Viewer")
        assert found is None

        # by config
        found = integrations.find_by(config={"client_id": "rsconnect-oidc"})
        assert found is not None
        assert found["config"]["client_id"] == "rsconnect-oidc"
        assert found["name"] == "keycloak integration"  # first one

        # by config to find second integration
        found = integrations.find_by(config={"token_endpoint_auth_method": "client_secret_post"})
        assert found is not None
        assert found["config"]["token_endpoint_auth_method"] == "client_secret_post"
        assert found["name"] == "keycloak-post"

        # by multiple criteria
        found = integrations.find_by(integration_type="custom", name="keycloak-post")
        assert found is not None
        assert found["template"] == "custom"
        assert found["name"] == "keycloak-post"

        # find connect integration
        found = integrations.find_by(integration_type=types.OAuthIntegrationType.CONNECT)
        assert found is not None
        assert found["template"] == "connect"
        assert found["name"] == "Connect Visitor API Key"

        found = integrations.find_by(integration_type="connect")
        assert found is not None
        assert found["template"] == "connect"
        assert found["name"] == "Connect Visitor API Key"

        found = integrations.find_by(name="Connect Visitor API Key")
        assert found is not None
        assert found["name"] == "Connect Visitor API Key"

        found = integrations.find_by(description="Allows access to Connect APIs")
        assert found is not None
        assert found["description"] == "Allows access to Connect APIs on behalf of a Connect user."

        found = integrations.find_by(config={"scopes": "admin"})
        assert found is not None
        assert found["config"]["scopes"] == "admin"

        # no match
        found = integrations.find_by(name="Non-existent Integration")
        assert found is None
