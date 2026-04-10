# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

The `posit-sdk` is a Python SDK for Posit's professional products: **Posit Connect** (`src/posit/connect/`) and **Posit Workbench** (`src/posit/workbench/`). Connect is the primary, mature product; Workbench support is early-stage.

## Commands

All development uses `uv` for package management and a `Makefile` for tasks. A `.venv` virtual environment is expected.

| Command | Purpose |
|---|---|
| `make dev` | Install in editable mode with all dev dependencies |
| `make test` | Run unit tests with coverage (`pytest`) |
| `make lint` | Lint (`ruff check` + `pyright`) |
| `make fmt` | Auto-format (`ruff check --fix` + `ruff format`) |
| `make build` | Build wheel distribution |
| `make it` | Run integration tests (requires Connect instance) |
| `make` | Run all: dev, test, lint, build |

**Run a single test:**
```bash
uv run pytest tests/posit/connect/test_content.py::TestContentItemDelete::test -s
```

## Architecture

### Resource Pattern

Both SDKs follow a layered resource architecture centered on `Context`:

- **`Client`** — Entry point. Subclasses `requests.Session`. Holds a `Context` and provides attribute-based access to resource collections (e.g., `client.content`, `client.users`).
- **`Context`** — Holds a weak reference back to the `Client`. Lazily fetches and caches server version. Passed to all resources.
- **`BaseResource(dict)`** — Dict subclass with `_ctx`. Most Connect domain objects (ContentItem, User, Group, etc.) extend this. Field access is via `item["key"]` (attribute access is deprecated).
- **`_Resource(dict)`** — Simpler dict subclass with `_ctx` and `_path`, providing `update()` and `destroy()` methods.
- **`Resources`** — Base class for collection managers (e.g., `Content`, `Users`) that hold `_ctx` and implement `find()`, `create()`, `get()`, etc.
- **`Active(BaseResource)`** — For singular HTTP endpoints returning one resource.

### Version Gating

The `@requires(version)` decorator (in `context.py`) gates methods by Connect server version. It compares `ctx.version` against the required version and raises `RuntimeError` if the server is too old.

### Pagination

`Paginator` (in `paginator.py`) handles offset-based pagination. Resource collections that return large lists use `_PaginatedResourceSequence`.

### Mixins

ContentItem uses mixins for composed behavior: `VanityMixin`, `ContentItemRepositoryMixin`, `ContentItemAssociations`, `ContentItemTags`.

## Testing

- Unit tests are in `tests/posit/`, mirroring the `src/posit/` structure.
- HTTP mocking uses the `responses` library with the `@responses.activate` decorator.
- Mock API responses are JSONC files stored in `tests/posit/connect/__api__/`, loaded via helpers in `tests/posit/connect/api.py` (`load_mock`, `load_mock_dict`, `load_mock_list`).
- Test `Client` instantiation: `Client("https://connect.example", "12345")` — no real server needed.
- Integration tests live in `integration/` and run against real Connect instances across many versions.

## Style

- **Ruff** handles all linting and formatting (line length: 99).
- **Pyright** for type checking.
- **NumPy-style docstrings** (used by quartodoc for API reference docs).
- `from __future__ import annotations` is used in all source files.
- `typing-extensions` is used instead of `typing` for Python 3.8 compatibility.
- Pre-commit hooks run `make fmt lint` (enable with `pre-commit install`).
- Conventional commit messages are enforced by CI.
