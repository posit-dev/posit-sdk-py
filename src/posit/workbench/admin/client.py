"""Client for the Posit Workbench launcher API, authenticated via a Bearer API token.

Distinct from ``posit.workbench.Client``, which authenticates via a session RPC cookie and only
works inside an active Workbench session. This one works from anywhere -- a laptop, CI, or a
Snakemake driver host -- given a server URL and an API token.
"""

from __future__ import annotations

from requests import Response, Session
from typing_extensions import TYPE_CHECKING, Any, Iterator, Self

from .. import rpc
from ..compute_envs import ComputeEnvs
from ..jobs import Jobs
from ..server import Server
from ..sessions import Sessions
from ..users import Users
from .auth import Auth
from .config import Config
from .context import Context

if TYPE_CHECKING:
    from types import TracebackType


class Client:
    """Client for the Posit Workbench launcher API.

    Parameters
    ----------
    url : str, optional
        Workbench server URL. Falls back to the ``WORKBENCH_SERVER`` environment variable.
    api_key : str, optional
        Workbench API token. Falls back to the ``WORKBENCH_API_KEY`` environment variable.
    timeout : float, optional
        Default request timeout in seconds (default 30). ``requests``' timeout is a per-read
        (not total-request) timeout, so this also bounds each chunk of a streaming response,
        not just non-streaming calls -- without it, a stalled server/network connection hangs
        indefinitely. Override per-call with ``timeout=None`` (or another value) via **kwargs.

    Examples
    --------
    >>> from posit.workbench.admin import Client
    >>> client = Client()  # reads WORKBENCH_SERVER / WORKBENCH_API_KEY
    >>> client.server.version()
    """

    def __init__(
        self,
        url: str | None = None,
        api_key: str | None = None,
        timeout: float | None = 30,
    ) -> None:
        self.cfg = Config(url=url, api_key=api_key)
        self.server_url = self.cfg.url
        session = Session()
        session.auth = Auth(self.cfg)
        self.session = session
        self.timeout = timeout
        self._ctx = Context(self)

    def get(self, path: str, **kwargs: Any) -> Response:
        """Send a GET request."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.get(self.server_url.append(path), **kwargs)

    def post(self, path: str, **kwargs: Any) -> Response:
        """Send a POST request."""
        kwargs.setdefault("timeout", self.timeout)
        return self.session.post(self.server_url.append(path), **kwargs)

    def call(self, method: str, **kwparams: Any) -> Any:
        """Invoke a non-streaming launcher API method and return its ``result``."""
        return rpc.call(self, method, **kwparams)

    def call_stream(self, method: str, **kwparams: Any) -> Iterator[dict[str, Any]]:
        """Invoke a streaming launcher API method, yielding each JSON chunk."""
        return rpc.call_stream(self, method, **kwparams)

    def call_raw(self, method: str, **kwparams: Any) -> dict[str, Any]:
        """Invoke a method whose success response isn't wrapped in ``{"result": ...}``."""
        return rpc.call_raw(self, method, **kwparams)

    @property
    def sessions(self) -> Sessions:
        """The sessions resource manager."""
        return Sessions(self._ctx)

    @property
    def jobs(self) -> Jobs:
        """The jobs resource manager."""
        return Jobs(self._ctx)

    @property
    def compute_envs(self) -> ComputeEnvs:
        """The compute envs resource manager."""
        return ComputeEnvs(self._ctx)

    @property
    def users(self) -> Users:
        """The users resource manager."""
        return Users(self._ctx)

    @property
    def server(self) -> Server:
        """The server resource manager."""
        return Server(self._ctx)

    @property
    def version(self) -> Any:
        """The server version, as a dict (e.g. ``{"major": "2025", "minor": "12"}``)."""
        return self.server.version().get("version")

    def __enter__(self) -> Self:
        """Enter method for using the client as a context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Close the session if it exists."""
        self.session.close()

    def __del__(self) -> None:
        """Close the session when the Client instance is deleted."""
        session = getattr(self, "session", None)
        if session is not None:
            session.close()
