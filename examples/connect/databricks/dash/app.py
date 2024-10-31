# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

import flask
import pandas as pd
from dash import Dash, Input, Output, dash_table, html
from databricks import sql
from databricks.sdk.core import ApiClient, Config, databricks_cli
from databricks.sdk.service.iam import CurrentUserAPI

from posit.connect.external.databricks import PositCredentialsStrategy

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
    ],
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

    def get_greeting():
        databricks_user_info = CurrentUserAPI(ApiClient(cfg)).me()
        return f"Hello, {databricks_user_info.display_name}!"

    def get_table():
        global df

        if df is None:
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
