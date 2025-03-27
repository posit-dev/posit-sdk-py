from datetime import datetime

import pytest
import responses

from posit.connect import Client
from posit.connect.external.aws import (
    Credentials,
    _decode_access_token,
    get_content_credentials,
    get_credentials,
)

aws_creds = Credentials(
    aws_access_key_id="abc123",
    aws_secret_access_key="def456",
    aws_session_token="ghi789",
    expiration=datetime(2025, 1, 1, 0, 0, 0, 0),
)

encoded_aws_creds = "eyJhY2Nlc3NLZXlJZCI6ICJhYmMxMjMiLCAic2VjcmV0QWNjZXNzS2V5IjogImRlZjQ1NiIsICJzZXNzaW9uVG9rZW4iOiAiZ2hpNzg5IiwgImV4cGlyYXRpb24iOiAiMjAyNS0wMS0wMVQwMDowMDowMFoifQ=="


class TestAWS:
    @responses.activate
    def test_get_aws_credentials(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:user-session-token",
                        "subject_token": "cit",
                        "requested_token_type": "urn:ietf:params:aws:token-type:credentials",
                    }
                )
            ],
            json={
                "access_token": encoded_aws_creds,
                "issued_token_type": "urn:ietf:params:aws:token-type:credentials",
                "token_type": "aws_credentials",
            },
        )

        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        response = get_credentials(c, "cit")

        assert response == aws_creds

    @responses.activate
    def test_get_aws_credentials_no_token(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:user-session-token",
                        "subject_token": "cit",
                        "requested_token_type": "urn:ietf:params:aws:token-type:credentials",
                    }
                )
            ],
            json={},
        )

        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None

        with pytest.raises(ValueError) as e:
            get_credentials(c, "cit")

        assert e.match("No access token found in credentials")

    @responses.activate
    def test_get_aws_content_credentials(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:content-session-token",
                        "subject_token": "cit",
                        "requested_token_type": "urn:ietf:params:aws:token-type:credentials",
                    }
                )
            ],
            json={
                "access_token": encoded_aws_creds,
                "issued_token_type": "urn:ietf:params:aws:token-type:credentials",
                "token_type": "aws_credentials",
            },
        )

        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None
        response = get_content_credentials(c, "cit")

        assert response == aws_creds

    @responses.activate
    def test_get_aws_content_credentials_no_token(self):
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:content-session-token",
                        "subject_token": "cit",
                        "requested_token_type": "urn:ietf:params:aws:token-type:credentials",
                    }
                )
            ],
            json={},
        )

        c = Client(api_key="12345", url="https://connect.example/")
        c._ctx.version = None

        with pytest.raises(ValueError) as e:
            get_content_credentials(c, "cit")

        assert e.match("No access token found in credentials")

    def test_decode_access_token(self):
        decoded_creds = _decode_access_token(encoded_aws_creds)
        assert decoded_creds == aws_creds
