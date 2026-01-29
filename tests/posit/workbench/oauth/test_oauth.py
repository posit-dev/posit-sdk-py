"""Tests for Workbench OAuth functionality."""

from datetime import datetime
from unittest.mock import patch

import pytest
import responses

from posit.workbench import Client

# Valid RPC cookie format: value|expiry_date
TEST_RPC_COOKIE = "test-cookie-value|Mon%2C%2001%20Jan%202030%2000%3A00%3A00%20GMT"


class TestGetCredentials:
    """Tests for the existing get_credentials method."""

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_credentials_success(self):
        """Test successful credential retrieval."""
        integration_id = "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6"

        responses.get(
            "https://workbench.example.com/oauth_token",
            json={
                "access_token": "token123",
                "expiry": "2025-12-31T23:59:59+00:00",
            },
        )

        client = Client()
        credentials = client.oauth.get_credentials(integration_id)

        assert credentials is not None
        assert credentials["access_token"] == "token123"
        assert credentials["integration_id"] == integration_id
        assert isinstance(credentials["expiry"], datetime)

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_credentials_error(self):
        """Test error handling in credential retrieval."""
        responses.get(
            "https://workbench.example.com/oauth_token",
            json={"error": "Integration not found"},
        )

        client = Client()

        with pytest.raises(RuntimeError, match="Integration not found"):
            client.oauth.get_credentials("invalid-id")

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_credentials_not_found(self):
        """Test when credentials are not available."""
        responses.get(
            "https://workbench.example.com/oauth_token",
            json={},  # Empty response, no access_token
        )

        client = Client()
        credentials = client.oauth.get_credentials("some-id")

        assert credentials is None

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_credentials_with_z_timezone(self):
        """Test credential retrieval with 'Z' timezone suffix."""
        integration_id = "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6"

        responses.get(
            "https://workbench.example.com/oauth_token",
            json={
                "access_token": "token456",
                "expiry": "2025-12-31T23:59:59Z",
            },
        )

        client = Client()
        credentials = client.oauth.get_credentials(integration_id)

        assert credentials is not None
        assert credentials["access_token"] == "token456"
        assert credentials["integration_id"] == integration_id
        assert isinstance(credentials["expiry"], datetime)
        # Verify the datetime was parsed correctly
        assert credentials["expiry"].year == 2025
        assert credentials["expiry"].month == 12
        assert credentials["expiry"].day == 31


class TestIntegrations:
    """Tests for integrations resource."""

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_find_success(self):
        """Test successful retrieval of integrations list."""
        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={
                "providers": [
                    {
                        "type": "custom",
                        "integrations": [
                            {
                                "type": "custom",
                                "name": "github-main",
                                "display_name": "GitHub",
                                "client_id": "client123",
                                "auth_url": "https://github.com/login/oauth/authorize",
                                "token_url": "https://github.com/login/oauth/access_token",
                                "scopes": ["read:user", "user:email"],
                                "issuer": "https://github.com",
                                "authenticated": True,
                                "uid": "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6",
                            },
                            {
                                "type": "custom",
                                "name": "azure-ad",
                                "display_name": "Azure AD",
                                "client_id": "azure-client-id",
                                "auth_url": "https://login.microsoftonline.com/authorize",
                                "token_url": "https://login.microsoftonline.com/token",
                                "scopes": ["openid", "profile"],
                                "issuer": "https://login.microsoftonline.com",
                                "authenticated": False,
                                "uid": "b2c3d4e5-6f7g-8h9i-0j1k-l2m3n4o5p6q7",
                            },
                        ],
                    }
                ]
            },
        )

        client = Client()
        integrations = client.oauth.integrations.find()

        assert len(integrations) == 2
        assert integrations[0]["type"] == "custom"
        assert integrations[0]["name"] == "github-main"
        assert integrations[0]["guid"] == "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6"
        assert integrations[0]["authenticated"] is True
        assert integrations[1]["type"] == "custom"
        assert integrations[1]["name"] == "azure-ad"
        assert integrations[1]["guid"] == "b2c3d4e5-6f7g-8h9i-0j1k-l2m3n4o5p6q7"
        assert integrations[1]["authenticated"] is False

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_find_empty(self):
        """Test when no integrations are configured."""
        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={"providers": []},
        )

        client = Client()
        integrations = client.oauth.integrations.find()

        assert integrations == []

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_find_error(self):
        """Test error handling in integrations retrieval."""
        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={"error": "Unauthorized access"},
        )

        client = Client()

        with pytest.raises(RuntimeError, match="Unauthorized access"):
            client.oauth.integrations.find()


