# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

from databricks import sql
from databricks.sdk.core import Config, databricks_cli
from flask import Flask, request

from posit.connect.external.databricks import PositCredentialsStrategy

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

rows = None
app = Flask(__name__)


@app.route("/")
def usage():
    return "<p>Try: <pre>GET /fares<pre></p>"


@app.route("/fares")
def get_fares():
    """
    Flask example API that returns the first few rows from
    a table hosted in Databricks.
    """
    global rows

    session_token = request.headers.get("Posit-Connect-User-Session-Token")
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

    if rows is None:
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

    return [row.asDict() for row in rows]


if __name__ == "__main__":
    app.run(debug=True)
