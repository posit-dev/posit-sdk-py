from unittest.mock import patch

import pytest
import responses

from posit.connect import Client
from posit.connect.oauth.oauth import API_KEY_TOKEN_TYPE, _get_content_session_token


class TestOAuthIntegrations:
    @patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN": "cit"})
    def test_get_content_session_token_success(self):
        assert _get_content_session_token() == "cit"

    def test_get_content_session_token_failure(self):
        with pytest.raises(ValueError):
            _get_content_session_token()

    @responses.activate
    def test_get_credentials(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:user-session-token",
                        "subject_token": "cit",
                    },
                ),
            ],
            json={
                "access_token": "viewer-token",
                "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "token_type": "Bearer",
            },
        )
        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        creds = c.oauth.get_credentials("cit")
        assert creds.get("access_token") == "viewer-token"

    @responses.activate
    def test_get_credentials_api_key(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:user-session-token",
                        "subject_token": "cit",
                        "requested_token_type": "urn:posit:connect:api-key",
                    },
                ),
            ],
            json={
                "access_token": "viewer-api-key",
                "issued_token_type": "urn:posit:connect:api-key",
                "token_type": "Key",
            },
        )
        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        creds = c.oauth.get_credentials("cit", API_KEY_TOKEN_TYPE)
        assert creds.get("access_token") == "viewer-api-key"
        assert creds.get("issued_token_type") == "urn:posit:connect:api-key"
        assert creds.get("token_type") == "Key"

    @responses.activate
    def test_get_content_credentials(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:content-session-token",
                        "subject_token": "cit",
                    },
                ),
            ],
            json={
                "access_token": "content-token",
                "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "token_type": "Bearer",
            },
        )
        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        creds = c.oauth.get_content_credentials("cit")
        assert creds.get("access_token") == "content-token"

    @patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN": "cit"})
    @responses.activate
    def test_get_content_credentials_env_var(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:content-session-token",
                        "subject_token": "cit",
                    },
                ),
            ],
            json={
                "access_token": "content-token",
                "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "token_type": "Bearer",
            },
        )
        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        creds = c.oauth.get_content_credentials()
        assert creds.get("access_token") == "content-token"
