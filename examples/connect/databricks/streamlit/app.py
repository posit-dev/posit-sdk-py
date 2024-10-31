# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

import pandas as pd
import streamlit as st
from databricks import sql
from databricks.sdk.core import ApiClient, Config, databricks_cli
from databricks.sdk.service.iam import CurrentUserAPI

from posit.connect.external.databricks import PositCredentialsStrategy

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

session_token = st.context.headers.get("Posit-Connect-User-Session-Token")
posit_strategy = PositCredentialsStrategy(
    local_strategy=databricks_cli,
    user_session_token=session_token,
)
cfg = Config(
    host=DATABRICKS_HOST_URL,
    # uses Posit's custom credential_strategy if running on Connect,
    # otherwise falls back to the strategy defined by local_strategy
    credentials_strategy=posit_strategy,
)

databricks_user = CurrentUserAPI(ApiClient(cfg)).me()
st.write(f"Hello, {databricks_user.display_name}!")

with sql.connect(
    server_hostname=DATABRICKS_HOST,
    http_path=SQL_HTTP_PATH,
    # https://github.com/databricks/databricks-sql-python/issues/148#issuecomment-2271561365
    credentials_provider=posit_strategy.sql_credentials_provider(cfg),
) as connection:
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM samples.nyctaxi.trips LIMIT 10;")
        result = cursor.fetchall()
        st.table(pd.DataFrame(result))