class TestIntegrationsGetAndFindBy:
    """Tests for get() and find_by() methods."""

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_found(self):
        """Test successful retrieval of specific integration by GUID."""
        target_guid = "a1b2c3d4-5e6f-7g8h-9i0j-k1l2m3n4o5p6"

        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={
                "providers": [
                    {
                        "type": "custom",
                        "integrations": [
                            {
                                "type": "custom",
                                "name": "github-main",
                                "display_name": "GitHub",
                                "client_id": "client123",
                                "auth_url": "https://github.com/login/oauth/authorize",
                                "token_url": "https://github.com/login/oauth/access_token",
                                "scopes": ["read:user"],
                                "issuer": "https://github.com",
                                "authenticated": True,
                                "uid": target_guid,
                            },
                        ],
                    }
                ]
            },
        )

        client = Client()
        integration = client.oauth.integrations.get(target_guid)

        assert integration is not None
        assert integration["guid"] == target_guid
        assert integration["type"] == "custom"
        assert integration["display_name"] == "GitHub"

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_not_found(self):
        """Test when integration with given GUID doesn't exist."""
        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={"providers": []},
        )

        client = Client()
        integration = client.oauth.integrations.get("nonexistent-guid")

        assert integration is None

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    def test_get_invalid_guid(self):
        """Test validation of guid parameter."""
        client = Client()

        with pytest.raises(ValueError, match="non-empty string"):
            client.oauth.integrations.get("")

        with pytest.raises(ValueError, match="non-empty string"):
            client.oauth.integrations.get(None)  # type: ignore

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_find_by_name_pattern(self):
        """Test finding integration by name pattern."""
        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={
                "providers": [
                    {
                        "type": "custom",
                        "integrations": [
                            {
                                "type": "custom",
                                "name": "github-main",
                                "display_name": "GitHub",
                                "client_id": "client123",
                                "auth_url": "https://github.com/login/oauth/authorize",
                                "token_url": "https://github.com/login/oauth/access_token",
                                "scopes": ["read:user"],
                                "issuer": "https://github.com",
                                "authenticated": True,
                                "uid": "guid-1",
                            },
                        ],
                    }
                ]
            },
        )

        client = Client()
        integration = client.oauth.integrations.find_by(name="^github.*")

        assert integration is not None
        assert integration["name"] == "github-main"

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_find_by_authenticated(self):
        """Test finding integration by authenticated status."""
        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={
                "providers": [
                    {
                        "type": "custom",
                        "integrations": [
                            {
                                "type": "github",
                                "name": "github-main",
                                "display_name": "GitHub",
                                "client_id": "client123",
                                "auth_url": "https://github.com/login/oauth/authorize",
                                "token_url": "https://github.com/login/oauth/access_token",
                                "scopes": ["read:user"],
                                "issuer": "https://github.com",
                                "authenticated": True,
                                "uid": "guid-1",
                            },
                            {
                                "type": "azure",
                                "name": "azure-ad",
                                "display_name": "Azure AD",
                                "client_id": "azure-client-id",
                                "auth_url": "https://login.microsoftonline.com/authorize",
                                "token_url": "https://login.microsoftonline.com/token",
                                "scopes": ["openid", "profile"],
                                "issuer": "https://login.microsoftonline.com",
                                "authenticated": False,
                                "uid": "guid-2",
                            },
                        ],
                    }
                ]
            },
        )

        client = Client()
        integration = client.oauth.integrations.find_by(authenticated=True)

        assert integration is not None
        assert integration["authenticated"] is True
        assert integration["type"] == "github"

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_find_by_multiple_criteria(self):
        """Test finding integration with multiple criteria."""
        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={
                "providers": [
                    {
                        "type": "custom",
                        "integrations": [
                            {
                                "type": "github",
                                "name": "github-main",
                                "display_name": "GitHub",
                                "client_id": "client123",
                                "auth_url": "https://github.com/login/oauth/authorize",
                                "token_url": "https://github.com/login/oauth/access_token",
                                "scopes": ["read:user"],
                                "issuer": "https://github.com",
                                "authenticated": True,
                                "uid": "guid-1",
                            },
                        ],
                    }
                ]
            },
        )

        client = Client()
        integration = client.oauth.integrations.find_by(name="github.*", authenticated=True)

        assert integration is not None
        assert integration["name"] == "github-main"
        assert integration["authenticated"] is True


