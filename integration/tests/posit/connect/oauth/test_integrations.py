import pytest
from packaging import version

from posit import connect

from .. import CONNECT_VERSION, fixtures


@pytest.mark.skipif(
    CONNECT_VERSION <= version.parse("2024.06.0"),
    reason="OAuth Integrations not supported.",
)
class TestIntegrations:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.integration = cls.client.oauth.integrations.create(
            name=fixtures.name(),
            description="integration description",
            template="custom",
            config={
                "auth_mode": "Confidential",
                "authorization_uri": "https://example.com/__tenand_id__/oauth2/v2.0/authorize",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "scopes": "a b c",
                "token_endpoint_auth_method": "client_secret_post",
                "token_uri": "https://example.com/__tenant_id__/oauth2/v2.0/token",
            },
        )

        cls.another_integration = cls.client.oauth.integrations.create(
            name=fixtures.name(),
            description="another integration description",
            template="custom",
            config={
                "auth_mode": "Confidential",
                "authorization_uri": "https://example.com/__tenand_id__/oauth2/v2.0/authorize",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "scopes": "a b c",
                "token_endpoint_auth_method": "client_secret_post",
                "token_uri": "https://example.com/__tenant_id__/oauth2/v2.0/token",
            },
        )

    def test_get(self):
        result = self.client.oauth.integrations.get(self.integration["guid"])
        assert result == self.integration

    def test_find(self):
        results = self.client.oauth.integrations.find()
        assert len(results) >= 2
        integration_guids = {integration["guid"] for integration in results}
        assert self.integration["guid"] in integration_guids
        assert self.another_integration["guid"] in integration_guids

    def test_create_update_delete(self):
        # create a new integration
        integration = self.client.oauth.integrations.create(
            name=fixtures.name(),
            description="new integration description",
            template="custom",
            config={
                "auth_mode": "Confidential",
                "authorization_uri": "https://example.com/__tenand_id__/oauth2/v2.0/authorize",
                "client_id": "client_id",
                "client_secret": "client_secret",
                "scopes": "a b c",
                "token_endpoint_auth_method": "client_secret_post",
                "token_uri": "https://example.com/__tenant_id__/oauth2/v2.0/token",
            },
        )

        created = self.client.oauth.integrations.get(integration["guid"])
        assert created == integration

        all_integrations = self.client.oauth.integrations.find()
        assert len(all_integrations) >= 3

        # update the new integration

        created.update(name="updated integration name")
        updated = self.client.oauth.integrations.get(integration["guid"])
        assert updated["name"] == "updated integration name"

        # delete the new integration

        created.delete()
        all_integrations_after_delete = self.client.oauth.integrations.find()
        assert len(all_integrations_after_delete) == len(all_integrations) - 1
