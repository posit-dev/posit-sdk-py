# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

from posit.connect.external.databricks import viewer_credentials_provider

from databricks import sql
from databricks.sdk.service.iam import CurrentUserAPI
from databricks.sdk.core import ApiClient, Config

from dash import Dash, html, Output, Input, dash_table
import pandas as pd
import flask

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

df = None
app = Dash(__name__)

app.layout = html.Div(
    children=[
        html.Div(id="greeting", children="Loading..."),
        html.Div(id="table-container"),
        html.Div(id="dummy"),  # dummy element to trigger callback on page load
    ]
)


@app.callback(
    [Output("table-container", "children"), Output("greeting", "children")],
    Input("dummy", "children"),
)
def update_page(_):
    """
    Dash example application that shows user information and
    the first few rows from a table hosted in Databricks.
    """

    session_token = flask.request.headers.get("Posit-Connect-User-Session-Token")
    credentials_provider = viewer_credentials_provider(user_session_token=session_token)

    def get_greeting():
        cfg = Config(
            host=DATABRICKS_HOST_URL, credentials_provider=credentials_provider
        )
        databricks_user_info = CurrentUserAPI(ApiClient(cfg)).me()
        return f"Hello, {databricks_user_info.display_name}!"

    def get_table():
        global df

        if df is None:
            query = "SELECT * FROM samples.nyctaxi.trips LIMIT 10;"

            with sql.connect(
                server_hostname=DATABRICKS_HOST,
                http_path=SQL_HTTP_PATH,
                auth_type="databricks-oauth",
                credentials_provider=credentials_provider,
            ) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    df = pd.DataFrame(
                        rows, columns=[col[0] for col in cursor.description]
                    )

        table = dash_table.DataTable(
            id="table",
            columns=[{"name": i, "id": i} for i in df.columns],
            data=df.to_dict("records"),
            style_table={"overflowX": "scroll"},
        )
        return table

    return get_table(), get_greeting()


if __name__ == "__main__":
    app.run(debug=True)
