import os

from posit.connect.client import Client
from posit.connect.external.databricks import viewer_credentials_provider

from databricks import sql
from databricks.sdk.service.iam import CurrentUserAPI
from databricks.sdk.core import ApiClient, Config

import pandas as pd
import streamlit as st
from streamlit.web.server.websocket_headers import _get_websocket_headers

DB_PAT=os.getenv("DATABRICKS_TOKEN")

DB_HOST="adb-138962681435081.1.azuredatabricks.net"
DB_HOST_URL = f"https://{DB_HOST}"
SQL_HTTP_PATH="/sql/1.0/warehouses/684d08139179d1dd"

CONTENT_IDENTITY = None

# Read the viewer's individual content identity token from the streamlit ws header.
headers = _get_websocket_headers()
if headers:
    CONTENT_IDENTITY = headers.get('Posit-Connect-Content-Identity')

with Client() as connect_client:
    credentials_provider = viewer_credentials_provider(
            connect_client.oauth, content_identity=CONTENT_IDENTITY)
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
            cursor.execute("SELECT * FROM catalog_zverham.example_schema_zverham.example_data_zverham")
            result = cursor.fetchall()
            st.table(pd.DataFrame(result))

