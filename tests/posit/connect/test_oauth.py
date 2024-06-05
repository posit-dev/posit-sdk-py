import responses

from posit.connect import Client


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
                    }
                )
            ],
            json={
                "access_token": "viewer-token",
                "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "token_type": "Bearer",
            },
        )
        responses.post(
            "https://connect.example/__api__/v1/oauth/integrations/credentials",
            match=[
                responses.matchers.urlencoded_params_matcher(
                    {
                        "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
                        "subject_token_type": "urn:posit:connect:api-key",
                        "subject_token": "12345",
                    }
                )
            ],
            json={
                "access_token": "sdk-user-token",
                "issued_token_type": "urn:ietf:params:oauth:token-type:access_token",
                "token_type": "Bearer",
            },
        )
        con = Client(api_key="12345", url="https://connect.example/")
        assert con.oauth.get_credentials()["access_token"] == "sdk-user-token"
        assert (
            con.oauth.get_credentials("cit")["access_token"] == "viewer-token"
        )