class TestGetDelegatedAzureToken:
    """Tests for get_delegated_azure_token method."""

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_delegated_azure_token_success(self):
        """Test successful Azure token retrieval."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={
                "result": True,
                "token": {
                    "access_token": "azure-token-xyz",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "scope": "https://management.azure.com/.default",
                    "ext_expires_in": 7200,
                },
            },
        )

        client = Client()
        token = client.oauth.get_delegated_azure_token("https://management.azure.com/")

        assert token["access_token"] == "azure-token-xyz"
        assert token["token_type"] == "Bearer"
        assert token["expires_in"] == 3600
        assert token.get("scope") == "https://management.azure.com/.default"
        assert token.get("ext_expires_in") == 7200

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_delegated_azure_token_minimal_response(self):
        """Test Azure token with only required fields."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={
                "result": True,
                "token": {
                    "access_token": "azure-token-xyz",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            },
        )

        client = Client()
        token = client.oauth.get_delegated_azure_token("https://storage.azure.com/")

        assert token["access_token"] == "azure-token-xyz"
        assert token["token_type"] == "Bearer"
        assert token["expires_in"] == 3600

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_delegated_azure_token_with_id_token(self):
        """Test Azure token response includes id_token when OIDC scopes requested."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={
                "result": True,
                "token": {
                    "access_token": "azure-token-xyz",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                    "id_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "scope": "openid profile https://graph.microsoft.com/.default",
                },
            },
        )

        client = Client()
        token = client.oauth.get_delegated_azure_token("https://graph.microsoft.com/")

        assert token["access_token"] == "azure-token-xyz"
        assert token["token_type"] == "Bearer"
        assert token["expires_in"] == 3600
        assert token.get("id_token") == "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."
        assert token.get("scope") == "openid profile https://graph.microsoft.com/.default"

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_delegated_azure_token_error(self):
        """Test error handling for Azure token."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={"error": "Azure AD not configured"},
        )

        client = Client()

        with pytest.raises(RuntimeError, match="Azure AD not configured"):
            client.oauth.get_delegated_azure_token("https://management.azure.com/")

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_delegated_azure_token_missing_token_field(self):
        """Test handling of response missing token field."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={"result": True},  # Missing token field
        )

        client = Client()

        with pytest.raises(RuntimeError, match="missing 'token' field"):
            client.oauth.get_delegated_azure_token("https://management.azure.com/")

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_delegated_azure_token_invalid_response(self):
        """Test handling of malformed response."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={
                "result": True,
                "token": {"some_field": "value"},  # Missing required fields
            },
        )

        client = Client()

        with pytest.raises(RuntimeError, match="missing required token fields"):
            client.oauth.get_delegated_azure_token("https://management.azure.com/")

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    def test_get_delegated_azure_token_invalid_resource(self):
        """Test validation of resource parameter."""
        client = Client()

        with pytest.raises(ValueError, match="non-empty string"):
            client.oauth.get_delegated_azure_token("")

        with pytest.raises(ValueError, match="non-empty string"):
            client.oauth.get_delegated_azure_token(None)  # type: ignore

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_delegated_azure_token_oauth2_error(self):
        """Test OAuth2 error handling for Azure token."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={
                "oauth2_error": {
                    "error": "unauthorized_client",
                    "error_description": "The client is not authorized to request a token using this method",
                }
            },
        )

        client = Client()

        with pytest.raises(
            RuntimeError,
            match="OAuth2 error retrieving Azure delegated token: unauthorized_client - The client is not authorized to request a token using this method",
        ):
            client.oauth.get_delegated_azure_token("https://management.azure.com/")

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.12.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_get_delegated_azure_token_oauth2_error_partial(self):
        """Test OAuth2 error with only error code provided."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={"oauth2_error": {"error": "access_denied"}},
        )

        client = Client()

        with pytest.raises(
            RuntimeError,
            match="OAuth2 error retrieving Azure delegated token: access_denied - no description",
        ):
            client.oauth.get_delegated_azure_token("https://management.azure.com/")


