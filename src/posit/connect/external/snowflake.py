"""Snowflake SDK integration.

Snowflake SDK credentials implementations which support interacting with Posit OAuth integrations on Connect.

Notes
-----
The APIs in this module are provided as a convenience and are subject to breaking changes.
"""

from typing_extensions import Optional

from .._utils import is_local
from ..client import Client


class PositAuthenticator:
    """
    Authenticator for Snowflake SDK which supports Posit OAuth integrations on Connect.

    Examples
    --------
    ```python
    import os

    import pandas as pd
    import snowflake.connector
    import streamlit as st

    from posit.connect.external.snowflake import PositAuthenticator

    ACCOUNT = os.getenv("SNOWFLAKE_ACCOUNT")
    WAREHOUSE = os.getenv("SNOWFLAKE_WAREHOUSE")

    # USER is only required when running the example locally with external browser auth
    USER = os.getenv("SNOWFLAKE_USER")

    # https://docs.snowflake.com/en/user-guide/sample-data-using
    DATABASE = os.getenv("SNOWFLAKE_DATABASE", "snowflake_sample_data")
    SCHEMA = os.getenv("SNOWFLAKE_SCHEMA", "tpch_sf1")
    TABLE = os.getenv("SNOWFLAKE_TABLE", "lineitem")

    session_token = st.context.headers.get("Posit-Connect-User-Session-Token")
    auth = PositAuthenticator(
        local_authenticator="EXTERNALBROWSER", user_session_token=session_token
    )

    con = snowflake.connector.connect(
        user=USER,
        account=ACCOUNT,
        warehouse=WAREHOUSE,
        database=DATABASE,
        schema=SCHEMA,
        authenticator=auth.authenticator,
        token=auth.token,
    )

    snowflake_user = con.cursor().execute("SELECT CURRENT_USER()").fetchone()
    st.write(f"Hello, {snowflake_user[0]}!")

    with st.spinner("Loading data from Snowflake..."):
        df = pd.read_sql_query(f"SELECT * FROM {TABLE} LIMIT 10", con)

    st.dataframe(df)
    ```
    """

    def __init__(
        self,
        local_authenticator: Optional[str] = None,
        client: Optional[Client] = None,
        user_session_token: Optional[str] = None,
    ):
        self._local_authenticator = local_authenticator
        self._client = client
        self._user_session_token = user_session_token

    @property
    def authenticator(self) -> Optional[str]:
        if is_local():
            return self._local_authenticator
        return "oauth"

    @property
    def token(self) -> Optional[str]:
        if is_local():
            return None

        # If the user-session-token wasn't provided and we're running on Connect then we raise an exception.
        # user_session_token is required to impersonate the viewer.
        if self._user_session_token is None:
            raise ValueError("The user-session-token is required for viewer authentication.")

        if self._client is None:
            self._client = Client()

        credentials = self._client.oauth.get_credentials(self._user_session_token)
        return credentials.get("access_token")
