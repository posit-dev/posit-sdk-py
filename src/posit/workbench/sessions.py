"""Session-related Workbench launcher API methods (launch, resume, inspect, stop, connect)."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Any

from . import rpc
from .resources import Resources

if TYPE_CHECKING:
    from .rpc import ContextProtocol
    from .types import (
        GetHistoricalSessionResult,
        GetSessionResult,
        LaunchParameters,
        LaunchSessionResult,
        SessionHook,
        WorkbenchSession,
    )


class Sessions(Resources):
    """Launch, resume, inspect, stop, and connect to Workbench IDE sessions."""

    def __init__(self, ctx: ContextProtocol) -> None:
        # Not super().__init__(ctx): Resources.__init__ types ctx as the specific in-session
        # Context, but this manager is shared with the Bearer-token admin.Context too -- see
        # ContextProtocol's docstring in rpc.py.
        self._ctx = ctx

    def launch(
        self,
        workbench: str,
        *,
        username: str | None = None,
        name: str | None = None,
        project_id: str | None = None,
        open_file: str | None = None,
        working_directory: str | None = None,
        launch_parameters: LaunchParameters | None = None,
        start_hooks: list[SessionHook] | None = None,
        stop_hooks: list[SessionHook] | None = None,
        environment: list[dict] | None = None,
    ) -> LaunchSessionResult:
        """Launch a new IDE session for a user.

        See: https://docs.posit.co/ide/server-pro/admin/workbench_api/interface.html#launch_session
        """
        return rpc.call(
            self._ctx.client,
            "launch_session",
            workbench=workbench,
            username=username,
            name=name,
            project_id=project_id,
            open_file=open_file,
            working_directory=working_directory,
            launch_parameters=launch_parameters,
            start_hooks=start_hooks,
            stop_hooks=stop_hooks,
            environment=environment,
        )

    def resume(
        self,
        session_id: str,
        *,
        username: str | None = None,
        launch_parameters: LaunchParameters | None = None,
    ) -> LaunchSessionResult:
        """Resume a previously suspended session."""
        return rpc.call(
            self._ctx.client,
            "resume_session",
            session_id=session_id,
            username=username,
            launch_parameters=launch_parameters,
        )

    def get(
        self,
        session_id: str | list[str] | None = None,
        *,
        user: str | None = None,
        fields: list[str] | None = None,
        timestamp: float | None = None,
        include_projects: bool | None = None,
        include_jobs: bool | None = None,
        include_all_jobs: bool | None = None,
    ) -> GetSessionResult:
        """Get session/job/project info.

        With no ``session_id``, returns all of the caller's sessions.
        """
        return rpc.call(
            self._ctx.client,
            "get_session",
            session_id=_join(session_id),
            user=user,
            fields=fields,
            timestamp=timestamp,
            include_projects=include_projects,
            include_jobs=include_jobs,
            include_all_jobs=include_all_jobs,
        )

    def get_historical(
        self,
        *,
        filter_time_begin: str | None = None,
        filter_time_end: str | None = None,
        include_jobs: bool | None = None,
        include_all_users: bool | None = None,
    ) -> GetHistoricalSessionResult:
        """Get ended sessions/jobs, optionally filtered by an end-time range (ISO-8601)."""
        return rpc.call(
            self._ctx.client,
            "get_historical_session",
            filter_time_begin=filter_time_begin,
            filter_time_end=filter_time_end,
            include_jobs=include_jobs,
            include_all_users=include_all_users,
        )

    def stop(
        self,
        session_ids: str | list[str],
        *,
        force_quit: bool | None = None,
        suspend: bool | None = None,
    ) -> None:
        """Stop, force-quit, or suspend one or more sessions."""
        rpc.call(
            self._ctx.client,
            "stop_session",
            session_ids=_join(session_ids),
            force_quit=force_quit,
            suspend=suspend,
        )

    def connection_url(self, session: WorkbenchSession | LaunchSessionResult | Any) -> str:
        """Resolve a session's relative ``url`` field into an absolute, browsable URL."""
        # "url" is always present on a session returned by launch_session/resume_session/
        # get_session in practice, even though the TypedDicts mark it optional (total=False).
        url = session["url"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        # _ClientProtocol deliberately doesn't declare server_url (rpc.py's functions don't
        # need it) -- both concrete clients have it, so this is safe at runtime.
        client: Any = self._ctx.client
        return client.server_url.append(url)


def _join(value: str | list[str] | None) -> str | None:
    if value is None or isinstance(value, str):
        return value
    return ",".join(value)
