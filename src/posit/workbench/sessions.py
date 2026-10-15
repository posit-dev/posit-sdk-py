"""Session-related Workbench launcher API methods (launch, resume, inspect, stop, connect)."""

from __future__ import annotations

from typing_extensions import TYPE_CHECKING, Any, Iterable, Protocol

from . import rpc
from .resources import Resource, ResourceSequence, _Resource, _ResourceSequence

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


class Session(Resource, Protocol):
    """A Workbench session with dictionary access and session operations."""

    def resume(
        self,
        *,
        username: str | None = None,
        launch_parameters: LaunchParameters | None = None,
    ) -> LaunchSessionResult:
        """Resume this session, returning the launcher response."""
        ...

    def stop(self, *, force_quit: bool | None = None, suspend: bool | None = None) -> None:
        """Stop, force-quit, or suspend this session."""
        ...

    @property
    def connection_url(self) -> str:
        """The absolute browser URL for this session."""
        ...


class Sessions(ResourceSequence[Session], Protocol):
    """Launch, resume, inspect, stop, and connect to Workbench IDE sessions."""

    def fetch(
        self,
        *,
        session_id: str | list[str] = ...,
        user: str = ...,
        fields: list[str] = ...,
        timestamp: float = ...,
    ) -> Iterable[Session]:
        """Fetch session records without the surrounding projects and jobs.

        Parameters
        ----------
        session_id : str or list[str], optional
            One or more session identifiers.
        user : str, optional
            The user whose sessions to retrieve.
        fields : list[str], optional
            Fields to include in each record.
        timestamp : float, optional
            Return updates since this timestamp.

        Returns
        -------
        Iterable[Session]
            Session records from the launcher response.
        """
        ...

    def find_by(
        self,
        *,
        id: str = ...,  # noqa: A002
        username: str = ...,
        workbench: str = ...,
        activity_state: str = ...,
    ) -> Session | None:
        """Find the first session matching all record fields exactly.

        Conditions apply locally and do not become RPC parameters.

        Parameters
        ----------
        id : str, optional
            The session identifier.
        username : str, optional
            The session owner.
        workbench : str, optional
            The session IDE.
        activity_state : str, optional
            The session activity state.

        Returns
        -------
        Session or None
            The first matching session, or None when no record matches.
        """
        ...

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
        ...

    def resume(
        self,
        session_id: str,
        *,
        username: str | None = None,
        launch_parameters: LaunchParameters | None = None,
    ) -> LaunchSessionResult:
        """Resume a previously suspended session."""
        ...

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
        ...

    def get_historical(
        self,
        *,
        filter_time_begin: str | None = None,
        filter_time_end: str | None = None,
        include_jobs: bool | None = None,
        include_all_users: bool | None = None,
    ) -> GetHistoricalSessionResult:
        """Get ended sessions/jobs, optionally filtered by an end-time range (ISO-8601)."""
        ...

    def stop(
        self,
        session_ids: str | list[str],
        *,
        force_quit: bool | None = None,
        suspend: bool | None = None,
    ) -> None:
        """Stop, force-quit, or suspend one or more sessions."""
        ...

    def connection_url(self, session: WorkbenchSession | LaunchSessionResult | Any) -> str:
        """Resolve a session's relative ``url`` field into an absolute, browsable URL."""
        ...


class _Sessions(_ResourceSequence[Session], Sessions):
    """Launch, resume, inspect, stop, and connect to Workbench IDE sessions."""

    def __init__(self, ctx: ContextProtocol) -> None:
        super().__init__(ctx, "get_session", resource_type=_Session, result_key="sessions")

    def fetch(self, **params: Any) -> Iterable[Session]:
        if "session_id" in params:
            params["session_id"] = _join(params["session_id"])
        return super().fetch(**params)

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
        rpc.call(
            self._ctx.client,
            "stop_session",
            session_ids=_join(session_ids),
            force_quit=force_quit,
            suspend=suspend,
        )

    def connection_url(self, session: WorkbenchSession | LaunchSessionResult | Any) -> str:
        # "url" is always present on a session returned by launch_session/resume_session/
        # get_session in practice, even though the TypedDicts mark it optional (total=False).
        url = session["url"]  # pyright: ignore[reportTypedDictNotRequiredAccess]
        # _ClientProtocol deliberately doesn't declare server_url (rpc.py's functions don't
        # need it) -- both concrete clients have it, so this is safe at runtime.
        client: Any = self._ctx.client
        return client.server_url.append(url)


class _Session(_Resource, Session):
    def resume(
        self,
        *,
        username: str | None = None,
        launch_parameters: LaunchParameters | None = None,
    ) -> LaunchSessionResult:
        return _Sessions(self._ctx).resume(
            self["id"], username=username, launch_parameters=launch_parameters
        )

    def stop(self, *, force_quit: bool | None = None, suspend: bool | None = None) -> None:
        _Sessions(self._ctx).stop(self["id"], force_quit=force_quit, suspend=suspend)

    @property
    def connection_url(self) -> str:
        return _Sessions(self._ctx).connection_url(self)


def _join(value: str | list[str] | None) -> str | None:
    if value is None or isinstance(value, str):
        return value
    return ",".join(value)
