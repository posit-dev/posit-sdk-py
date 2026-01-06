"""Reads RPC Cookie from known location within Posit Workbench sessions."""

from __future__ import annotations

import os
from datetime import datetime, timezone

PWB_SESSION_RUNTIME_DIR_ENV = "PWB_SESSION_RUNTIME_DIR"
RPC_COOKIE_FILE = "rpc_cookie"
RS_SESSION_RPC_COOKIE_ENV = "RS_SESSION_RPC_COOKIE"


class CookieReader:
    """Reads the RPC authentication cookie from the Posit Workbench session runtime directory."""

    def __init__(self, runtime_dir: str = "") -> None:
        self.runtime_dir = runtime_dir
        self.cookie_value = None
        self.expiry_time = None
        self._load_cookie()

    def _load_cookie(self):
        # Try to read from file first
        cookie_from_file = self._read_cookie_from_file()

        # Fall back to environment variable if file reading fails
        if cookie_from_file is None:
            cookie_from_env = os.environ.get(RS_SESSION_RPC_COOKIE_ENV)
            if cookie_from_env:
                self.cookie_value = cookie_from_env
            else:
                raise RuntimeError(
                    f"RPC cookie not found. Ensure either {PWB_SESSION_RUNTIME_DIR_ENV} is set "
                    f"with a valid cookie file, or {RS_SESSION_RPC_COOKIE_ENV} environment variable is defined."
                )
        else:
            self.cookie_value = cookie_from_file

        self.expiry_time = self._parse_cookie_expiry(self.cookie_value)
        if self.expiry_time is None:
            self.cookie_value = None
            raise RuntimeError("Could not parse expiry time from RPC cookie.")

    def _read_cookie_from_file(self) -> str | None:
        """Attempts to read the cookie from the runtime directory file. Returns None if not available."""
        if not self.runtime_dir:
            self.runtime_dir = os.environ.get(PWB_SESSION_RUNTIME_DIR_ENV)
            if not self.runtime_dir:
                return None

        cookie_path = f"{self.runtime_dir}/{RPC_COOKIE_FILE}"
        try:
            with open(cookie_path, "r") as cookie_file:
                return cookie_file.read().strip()
        except FileNotFoundError:
            return None
        except Exception:
            return None

    def _parse_cookie_expiry(self, cookie_str: str) -> datetime | None:
        """
        Parses the expiry time from the cookie string.

        Returns the expiry time as a datetime object, or None if not found.
        """
        parts = cookie_str.split("|")
        if len(parts) < 2:
            return None
        expiry_str = parts[1].replace("%2C", ",").replace("%20", " ").replace("%3A", ":")
        try:
            expiry_time = datetime.strptime(expiry_str, "%a, %d %b %Y %H:%M:%S GMT")
            return expiry_time.replace(tzinfo=timezone.utc)
        except ValueError:
            return None

    def get_cookie(self) -> str | None:
        """Returns the RPC cookie value if valid, else None."""
        if self.expiry_time and datetime.now(timezone.utc) < self.expiry_time:
            return self.cookie_value

        self._load_cookie()
        return self.cookie_value
