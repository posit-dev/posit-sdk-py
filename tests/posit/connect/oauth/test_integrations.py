from unittest import mock

import responses
from responses import matchers

from posit.connect.client import Client
from posit.connect.oauth.associations import IntegrationAssociations
from posit.connect.oauth.integrations import Integration

from ..api import load_mock  # type: ignore


class TestIntegrationAttributes:
    @classmethod
    def setup_class(cls):
        guid = "22644575-a27b-4118-ad06-e24459b05126"
        fake_item = load_mock(f"v1/oauth/integrations/{guid}.json")
        cls.item = Integration(mock.Mock(), **fake_item)

    def test_id(self):
        assert self.item.id == "3"

    def test_guid(self):
        assert self.item.guid == "22644575-a27b-4118-ad06-e24459b05126"

    def test_name(self):
        assert self.item.name == "keycloak integration"

    def test_description(self):
        assert self.item.description == "integration description"

    def test_template(self):
        assert self.item.template == "custom"

    def test_config(self):
        assert self.item.config["auth_mode"] == "Confidential"
        assert (
            self.item.config["authorization_uri"]
            == "http://keycloak:8080/realms/rsconnect/protocol/openid-connect/auth"
        )
        assert self.item.config["client_id"] == "rsconnect-oidc"
        assert self.item.config["scopes"] == "email"
        assert self.item.config["token_endpoint_auth_method"] == "client_secret_basic"
        assert (
            self.item.config["token_uri"]
            == "http://keycloak:8080/realms/rsconnect/protocol/openid-connect/token"
        )

    def test_created_time(self):
        assert self.item.created_time == "2024-07-16T19:28:05Z"

    def test_updated_time(self):
        assert self.item.updated_time == "2024-07-17T19:28:05Z"

    def test_associations(self):
        assert isinstance(self.item.associations, IntegrationAssociations)


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
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}"
        )

        # setup
        c = Client("https://connect.example", "12345")
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
        integration = c.oauth.integrations.get(guid)
        assert integration.guid == guid

        new_name = "New Name"

        fake_integration = load_mock(f"v1/oauth/integrations/{guid}.json")
        fake_integration.update(name=new_name)
        assert fake_integration["name"] == new_name

        mock_update = responses.patch(
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}",
            json=fake_integration,
        )

        integration.update(name=new_name)
        assert mock_update.call_count == 1
        assert integration.name == new_name


class TestIntegrationsCreate:
    @responses.activate
    def test(self):
        # data
        guid = "22644575-a27b-4118-ad06-e24459b05126"
        fake_integration = load_mock(f"v1/oauth/integrations/{guid}.json")

        # behavior
        mock_create = responses.post(
            f"https://connect.example/__api__/v1/oauth/integrations",
            json=load_mock(f"v1/oauth/integrations/{guid}.json"),
            match=[
                matchers.json_params_matcher(
                    {
                        "name": fake_integration["name"],
                        "description": fake_integration["description"],
                        "template": fake_integration["template"],
                        "config": fake_integration["config"],
                    }
                )
            ],
        )

        # setup
        c = Client("https://connect.example", "12345")

        # invoke
        integration = c.oauth.integrations.create(
            name=fake_integration["name"],
            description=fake_integration["description"],
            template=fake_integration["template"],
            config=fake_integration["config"],
        )

        # assert
        assert mock_create.call_count == 1
        assert integration.name == fake_integration["name"]
        assert integration.description == fake_integration["description"]
        assert integration.template == fake_integration["template"]
        assert integration.config == fake_integration["config"]


class TestIntegrationsFind:
    @responses.activate
    def test(self):
        # behavior
        mock_get = responses.get(
            "https://connect.example/__api__/v1/oauth/integrations",
            json=load_mock("v1/oauth/integrations.json"),
        )

        # setup
        client = Client("https://connect.example", "12345")

        # invoke
        integrations = client.oauth.integrations.find()

        # assert
        assert mock_get.call_count == 1
        assert len(integrations) == 2
        assert integrations[0].id == "3"
        assert integrations[1].id == "4"


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
        integration = c.oauth.integrations.get(guid)

        assert mock_get.call_count == 1
        assert integration.guid == guid
