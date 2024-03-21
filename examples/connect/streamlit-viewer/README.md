# Streamlit Example

## Start the app locally

```bash
export DATABRICKS_HOST="<databricks-workspace-url>"
export DATABRICKS_CLUSTER_ID="<databricks-compute-cluster-id>"
streamlit run app.py
```

## Deploy to PTD Staging Connect

Validate that Posit `publisher` is installed:

```bash
publisher --version
```

Or install it as documented in the [installation](https://github.com/posit-dev/publisher) section of the documentation.

Publish with the following command:

```bash
publisher redeploy ptd-streamlit-dbconnect-viewer
```
