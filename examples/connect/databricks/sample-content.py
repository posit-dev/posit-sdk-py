# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

from posit.connect.external.databricks import viewer_credentials_provider

from databricks import sql
from databricks.sdk.service.iam import CurrentUserAPI
from databricks.sdk.core import ApiClient, Config

import pandas as pd
import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

DB_PAT=os.getenv("DATABRICKS_TOKEN")

DB_HOST=os.getenv("DB_HOST")
DB_HOST_URL = f"https://{DB_HOST}"
SQL_HTTP_PATH=os.getenv("SQL_HTTP_PATH")

USER_SESSION_TOKEN = None

# Read the viewer's user session token from the streamlit ws header.
headers = _get_websocket_headers()
if headers:
    USER_SESSION_TOKEN = headers.get('Posit-Connect-User-Session')

credentials_provider = viewer_credentials_provider(user_session_token=USER_SESSION_TOKEN)
cfg = Config(host=DB_HOST_URL, credentials_provider=credentials_provider)
#cfg = Config(host=DB_HOST_URL, token=DB_PAT)

databricks_user = CurrentUserAPI(ApiClient(cfg)).me()
st.write(f"Hello, {databricks_user.display_name}!")

with sql.connect(
        server_hostname=DB_HOST,
        http_path=SQL_HTTP_PATH,
        #access_token=DB_PAT) as connection:
        auth_type='databricks-oauth',
        credentials_provider=credentials_provider) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM data")
        result = cursor.fetchall()
        st.table(pd.DataFrame(result))

