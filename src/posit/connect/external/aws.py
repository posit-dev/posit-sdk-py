from __future__ import annotations

import base64
import json

from typing_extensions import TYPE_CHECKING, Dict, Optional

from ..oauth.oauth import OAuthTokenType

if TYPE_CHECKING:
    from ..client import Client


def get_aws_credentials(client: Client, user_session_token: str) -> Dict[str, str]:
    """
    Get AWS credentials using OAuth token exchange for an AWS Viewer integration.

    According to RFC 8693, the access token must be a base64 encoded JSON object
    containing the AWS credentials. This function will decode and deserialize the
    access token and return the AWS credentials.

    Examples
    --------
    ```python
    from posit.connect import Client
    from posit.connect.external.aws import get_aws_credentials
    import boto3
    from shiny.express import session

    client = Client()
    session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
    credentials = get_aws_credentials(client, user_session_token)
    aws_session = boto3.Session(
        aws_access_key_id=credentials["accessKeyId"],
        aws_secret_access_key=credentials["secretAccessKey"],
        aws_session_token=credentials["sessionToken"],
    )

    s3 = aws_session.resource("s3")
    bucket = s3.Bucket("your-bucket-name")
    ```

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
    return _decode_access_token(access_token)


def get_aws_content_credentials(
    client: Client, content_session_token: Optional[str] = None
) -> Dict[str, str]:
    """
    Get AWS credentials using OAuth token exchange for an AWS Service Account integration.

    According to RFC 8693, the access token must be a base64 encoded JSON object
    containing the AWS credentials. This function will decode and deserialize the
    access token and return the AWS credentials.

    Examples
    --------
    ```python
    from posit.connect import Client
    from posit.connect.external.aws import get_aws_content_credentials
    import boto3

    client = Client()
    credentials = get_aws_content_credentials(client)
    session = boto3.Session(
        aws_access_key_id=credentials["accessKeyId"],
        aws_secret_access_key=credentials["secretAccessKey"],
        aws_session_token=credentials["sessionToken"],
    )

    s3 = session.resource("s3")
    bucket = s3.Bucket("your-bucket-name")
    ```

    Parameters
    ----------
    client : Client
        The client to use for making requests
    content_session_token : str
        The content session token to exchange

    Returns
    -------
    Dict[str, str]
        Dictionary containing AWS credentials with keys:
        access_key_id, secret_access_key, session_token, and expiration
    """
    # Get credentials using OAuth
    credentials = client.oauth.get_content_credentials(
        content_session_token=content_session_token,
        requested_token_type=OAuthTokenType.AWS_CREDENTIALS,
    )

    # Decode base64 access token
    access_token = credentials.get("access_token")
    if not access_token:
        raise ValueError("No access token found in credentials")
    return _decode_access_token(access_token)


def _decode_access_token(access_token: str) -> Dict[str, str]:
    """
    Decode and deserialize an access token containing AWS credentials.

    According to RFC 8693, the access token must be a base64 encoded JSON object
    containing the AWS credentials. This function will decode and deserialize the
    access token and return the AWS credentials.

    Parameters
    ----------
    access_token : str
        The access token to decode

    Returns
    -------
    Dict[str, str]
        Dictionary containing AWS credentials with keys:
        access_key_id, secret_access_key, session_token, and expiration
    """
    decoded_bytes = base64.b64decode(access_token)
    decoded_str = decoded_bytes.decode("utf-8")
    aws_credentials = json.loads(decoded_str)

    return aws_credentials
