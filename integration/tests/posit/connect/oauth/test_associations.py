from pathlib import Path

import pytest
from packaging import version

from posit import connect

from .. import CONNECT_VERSION


@pytest.mark.skipif(
    CONNECT_VERSION <= version.parse("2024.06.0"),
    reason="OAuth Integrations not supported.",
)
class TestAssociations:
    @classmethod
    def setup_class(cls):
        cls.client = connect.Client()
        cls.integration = cls.client.oauth.integrations.create(
            name="example integration",
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
            name="another example integration",
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

        # create content
        # requires full bundle deployment to produce an interactive content type
        cls.content = cls.client.content.create(name="example-flask-minimal")
        # create bundle
        path = Path("../../../../resources/connect/bundles/example-flask-minimal/bundle.tar.gz")
        path = (Path(__file__).parent / path).resolve()
        bundle = cls.content.bundles.create(str(path))
        # deploy bundle
        task = bundle.deploy()
        task.wait_for()

        cls.content.oauth.associations.update(cls.integration["guid"])

    @classmethod
    def teardown_class(cls):
        cls.integration.delete()
        cls.another_integration.delete()
        assert len(cls.client.oauth.integrations.find()) == 0

        cls.content.delete()
        assert cls.client.content.count() == 0

    def test_find_by_integration(self):
        associations = self.integration.associations.find()
        assert len(associations) == 1
        assert associations[0]["oauth_integration_guid"] == self.integration["guid"]

        no_associations = self.another_integration.associations.find()
        assert len(no_associations) == 0

    def test_find_update_by_content(self):
        associations = self.content.oauth.associations.find()
        assert len(associations) == 1
        assert associations[0]["app_guid"] == self.content["guid"]
        assert associations[0]["oauth_integration_guid"] == self.integration["guid"]

        # update content association to another_integration
        self.content.oauth.associations.update(self.another_integration["guid"])
        updated_associations = self.content.oauth.associations.find()
        assert len(updated_associations) == 1
        assert updated_associations[0]["app_guid"] == self.content["guid"]
        assert (
            updated_associations[0]["oauth_integration_guid"] == self.another_integration["guid"]
        )

        # unset content association
        self.content.oauth.associations.delete()
        no_associations = self.content.oauth.associations.find()
        assert len(no_associations) == 0
