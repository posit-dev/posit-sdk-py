import logging
from unittest.mock import patch

import responses

from posit.connect import Client
from posit.connect.oauth.oauth import OAuthTokenType, _get_content_session_token


class TestGetContentSessionToken:
    @patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN": "cit"})
    def test_env_var(self):
        assert _get_content_session_token() == "cit"

    def test_no_env_var(self):
        assert _get_content_session_token() is None

    def test_token_file(self, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text("file-token\n")
        with patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN_FILE": str(token_file)}):
            assert _get_content_session_token() == "file-token"

    def test_token_file_takes_priority(self, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text("file-token")
        with patch.dict(
            "os.environ",
            {
                "CONNECT_CONTENT_SESSION_TOKEN_FILE": str(token_file),
                "CONNECT_CONTENT_SESSION_TOKEN": "env-token",
            },
        ):
            assert _get_content_session_token() == "file-token"

    def test_token_file_not_found_falls_back_to_env_var(self, tmp_path):
        token_file = tmp_path / "nonexistent"
        with patch.dict(
            "os.environ",
            {
                "CONNECT_CONTENT_SESSION_TOKEN_FILE": str(token_file),
                "CONNECT_CONTENT_SESSION_TOKEN": "env-token",
            },
        ):
            assert _get_content_session_token() == "env-token"

    def test_token_file_empty(self, tmp_path, caplog):
        token_file = tmp_path / "token"
        token_file.write_text("")
        with patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN_FILE": str(token_file)}):
            with caplog.at_level(logging.WARNING):
                assert _get_content_session_token() is None
            assert "file is empty" in caplog.text


class TestHasContentCredentials:
    @patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN": "cit"})
    def test_true_with_env_var(self):
        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        assert c.oauth.has_content_credentials() is True

    def test_false_without_env_var(self):
        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        assert c.oauth.has_content_credentials() is False

    def test_true_with_token_file(self, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text("file-token")
        with patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN_FILE": str(token_file)}):
            c = Client(api_key="12345", url="https://connect.example/")
            c._ctx.version = None
            assert c.oauth.has_content_credentials() is True

    def test_false_with_empty_token_file(self, tmp_path):
        token_file = tmp_path / "token"
        token_file.write_text("")
        with patch.dict("os.environ", {"CONNECT_CONTENT_SESSION_TOKEN_FILE": str(token_file)}):
            c = Client(api_key="12345", url="https://connect.example/")
            c._ctx.version = None
            assert c.oauth.has_content_credentials() is False


class TestOAuthIntegrations:

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
                        # no requested token type set
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
    def test_get_credentials_with_requested_token_type(self):
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
        creds = c.oauth.get_credentials("cit", OAuthTokenType.API_KEY)
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
                        # no requested token type set
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
        assert creds is not None
        assert creds.get("access_token") == "content-token"

    @responses.activate
    def test_get_content_credentials_with_requested_token_type(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:content-session-token",
                        "subject_token": "cit",
                        "requested_token_type": "urn:ietf:params:aws:token-type:credentials",
                    },
                ),
            ],
            json={
                "access_token": "encoded-aws-creds",
                "issued_token_type": "urn:ietf:params:aws:token-type:credentials",
                "token_type": "aws_credentials",
            },
        )
        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        creds = c.oauth.get_content_credentials("cit", OAuthTokenType.AWS_CREDENTIALS)
        assert creds is not None
        assert creds.get("access_token") == "encoded-aws-creds"
        assert creds.get("issued_token_type") == "urn:ietf:params:aws:token-type:credentials"
        assert creds.get("token_type") == "aws_credentials"

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
        assert creds is not None
        assert creds.get("access_token") == "content-token"

    def test_get_content_credentials_returns_none_without_token(self):
        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        assert c.oauth.get_content_credentials() is None

    @responses.activate
    def test_get_content_credentials_with_audience(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:content-session-token",
                        "subject_token": "cit",
                        "audience": "integration-guid",
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
        creds = c.oauth.get_content_credentials("cit", audience="integration-guid")
        assert creds is not None
        assert creds.get("access_token") == "content-token"
        assert creds.get("issued_token_type") == "urn:ietf:params:oauth:token-type:access_token"
        assert creds.get("token_type") == "Bearer"

    @responses.activate
    def test_get_credentials_with_audience_and_req_token_type(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:user-session-token",
                        "subject_token": "cit",
                        "audience": "integration-guid",
                        "requested_token_type": "urn:ietf:params:oauth:token-type:access_token",
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
        creds = c.oauth.get_credentials(
            "cit",
            audience="integration-guid",
            requested_token_type=OAuthTokenType.ACCESS_TOKEN,
        )
        assert creds.get("access_token") == "viewer-token"
        assert creds.get("issued_token_type") == "urn:ietf:params:oauth:token-type:access_token"
        assert creds.get("token_type") == "Bearer"
