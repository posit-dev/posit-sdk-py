from ..client import Client


def connect_mcp_help() -> str:
    """Return a help string for the Connect MCP tools."""
    return """
        This is the Posit Connect MCP tools. You can use these tools to interact with the Posit Connect server.
        To authenticate properly, you need to provide a valid Connect server url and api key using the CONNECT_SERVER
        and CONNECT_API_KEY environment variables, respectively.
    """


def get_current_user() -> str:
    """Return the current user's information based on the API key."""
    client = Client()
    return str(client.me)


TOOLS = [
    connect_mcp_help,
    get_current_user,
]
