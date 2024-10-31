# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

import pandas as pd
from databricks import sql
from databricks.sdk.core import ApiClient, Config, databricks_cli
from databricks.sdk.service.iam import CurrentUserAPI
from shiny import App, Inputs, Outputs, Session, render, ui

from posit.connect.external.databricks import PositCredentialsStrategy

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

app_ui = ui.page_fluid(ui.output_text("text"), ui.output_data_frame("result"))


def server(i: Inputs, o: Outputs, session: Session):
    """
    Shiny for Python example application that shows user information and
    the first few rows from a table hosted in Databricks.
    """
    session_token = session.http_conn.headers.get("Posit-Connect-User-Session-Token")
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

    @render.data_frame
    def result():
        query = "SELECT * FROM samples.nyctaxi.trips LIMIT 10;"

        with sql.connect(
            server_hostname=DATABRICKS_HOST,
            http_path=SQL_HTTP_PATH,
            # https://github.com/databricks/databricks-sql-python/issues/148#issuecomment-2271561365
            credentials_provider=posit_strategy.sql_credentials_provider(cfg),
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns=[col[0] for col in cursor.description])
                return df

    @render.text
    def text():
        databricks_user_info = CurrentUserAPI(ApiClient(cfg)).me()
        return f"Hello, {databricks_user_info.display_name}!"


app = App(app_ui, server)
