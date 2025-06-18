import asyncio
import contextlib
import urllib.parse
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from mcp.server.fastmcp import Context, FastMCP
from mcp.server.fastmcp.exceptions import ToolError

from .tools import TOOLS

mcp = FastMCP(
    name="Connect MCP Server",
    instructions="MCP server for interacting with Posit Connect.",
)

for tool_fn in TOOLS:
    mcp.add_tool(tool_fn)


def run_stdio_server():
    asyncio.run(mcp.run_stdio_async())


def get_streamable_http_server():
    @contextlib.asynccontextmanager
    async def lifespan(app: FastAPI):
        async with contextlib.AsyncExitStack() as stack:
            await stack.enter_async_context(mcp.session_manager.run())
            yield

    app = FastAPI(title="Connect MCP Server", lifespan=lifespan)
    templates = Jinja2Templates(directory=str(Path(__file__).parent))

    @app.get("/")
    async def get_index_page(request: Request):
        """Serves the HTML index page using a Jinja2 template."""
        tools_info = []
        for tool_name, tool_def in mcp._tool_manager._tools.items():
            parameters = {}
            for prop_name, prop in tool_def.parameters["properties"].items():
                parameters[prop_name] = {
                    "name": prop["title"],
                    "type": prop["type"],
                    "required": False,
                }

            if "required" in tool_def.parameters:
                for required_prop_name in tool_def.parameters["required"]:
                    if required_prop_name in parameters:
                        parameters[required_prop_name]["required"] = True

            tools_info.append(
                {
                    "name": tool_name,
                    "description": tool_def.description or "No description available.",
                    "parameters": parameters,
                }
            )
        endpoint = urllib.parse.urljoin(request.url._url, "mcp")
        return templates.TemplateResponse(
            "index.html.jinja",
            {
                "request": request,
                "server_name": mcp.name,
                "endpoint": endpoint,
                "tools": tools_info,
            },
        )

    app.mount("/", mcp.streamable_http_app())
    return app
