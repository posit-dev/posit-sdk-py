from enum import Enum

GRANT_TYPE = "urn:ietf:params:oauth:grant-type:token-exchange"


class OAuthTokenType(str, Enum):
    ACCESS_TOKEN = "urn:ietf:params:oauth:token-type:access_token"
    AWS_CREDENTIALS = "urn:ietf:params:aws:token-type:credentials"
    API_KEY = "urn:posit:connect:api-key"
    CONTENT_SESSION_TOKEN = "urn:posit:connect:content-session-token"
    USER_SESSION_TOKEN = "urn:posit:connect:user-session-token"


class OAuthIntegrationAuthType(str, Enum):
    """OAuth integration authentication type."""

    VIEWER = "Viewer"
    SERVICE_ACCOUNT = "Service Account"
    VISITOR_API_KEY = "Visitor API Key"


class OAuthIntegrationType(str, Enum):
    """OAuth integration type."""

    AWS = "aws"
    AZURE = "azure"
    AZURE_OPENAI = "azure-openai"
    CONNECT = "connect"
    CUSTOM = "custom"
    DATABRICKS = "databricks"
    GITHUB = "github"
    GOOGLE_BIGQUERY = "bigquery"
    GOOGLE_DRIVE = "drive"
    GOOGLE_SHEETS = "sheets"
    GOOGLE_VERTEX_AI = "vertex-ai"
    MSGRAPH = "msgraph"
    SALESFORCE = "salesforce"
    SHAREPOINT = "sharepoint"
    SNOWFLAKE = "snowflake"
