# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import ApiClient, Config
from databricks.sdk.service.iam import CurrentUserAPI
from streamlit.web.server.websocket_headers import _get_websocket_headers

from posit.connect.external.databricks import viewer_credentials_provider

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

session_token = _get_websocket_headers().get(
    "Posit-Connect-User-Session-Token"
)

credentials_provider = viewer_credentials_provider(
    user_session_token=session_token
)

cfg = Config(
    host=DATABRICKS_HOST_URL, credentials_provider=credentials_provider
)
databricks_user = CurrentUserAPI(ApiClient(cfg)).me()
st.write(f"Hello, {databricks_user.display_name}!")

with sql.connect(
    server_hostname=DATABRICKS_HOST,
    http_path=SQL_HTTP_PATH,
    auth_type="databricks-oauth",
    credentials_provider=credentials_provider,
) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM samples.nyctaxi.trips LIMIT 10;")
        result = cursor.fetchall()
        st.table(pd.DataFrame(result))