class TestVersionRequirements:
    """Tests for version requirement enforcement."""

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2025.12.0",  # Too old for OAuth integrations
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    def test_oauth_integrations_version_check(self):
        """Test that oauth integrations enforce version requirement."""
        client = Client()

        with pytest.raises(RuntimeError, match="2026.01.0"):
            _ = client.oauth.integrations.find()

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.11.0",  # Too old for Azure token
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    def test_azure_token_version_check(self):
        """Test that get_delegated_azure_token enforces its version."""
        client = Client()

        with pytest.raises(RuntimeError, match="2024.12.0"):
            client.oauth.get_delegated_azure_token("https://management.azure.com/")

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2025.11.0-dev",  # Dev version should skip check
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_dev_version_skips_check(self):
        """Test that dev versions skip version checks."""
        responses.get(
            "https://workbench.example.com/oauth_integrations",
            json={"providers": []},
        )

        client = Client()
        # Should not raise even though this would be considered < 2026.01.0
        integrations = client.oauth.integrations.find()
        assert integrations == []

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://workbench.example.com",
            "RSTUDIO_VERSION": "2024.11.0-dev+123",  # Dev version should skip check
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_dev_version_with_build_number_skips_check(self):
        """Test that dev versions with build numbers skip version checks."""
        responses.get(
            "https://workbench.example.com/delegated_azure_token",
            json={
                "result": True,
                "token": {
                    "access_token": "azure-token-xyz",
                    "token_type": "Bearer",
                    "expires_in": 3600,
                },
            },
        )

        client = Client()
        # Should not raise for dev version even though base version is too old
        token = client.oauth.get_delegated_azure_token("https://management.azure.com/")
        assert token["access_token"] == "azure-token-xyz"


class TestBasePathHandling:
    """Tests for proper handling of base paths in server URLs."""

    @patch.dict(
        "os.environ",
        {
            "POSIT_PRODUCT": "WORKBENCH",
            "RS_SERVER_ADDRESS": "https://example.com/workbench",  # Server with base path
            "RSTUDIO_VERSION": "2026.01.0",
            "RS_SESSION_RPC_COOKIE": TEST_RPC_COOKIE,
        },
    )
    @responses.activate
    def test_base_path_preserved(self):
        """Test that base paths in server URLs are preserved when making requests."""
        integration_id = "test-integration-id"

        # Mock should expect the URL to preserve the base path
        responses.get(
            "https://example.com/workbench/oauth_token",
            json={
                "access_token": "token123",
                "expiry": "2025-12-31T23:59:59+00:00",
            },
        )

        client = Client()
        credentials = client.oauth.get_credentials(integration_id)

        assert credentials is not None
        assert credentials["access_token"] == "token123"
