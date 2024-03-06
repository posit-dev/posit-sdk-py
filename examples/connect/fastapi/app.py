# -*- coding: utf-8 -*-
# mypy: ignore-errors
import os

from posit.connect.external.databricks import viewer_credentials_provider

from databricks import sql

from typing import Annotated

from fastapi import FastAPI, Header, Depends
from fastapi.responses import JSONResponse

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

rows = None
app = FastAPI()


async def get_token(
    posit_connect_user_session_token: Annotated[str | None, Header()] = None,
) -> dict | None:
    """
    Get the token from the Posit-Connect-User-Session-Token header.
    """
    if posit_connect_user_session_token is None:
        return None
    return posit_connect_user_session_token


@app.get("/fares")
async def get_fares(session_token=Depends(get_token)) -> JSONResponse:
    """
    FastAPI example API that returns the first few rows from
    a table hosted in Databricks.
    """
    global rows

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
