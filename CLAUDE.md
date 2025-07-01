# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The Posit SDK for Python provides a Pythonic interface for Posit's professional products, currently focusing on Posit Connect. The project is structured as a Python package using modern tooling and follows a client-based architecture pattern.

## Development Commands

### Setup and Installation

- `make dev` - Install project in editable mode with all development dependencies
- `make ensure-uv` - Ensure uv package manager is installed

### Testing

- `make test` - Run unit tests with coverage using pytest
- `make it` - Run integration tests against Connect versions
- `make integration/latest` - Run integration tests against latest Connect version
- `make integration/<version>` - Run integration tests against specific Connect version (e.g., `make integration/2025.06.0`)

### Code Quality

- `make lint` - Run ruff linting and pyright type checking
- `make fmt` - Auto-format code with ruff and fix lint issues
- `pre-commit install` - Enable pre-commit hooks for automatic formatting/linting

### Build and Release

- `make build` - Build distribution packages
- `make clean` - Remove build artifacts and caches
- `make all` - Complete workflow: dev, test, lint, build

### Coverage

- `make cov` - Generate coverage report
- `make cov-html` - Generate and open HTML coverage report

## Architecture

### Core Client Pattern

The SDK uses a centralized `Client` class that provides access to all API resources:

- **Client** (`src/posit/connect/client.py`) - Main entry point with authentication and resource access
- **Context** (`src/posit/connect/context.py`) - Manages client state and version requirements
- **Auth** (`src/posit/connect/auth.py`) - Handles API key authentication

### Resource Organization

Resources are organized as properties of the Client class:

- `client.content` - Content management (apps, reports, etc.)
- `client.users` - User management
- `client.groups` - Group management
- `client.tags` - Tag management
- `client.metrics` - Usage and performance metrics
- `client.oauth` - OAuth integrations (Connect 2024.08.0+)
- `client.system` - System information
- `client.me` - Current user information

### Version Requirements

The SDK uses the `@requires(version="X.Y.Z")` decorator to enforce minimum Connect server versions for API features. This prevents runtime errors when using newer APIs against older servers.

### Testing Structure

- **Unit tests**: `tests/posit/connect/` - Mock-based tests with JSON fixtures in `tests/posit/connect/__api__/`
- **Integration tests**: `integration/tests/` - Real server tests against multiple Connect versions
- **Docker-based testing**: Integration tests run against dockerized Connect instances

## Key Configuration Files

- `pyproject.toml` - Python project configuration, dependencies, and tool settings
- `Makefile` - Build automation and development commands
- `uv.lock` - Locked dependency versions
- `integration/Makefile` - Integration test orchestration with Docker Compose
- `integration/compose.yaml` - Docker services for integration testing

## Integration Testing

The integration test suite runs against multiple Connect server versions using Docker:

- Tests are located in `integration/tests/`
- Each Connect version gets its own Docker container
- Use `make integration/latest` for quick testing or `make integration/all` for full compatibility testing
- Available versions are defined in `integration/Makefile` under `CONNECT_VERSIONS`

## Authentication Patterns

The SDK supports multiple authentication patterns:

1. Environment variables: `CONNECT_SERVER` and `CONNECT_API_KEY`
2. Client constructor: `Client(url, api_key)`
3. User session tokens: `client.with_user_session_token(token)` for viewer-scoped operations

## Development Notes

- Uses `uv` as the package manager and virtual environment tool
- Ruff handles both linting and formatting (replaces black/isort)
- Type checking with pyright
- Supports Python 3.8+ with modern typing via `typing_extensions`
- Integration tests require Docker and can run in parallel with `make -j 4`
