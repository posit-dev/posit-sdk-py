# FastAPI Example

## Start the app locally

```bash
# install uvicorn
pip install "uvicorn[standard]"

# start the app
export DATABRICKS_HOST="<databricks-sql-warehouse-server-hostname>"
export DATABRICKS_PATH="<databricks-sql-warehouse-http-path>"
uvicorn app:app --reload

# send a request to the rest api
curl -X 'GET' 'http://127.0.0.1:8000/fares'
```

## Deploy to Posit Connect

Validate that `rsconnect-python` is installed:

```bash
rsconnect version
```

Or install it as documented in the [installation](https://docs.posit.co/rsconnect-python/#installation) section of the documentation.

To publish, make sure `CONNECT_SERVER`, `CONNECT_API_KEY`, `DATABRICKS_HOST`, `DATABRICKS_PATH` have valid values. Then, on a terminal session, enter the following command:

```bash
rsconnect deploy fastapi . \
  --server "${CONNECT_SERVER}" \
  --api-key "${CONNECT_API_KEY}" \
  --environment DATABRICKS_HOST \
  --environment DATABRICKS_PATH
```

Note that the Databricks environment variables do not need to be resolved by the shell, so they do not include the `$` prefix.

The Databricks environment variables only need to be set once, unless a change needs to be made. If the values have not changed, you don’t need to provide them again when you publish updates to the document.

```
rsconnect deploy fastapi . \
  --server "${CONNECT_SERVER}" \
  --api-key "${CONNECT_API_KEY}"
```
