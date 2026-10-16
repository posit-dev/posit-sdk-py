"""Exceptions raised by the Workbench launcher API (sessions/jobs/compute_envs/users/server)."""

from __future__ import annotations

from typing_extensions import Any


class WorkbenchError(Exception):
    """Base class for all errors raised by the Workbench launcher API client."""


class WorkbenchRPCError(WorkbenchError):
    """Raised when the server responds with a JSON-RPC ``{"error": {...}}`` envelope."""

    def __init__(self, code: int, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"Workbench API error {code}: {message}")


class WorkbenchHTTPError(WorkbenchError):
    """Raised when the HTTP request itself fails (e.g. 401, 502, 503)."""

    def __init__(self, status_code: int, body: Any) -> None:
        self.status_code = status_code
        self.body = body
        super().__init__(f"Workbench API HTTP error {status_code}: {body!r}")


class WorkbenchJobNotFoundError(WorkbenchError):
    """Raised when a job can't be found in either the active or the historical job list."""

    def __init__(self, job_id: str) -> None:
        self.job_id = job_id
        super().__init__(
            f"Job {job_id!r} not found in active or historical jobs (it may have ended and "
            "rotated out of the active list while get_historical_session is unauthorized "
            "for this user)"
        )
