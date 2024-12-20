# -*- coding: utf-8 -*-
# mypy: ignore-errors
from __future__ import annotations

import os

from databricks import sql
from databricks.sdk.core import Config, databricks_cli
from fastapi import FastAPI, Header
from typing_extensions import TYPE_CHECKING, Annotated

from posit.connect.external.databricks import PositCredentialsStrategy

if TYPE_CHECKING:
    from fastapi.responses import JSONResponse

DATABRICKS_HOST = os.getenv("DATABRICKS_HOST")
DATABRICKS_HOST_URL = f"https://{DATABRICKS_HOST}"
SQL_HTTP_PATH = os.getenv("DATABRICKS_PATH")

rows = None
app = FastAPI()


@app.get("/fares")
async def get_fares(
    posit_connect_user_session_token: Annotated[str | None, Header()] = None,
) -> JSONResponse:
    """
    FastAPI example API that returns the first few rows from
    a table hosted in Databricks.
    """
    global rows

    posit_strategy = PositCredentialsStrategy(
        local_strategy=databricks_cli,
        user_session_token=posit_connect_user_session_token,
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
