# Streamlit Example

## Start the app locally

```bash
SNOWFLAKE_ACCOUNT = "<snowflake-account-identifier>"
SNOWFLAKE_WAREHOUSE = "<snowflake-warehouse-name>"

# USER is only required when running the example locally with external browser auth
SNOWFLAKE_USER="<snowflake-username>" streamlit run app.py
```

## Deploy to Posit Connect

Validate that `rsconnect-python` is installed:

```bash
rsconnect version
```

Or install it as documented in the [installation](https://docs.posit.co/rsconnect-python/#installation) section of the documentation.

To publish, make sure `CONNECT_SERVER`, `CONNECT_API_KEY`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_WAREHOUSE` have valid values. Then, on a terminal session, enter the following command:

```bash
rsconnect deploy streamlit . \
  --server "${CONNECT_SERVER}" \
  --api-key "${CONNECT_API_KEY}" \
  --environment SNOWFLAKE_ACCOUNT \
  --environment SNOWFLAKE_WAREHOUSE
```

Note that the Snowflake environment variables do not need to be resolved by the shell, so they do not include the `$` prefix.

The Snowflake environment variables only need to be set once, unless a change needs to be made. If the values have not changed, you don’t need to provide them again when you publish updates to the document.

```bash
rsconnect deploy streamlit . \
  --server "${CONNECT_SERVER}" \
  --api-key "${CONNECT_API_KEY}"
```
