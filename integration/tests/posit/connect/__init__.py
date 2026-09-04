import os

from packaging.version import InvalidVersion, parse

try:
    CONNECT_VERSION = parse(os.environ["CONNECT_VERSION"])
except (KeyError, InvalidVersion) as e:
    raise RuntimeError(
        "Set the CONNECT_VERSION environment variable to the Connect version "
        "under test (e.g., `CONNECT_VERSION=2026.01.0 uv run pytest ...`), or "
        "run the suite via the Makefile (e.g., `make -C integration 2026.01.0`)."
    ) from e
