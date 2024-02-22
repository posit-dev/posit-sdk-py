```bash
# start streamlit locally
DATABRICKS_TOKEN=<DB_PAT> \
CONNECT_SERVER=http://localhost:3939/__api__ \
CONNECT_API_KEY=$CONNECT_INSECURE_ADMIN_API_KEY \
streamlit run ./sample-content.py


# deploy the app the first time
publisher deploy -a localhost:3939 -n databricks ./

# re-deploy the databricks app
publisher redeploy databricks
```


TODO: Test this content with databricks-connect
<https://docs.databricks.com/en/dev-tools/databricks-connect/python/index.html>

```
# install the sdk from this branch
pip install git+https://github.com/posit-dev/posit-sdk-py.git@kegs/databricks-oauth
```
