# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

from posit.connect.external.databricks import viewer_credentials_provider
from databricks import sql
from flask import Flask, request

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
    credentials_provider = viewer_credentials_provider(user_session_token=session_token)

    if rows is None:
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

    return [row.asDict() for row in rows]


if __name__ == "__main__":
    app.run(debug=True)
