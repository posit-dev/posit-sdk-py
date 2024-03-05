# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

import pandas as pd

from posit.connect.external.databricks import viewer_credentials_provider

from databricks import sql
from databricks.sdk.service.iam import CurrentUserAPI
from databricks.sdk.core import ApiClient, Config

from shiny import App, Inputs, Outputs, Session, render, ui

DATABRICKS_PAT = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HOST=os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

app_ui = ui.page_fluid(
    ui.output_text("text"),
    ui.output_data_frame("result")
)

def get_databricks_user_info(credentials_provider):
    """
    Use the Databricks SDK to get the current user's information.
    """

    if os.getenv("CONNECT_SERVER"):
        cfg = Config(
            host=DATABRICKS_HOST_URL,
            credentials_provider=credentials_provider
        )
    else:
        cfg = Config(host=DATABRICKS_HOST_URL, token=DATABRICKS_PAT)

    return CurrentUserAPI(ApiClient(cfg)).me()

def server(input: Inputs, output: Outputs, session: Session):
    """
    Shiny for Python example application that shows user information and 
    the first few rows from a table hosted in Databricks.
    """

    session_token = session.http_conn.headers.get('Posit-Connect-User-Session-Token')
    credentials_provider = viewer_credentials_provider(user_session_token=session_token)
    databricks_user_info = get_databricks_user_info(credentials_provider=credentials_provider)

    @render.data_frame
    def result():

        query = "SELECT * FROM samples.nyctaxi.trips LIMIT 10;"

        with sql.connect(server_hostname=DATABRICKS_HOST,
                         http_path=SQL_HTTP_PATH,
                         auth_type="databricks-oauth",
                         credentials_provider=credentials_provider) as connection:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns = [col[0] for col in cursor.description])
                return df

    @render.text
    def text():
        return f"Hello, {databricks_user_info.display_name}!"

app = App(app_ui, server)
