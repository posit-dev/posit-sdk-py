from __future__ import annotations

import base64
import json

from typing_extensions import TYPE_CHECKING, Dict

from ..oauth.oauth import OAuthTokenType

if TYPE_CHECKING:
    from ..client import Client


def get_aws_credentials(client: Client, user_session_token: str) -> Dict[str, str]:
    """
    Get AWS credentials using OAuth token exchange.

    According to RFC 8693, the access token must be a base64 encoded JSON object
    containing the AWS credentials. This function will decode and deserialize the
    access token and return the AWS credentials.

    Parameters
    ----------
    client : Client
        The client to use for making requests
    user_session_token : str
        The user session token to exchange

    Returns
    -------
    Dict[str, str]
        Dictionary containing AWS credentials with keys:
        access_key_id, secret_access_key, session_token, and expiration
    """
    # Get credentials using OAuth
    credentials = client.oauth.get_credentials(
        user_session_token=user_session_token,
        requested_token_type=OAuthTokenType.AWS_CREDENTIALS,
    )

    # Decode base64 access token
    access_token = credentials.get("access_token")
    if not access_token:
        raise ValueError("No access token found in credentials")
    decoded_bytes = base64.b64decode(access_token)
    decoded_str = decoded_bytes.decode("utf-8")
    aws_credentials = json.loads(decoded_str)

    return aws_credentials
