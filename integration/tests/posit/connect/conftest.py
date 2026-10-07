"""Provision a fresh Posit Connect container for each test class.

Prevents state from leaking between classes (posit-dev/posit-sdk-py#460).
Standard pytest selection works: running a single test boots exactly the
container(s) its class needs.
"""

from __future__ import annotations

import os
import socket
import subprocess
import warnings

import pytest

# with-connect requires Python >= 3.13; pin the source to avoid a stale
# copy on PATH.
_WITH_CONNECT = [
    "uvx",
    "--python",
    "3.13",
    "--from",
    "git+https://github.com/posit-dev/with-connect.git",
    "with-connect",
]


def _runtime_config(python_version: str) -> dict[str, str]:
    """Enable integration features for images with a single Python runtime."""
    return {
        "CONNECT_PYTHON_ENABLED": "true",
        "CONNECT_PYTHON_EXECUTABLE": f"/opt/python/{python_version}/bin/python",
        "CONNECT_PYTHON_VERSIONMATCHING": "nearest",
        "CONNECT_PYTHON_ENVIRONMENTMANAGEMENT": "true",
        "CONNECT_SERVER_ALLOWRUNTIMECACHEMANAGEMENT": "true",
        "CONNECT_METRICS_INSTRUMENTATION": "true",
    }


# Release defaults may contain any Connect environment overrides. Exact versions
# can override individual settings without duplicating the release configuration.
# Match the older Python version in test bundles to the runtime in each image.
_CONNECT_CONFIGS: dict[str, dict[str, str]] = {
    "2026.04": _runtime_config("3.14.4"),
    "2026.05": _runtime_config("3.14.5"),
    "2026.06": _runtime_config("3.14.6"),
    "2026.07": _runtime_config("3.14.6"),
    "2026.08": _runtime_config("3.14.7"),
    "2026.09": _runtime_config("3.14.7"),
}

# Posit Connect license file to mount into each container (gitignored).
_LICENSE = os.environ.get("LICENSE", "./license.lic")


def _connect_env(connect_version: str) -> list[str]:
    """Merge release defaults and exact-version overrides into with-connect flags."""
    release = ".".join(connect_version.split(".")[:2])
    config = {
        **_CONNECT_CONFIGS.get(release, {}),
        **_CONNECT_CONFIGS.get(connect_version, {}),
    }
    return [arg for key, value in config.items() for arg in ("--env", f"{key}={value}")]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="class", autouse=True)
def fresh_connect():
    """Boot a fresh Connect container and expose it via the environment.

    Setup runs before setup_class; the finalizer runs after teardown_class,
    even if it raises.
    """
    version = os.environ["CONNECT_VERSION"]
    port = _free_port()

    result = subprocess.run(
        [
            *_WITH_CONNECT,
            "--version",
            version,
            "--port",
            str(port),
            "--license",
            _LICENSE,
            "--quiet",
            *_connect_env(version),
        ],
        capture_output=True,
        text=True,
        timeout=900,  # the first invocation may pull the Connect image
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"with-connect failed to start Connect {version} on port {port}:\n{result.stderr}"
        )

    creds = dict(line.split("=", 1) for line in result.stdout.splitlines() if "=" in line)

    # Fetch container_id before validating credentials, so a container is still
    # cleaned up in `finally` even if with-connect's output is incomplete.
    container_id = creds.get("CONTAINER_ID")
    try:
        missing = [
            key
            for key in ("CONNECT_SERVER", "CONNECT_API_KEY", "CONTAINER_ID")
            if key not in creds
        ]
        if missing:
            raise RuntimeError(
                f"with-connect start-only output was missing expected credentials: {', '.join(missing)}"
            )

        os.environ["CONNECT_SERVER"] = creds["CONNECT_SERVER"]
        os.environ["CONNECT_API_KEY"] = creds["CONNECT_API_KEY"]
        yield
    finally:
        # `rm` (not `stop`) so per-class containers don't accumulate on disk.
        if container_id is not None:
            stop = subprocess.run(
                ["docker", "rm", "--force", "--volumes", container_id],
                capture_output=True,
                text=True,
                timeout=120,
            )
            if stop.returncode != 0:
                warnings.warn(
                    f"failed to remove Connect container {container_id}: {stop.stderr}",
                    RuntimeWarning,
                    stacklevel=2,
                )
