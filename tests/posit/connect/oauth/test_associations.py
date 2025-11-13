from unittest import mock

import responses

from posit.connect.client import Client
from posit.connect.oauth.associations import Association

from ..api import load_mock, load_mock_list


class TestAssociationAttributes:
    @classmethod
    def setup_class(cls):
        guid = "22644575-a27b-4118-ad06-e24459b05126"
        fake_items = load_mock_list(f"v1/oauth/integrations/{guid}/associations.json")

        assert len(fake_items) == 1
        fake_item = fake_items[0]

        cls.item = Association(mock.Mock(), **fake_item)

    def test_app_guid(self):
        assert self.item["app_guid"] == "f2f37341-e21d-3d80-c698-a935ad614066"

    def test_oauth_integration_guid(self):
        assert self.item["oauth_integration_guid"] == "22644575-a27b-4118-ad06-e24459b05126"

    def test_oauth_integration_name(self):
        assert self.item["oauth_integration_name"] == "keycloak integration"

    def test_oauth_integration_description(self):
        assert self.item["oauth_integration_description"] == "integration description"

    def test_oauth_integration_template(self):
        assert self.item["oauth_integration_template"] == "custom"

    def test_created_time(self):
        assert self.item["created_time"] == "2024-10-01T18:16:09Z"


class TestIntegrationAssociationsFind:
    @responses.activate
    def test(self):
        guid = "22644575-a27b-4118-ad06-e24459b05126"

        # behavior
        mock_get_integration = responses.get(
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}",
            json=load_mock(f"v1/oauth/integrations/{guid}.json"),
        )
        mock_get_association = responses.get(
            f"https://connect.example/__api__/v1/oauth/integrations/{guid}/associations",
            json=load_mock(f"v1/oauth/integrations/{guid}/associations.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        # invoke
        associations = c.oauth.integrations.get(guid).associations.find()

        assert len(associations) == 1
        association = associations[0]
        assert association["oauth_integration_guid"] == guid

        assert mock_get_integration.call_count == 1
        assert mock_get_association.call_count == 1


class TestContentAssociationsFind:
    @responses.activate
    def test(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get_content = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )
        mock_get_association = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}/oauth/integrations/associations",
            json=load_mock(f"v1/content/{guid}/oauth/integrations/associations.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        # invoke
        associations = c.content.get(guid).oauth.associations.find()

        # assert
        assert len(associations) == 2
        assert associations[0]["app_guid"] == guid
        assert associations[1]["app_guid"] == guid
        assert (
            associations[0]["oauth_integration_guid"] != associations[1]["oauth_integration_guid"]
        )

        assert mock_get_content.call_count == 1
        assert mock_get_association.call_count == 1


class TestContentAssociationsUpdate:
    @responses.activate
    def test(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get_content = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        new_integration_guid1 = "00000000-a27b-4118-ad06-e24459b05126"
        new_integration_guid2 = "00000001-a27b-4118-ad06-e24459b05126"

        mock_put = responses.put(
            f"https://connect.example/__api__/v1/content/{guid}/oauth/integrations/associations",
            json=[
                {"oauth_integration_guid": new_integration_guid1},
                {"oauth_integration_guid": new_integration_guid2},
            ],
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # invoke
        c.content.get(guid).oauth.associations.update(
            [
                new_integration_guid1,
                new_integration_guid2,
            ]
        )

        # assert
        assert mock_put.call_count == 1
        assert mock_get_content.call_count == 1

    @responses.activate
    def test_overload_str_type(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get_content = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        new_integration_guid = "00000000-a27b-4118-ad06-e24459b05126"

        mock_put = responses.put(
            f"https://connect.example/__api__/v1/content/{guid}/oauth/integrations/associations",
            json=[
                {"oauth_integration_guid": new_integration_guid},
            ],
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # invoke
        c.content.get(guid).oauth.associations.update(new_integration_guid)

        # assert
        assert mock_put.call_count == 1
        assert mock_get_content.call_count == 1


class TestContentAssociationsDelete:
    @responses.activate
    def test(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get_content = responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        mock_put = responses.put(
            f"https://connect.example/__api__/v1/content/{guid}/oauth/integrations/associations",
            json=[],
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None

        # invoke
        c.content.get(guid).oauth.associations.delete()

        # assert
        assert mock_put.call_count == 1
        assert mock_get_content.call_count == 1


class TestContentAssociationsFindBy:
    @responses.activate
    def test(self):
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{guid}/oauth/integrations/associations",
            json=load_mock(f"v1/content/{guid}/oauth/integrations/associations.json"),
        )

        # setup
        c = Client("https://connect.example", "12345")
        c._ctx.version = None
        associations = c.content.get(guid).oauth.associations

        # invoke and assert
        # by guid
        found = associations.find_by(guid="22644575-a27b-4118-ad06-e24459b05126")
        assert found is not None
        assert found["oauth_integration_guid"] == "22644575-a27b-4118-ad06-e24459b05126"

        # by name (exact match)
        found = associations.find_by(name="^keycloak integration$")
        assert found is not None
        assert found["oauth_integration_name"] == "keycloak integration"

        # by name (partial match) - should find first match
        found = associations.find_by(name="integration")
        assert found is not None
        assert found["oauth_integration_name"] == "keycloak integration"

        # by description (exact match)
        found = associations.find_by(description="^integration description$")
        assert found is not None
        assert found["oauth_integration_description"] == "integration description"

        # by description (partial match)
        found = associations.find_by(description="another")
        assert found is not None
        assert found["oauth_integration_description"] == "another description"

        # by integration_type
        found = associations.find_by(integration_type="custom")
        assert found is not None
        assert found["oauth_integration_template"] == "custom"
        assert found["oauth_integration_name"] == "keycloak integration"  # first one

        # by multiple criteria
        found = associations.find_by(integration_type="connect", name="another integration")
        assert found is not None
        assert found["oauth_integration_template"] == "connect"
        assert found["oauth_integration_name"] == "another integration"

        # no match
        found = associations.find_by(name="Non-existent Integration")
        assert found is None
