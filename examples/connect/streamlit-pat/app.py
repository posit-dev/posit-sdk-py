# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

from databricks.connect.session import DatabricksSession
from databricks.sdk.service.iam import CurrentUserAPI
from databricks.sdk.core import ApiClient, Config

import streamlit as st

DATABRICKS_PAT = os.getenv("DATABRICKS_PAT")
DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")

# https://docs.databricks.com/en/compute/access-mode-limitations.html#general-uc
# *Important* The cluster must use a shared access mode if the UC table has any row-filter-column-masks defined.
# https://docs.databricks.com/en/data-governance/unity-catalog/row-and-column-filters.html
DATABRICKS_CLUSTER_ID = os.getenv("DATABRICKS_CLUSTER_ID")

cfg = Config(
    host=DATABRICKS_HOST,
    cluster_id=DATABRICKS_CLUSTER_ID,
    token=DATABRICKS_PAT,
)

try:
    databricks_user = CurrentUserAPI(ApiClient(cfg)).me()
    st.write(f"Hello, {databricks_user.display_name}!")

    spark = DatabricksSession.builder.sdkConfig(cfg).getOrCreate()
    catalog = "catalog_zverham"
    schema = "example_schema_zverham"
    table = "example_data_zverham"
    df = spark.sql(f"SELECT * FROM {catalog}.{schema}.{table};")
    st.table(df.toPandas())

except Exception as e:
    st.error(e)
