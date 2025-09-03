import json
from typing import Any, Dict, List, Optional

import click
from click.core import Command, Group


def extract_click_options(command: Command) -> List[Dict[str, Any]]:
    """Extract Click options and convert them to MCP tool parameters."""
    properties = {}
    required = []

    for param in command.params:
        if isinstance(param, click.Option):
            param_name = param.name
            param_type = "string"  # Default type
            description = param.help or f"Parameter {param_name}"

            # Map Click types to JSON schema types
            if isinstance(param.type, click.IntRange):
                param_type = "integer"
                if param.type.min is not None:
                    properties[param_name] = {
                        "type": param_type,
                        "description": description,
                        "minimum": param.type.min,
                    }
                else:
                    properties[param_name] = {"type": param_type, "description": description}
            elif isinstance(param.type, click.Choice):
                properties[param_name] = {
                    "type": "string",
                    "enum": list(param.type.choices),
                    "description": description,
                }
            elif isinstance(param.type, click.Path):
                properties[param_name] = {
                    "type": "string",
                    "description": f"{description} (file path)",
                }
            elif isinstance(param.type, click.types.BoolParamType):
                param_type = "boolean"
                properties[param_name] = {"type": param_type, "description": description}
            else:
                properties[param_name] = {"type": param_type, "description": description}

            # Handle required parameters
            if param.required:
                required.append(param_name)

            # Handle default values
            if param.default is not None and not isinstance(param.default, tuple):
                properties[param_name]["default"] = param.default

    return {"type": "object", "properties": properties, "required": required}


def generate_mcp_tool_schema(command: Command, tool_name: str) -> Dict[str, Any]:
    """Generate MCP tool schema from Click command."""
    return {
        "name": tool_name,
        "description": command.help or command.short_help or f"Execute {tool_name} command",
        "inputSchema": extract_click_options(command),
    }


def get_all_commands(group: Group, prefix: str = "") -> Dict[str, Command]:
    """Recursively extract all commands from a Click group."""
    commands = {}

    for name, command in group.commands.items():
        tool_name = f"{prefix}{name}".replace("-", "_")

        if isinstance(command, Group):
            # Recursively handle subcommands
            subcommands = get_all_commands(command, f"{tool_name}_")
            commands.update(subcommands)
        else:
            commands[tool_name] = command

    return commands


def generate_all_mcp_tools() -> List[Dict[str, Any]]:
    """Generate MCP tool schemas for all rsconnect commands."""
    from rsconnect.main import cli

    tools = []
    commands = get_all_commands(cli)

    for tool_name, command in commands.items():
        try:
            schema = generate_mcp_tool_schema(command, tool_name)
            tools.append(schema)
        except Exception as e:
            print(f"Error generating schema for {tool_name}: {e}")

    return tools
