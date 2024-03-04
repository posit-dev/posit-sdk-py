# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

from posit.connect.external.databricks import viewer_credentials_provider

from databricks import sql
from databricks.sdk.service.iam import CurrentUserAPI
from databricks.sdk.core import ApiClient, Config

from shiny import App, Inputs, Outputs, Session, render, ui
import pandas as pd

query = """
SELECT
  *
FROM
  samples.nyctaxi.trips
LIMIT 10;
"""

DATABRICKS_PAT = os.getenv("DATABRICKS_TOKEN")
DATABRICKS_HOST=os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

USER_SESSION_TOKEN = None

app_ui = ui.page_fluid(
    ui.output_text("text"),
    ui.output_data_frame("result")
)

def server(input: Inputs, output: Outputs, session: Session):

    credentials_provider = None
    if os.getenv("CONNECT_SERVER"):
        USER_SESSION_TOKEN = session.http_conn.headers['Posit-Connect-User-Session-Token']
        credentials_provider = viewer_credentials_provider(user_session_token=USER_SESSION_TOKEN)
        cfg = Config(host=DATABRICKS_HOST_URL, credentials_provider=credentials_provider)
    else:
        cfg = Config(host=DATABRICKS_HOST_URL, token=DATABRICKS_PAT)

    databricks_user = CurrentUserAPI(ApiClient(cfg)).me()

    @render.data_frame
    def result():

        connection_settings = {
            "server_hostname": DATABRICKS_HOST,
            "http_path": SQL_HTTP_PATH,
        }
        if os.getenv("CONNECT_SERVER"):
            connection_settings.update({
                "auth_type": "databricks-oauth",
                "credentials_provider": credentials_provider
            })
        else:
            connection_settings.update({
                "access_token": DATABRICKS_PAT
            })

        with sql.connect(**connection_settings) as connection:
            with connection.cursor() as cursor:
                tmp = cursor.execute(query)
                rows = cursor.fetchall()
                df = pd.DataFrame(rows, columns = [col[0] for col in cursor.description])
                return df

    @render.text
    def text():
        return f"Hello, {databricks_user.display_name}!"

app = App(app_ui, server)
