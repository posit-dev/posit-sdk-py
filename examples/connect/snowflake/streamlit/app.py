# -*- coding: utf-8 -*-
# mypy: ignore-errors
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
auth = PositAuthenticator(local_authenticator="EXTERNALBROWSER", user_session_token=session_token)

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
