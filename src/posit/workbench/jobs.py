"""Job-related Workbench launcher API methods (launch, stop, output) for regular and audited jobs."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing_extensions import TYPE_CHECKING, Any, Iterator, cast

from . import rpc
from .errors import WorkbenchHTTPError
from .resources import Resources

if TYPE_CHECKING:
    from .rpc import ContextProtocol
    from .types import AuditedJobDetails, AuditedJobOutputChunk, JobOutputChunk, WorkbenchJob

# Terminal WorkbenchJob "status" values, per the API's documented enum
# (Pending/Canceled/Running/Suspended/Failed/Finished/Killed) -- "Suspended" is treated as
# non-terminal since it's a session-oriented state, not a job end state.
_TERMINAL_JOB_STATUSES = frozenset({"Canceled", "Failed", "Finished", "Killed"})


@dataclass
class JobResult:
    """The outcome of a job that has reached a terminal state."""

    job: WorkbenchJob
    exit_code: int | None
    status: str | None
    error_message: str | None
    stdout: str = ""
    stderr: str = ""


class Jobs(Resources):
    """Launch, stop, and fetch output/details for Workbench jobs (regular and audited)."""

    def __init__(self, ctx: ContextProtocol) -> None:
        # Not super().__init__(ctx): Resources.__init__ types ctx as the specific in-session
        # Context, but this manager is shared with the Bearer-token admin.Context too -- see
        # ContextProtocol's docstring in rpc.py.
        self._ctx = ctx

    def _build_job(
        self,
        cluster: str,
        name: str,
        exe: str,
        args: list[str] | None,
        *,
        working_directory: str | None,
        environment: list[dict] | None,
        tags: list[str] | None,
        container: dict | None,
        resource_limits: list[dict] | None,
        queues: list[str] | None,
        placement_constraints: list[dict] | None,
        user: str | None,
    ) -> dict[str, Any]:
        # Unlike the Session API (snake_case throughout, e.g. launch_parameters), the Job
        # Launcher API's job object is camelCase -- confirmed by live get_compute_envs()
        # output ("defaultValue"/"maxValue") and the doc's launch_job result example
        # ("workingDirectory"/"resourceLimits"/"placementConstraints").
        job: dict[str, Any] = {"cluster": cluster, "name": name, "exe": exe}
        if args is not None:
            job["args"] = args
        if working_directory is not None:
            job["workingDirectory"] = working_directory
        if environment is not None:
            job["environment"] = environment
        if tags is not None:
            job["tags"] = tags
        if container is not None:
            job["container"] = container
        if resource_limits is not None:
            job["resourceLimits"] = resource_limits
        if queues is not None:
            job["queues"] = queues
        if placement_constraints is not None:
            job["placementConstraints"] = placement_constraints
        if user is not None:
            job["user"] = user
        return job

    def launch(
        self,
        cluster: str,
        name: str,
        exe: str,
        args: list[str] | None = None,
        *,
        working_directory: str | None = None,
        environment: list[dict] | None = None,
        tags: list[str] | None = None,
        container: dict | None = None,
        resource_limits: list[dict] | None = None,
        queues: list[str] | None = None,
        placement_constraints: list[dict] | None = None,
        user: str | None = None,
        apply_config_settings: bool | None = None,
    ) -> WorkbenchJob:
        """Launch a (non-audited) Workbench job."""
        job = self._build_job(
            cluster,
            name,
            exe,
            args,
            working_directory=working_directory,
            environment=environment,
            tags=tags,
            container=container,
            resource_limits=resource_limits,
            queues=queues,
            placement_constraints=placement_constraints,
            user=user,
        )
        result = rpc.call(
            self._ctx.client,
            "launch_job",
            job=job,
            apply_config_settings=apply_config_settings,
        )
        # Assumes the result envelope echoes the job back under a "job" key, mirroring the
        # "job" kwparam key; verify against a live server if this ever mismatches.
        return result["job"]

    def launch_audited(
        self,
        cluster: str,
        name: str,
        exe: str,
        args: list[str] | None = None,
        *,
        working_directory: str | None = None,
        environment: list[dict] | None = None,
        tags: list[str] | None = None,
        container: dict | None = None,
        resource_limits: list[dict] | None = None,
        queues: list[str] | None = None,
        placement_constraints: list[dict] | None = None,
        user: str | None = None,
        apply_config_settings: bool | None = None,
    ) -> WorkbenchJob:
        """Launch an audited Workbench job.

        A container image is required for containerized jobs.
        """
        audited_job = self._build_job(
            cluster,
            name,
            exe,
            args,
            working_directory=working_directory,
            environment=environment,
            tags=tags,
            container=container,
            resource_limits=resource_limits,
            queues=queues,
            placement_constraints=placement_constraints,
            user=user,
        )
        result = rpc.call(
            self._ctx.client,
            "launch_audited_job",
            audited_job=audited_job,
            apply_config_settings=apply_config_settings,
        )
        # Assumes the result envelope echoes the job back under an "audited_job" key,
        # mirroring the "audited_job" kwparam key; verify against a live server if this
        # ever mismatches.
        return result["audited_job"]

    def launch_and_wait(
        self,
        cluster: str,
        name: str,
        exe: str,
        args: list[str] | None = None,
        *,
        working_directory: str | None = None,
        environment: list[dict] | None = None,
        tags: list[str] | None = None,
        container: dict | None = None,
        resource_limits: list[dict] | None = None,
        queues: list[str] | None = None,
        placement_constraints: list[dict] | None = None,
        user: str | None = None,
        apply_config_settings: bool | None = None,
        poll_interval: float = 2.0,
        timeout: float | None = None,
        capture_output: bool = True,
    ) -> JobResult:
        """Launch a (non-audited) job and block until it reaches a terminal state.

        If ``capture_output`` is set (the default), first drains ``get_output`` for the job --
        which streams until the job's process ends -- collecting stdout/stderr into the
        returned result. It then polls ``get_session``/``get_historical_session`` every
        ``poll_interval`` seconds for the job's final status (normally just once, since the
        output stream closing already means the job has ended). Raises ``TimeoutError`` if
        ``timeout`` elapses first; note ``timeout`` only bounds the status poll, not the
        output-draining step.

        Returns
        -------
        JobResult
            ``exit_code``, ``error_message`` (from the job's ``statusMessage``, if the job
            didn't finish cleanly), ``stdout``/``stderr`` (if captured), and the full raw job
            dict.
        """
        job = self.launch(
            cluster,
            name,
            exe,
            args,
            working_directory=working_directory,
            environment=environment,
            tags=tags,
            container=container,
            resource_limits=resource_limits,
            queues=queues,
            placement_constraints=placement_constraints,
            user=user,
            apply_config_settings=apply_config_settings,
        )

        # "id" is always present on a job returned by launch_job in practice, even though
        # WorkbenchJob marks it optional (total=False).
        job_id = job["id"]  # pyright: ignore[reportTypedDictNotRequiredAccess]

        stdout = ""
        stderr = ""
        if capture_output:
            stdout, stderr = self._collect_output(job_id, user=user)

        result = self._wait_for_terminal_status(
            job_id,
            user=user,
            poll_interval=poll_interval,
            timeout=timeout,
        )
        result.stdout = stdout
        result.stderr = stderr
        return result

    def _collect_output(self, job_id: str, *, user: str | None) -> tuple[str, str]:
        stdout_chunks: list[str] = []
        stderr_chunks: list[str] = []
        for chunk in self.get_output(job_id, user=user):
            text = chunk.get("output", "")
            if chunk.get("outputType") == "stderr":
                stderr_chunks.append(text)
            else:
                stdout_chunks.append(text)
        return "".join(stdout_chunks), "".join(stderr_chunks)

    def get_status_map(
        self,
        *,
        user: str | None = None,
        include_historical: bool = True,
    ) -> dict[str, WorkbenchJob]:
        """Fetch all known jobs in one (or two) round-trips, keyed by job id.

        Meant for checking many jobs' status at once -- e.g. a Snakemake executor's
        active-job poll -- with a single ``get_session`` call (plus one
        ``get_historical_session`` call, unless ``include_historical=False``) instead of one
        call per job.

        On an id collision, the active-job entry wins over the historical one.

        ``get_historical_session`` requires broader session-visibility privileges than plain
        self-service job launching does -- confirmed live: a regular user's in-session cookie
        can ``launch_job``/``get_session`` for themselves but gets HTTP 401 from
        ``get_historical_session``, while a Bearer token for an account with elevated
        visibility does not. Rather than let that break status polling for ordinary users, a
        401/403 here is treated the same as ``include_historical=False`` -- silently degrading
        to active-job-only status, at the cost of no longer catching jobs that finish and
        rotate out of the active list before the next poll.
        """
        statuses: dict[str, WorkbenchJob] = {}

        if include_historical:
            try:
                historical = rpc.call(
                    self._ctx.client, "get_historical_session", include_jobs=True
                )
            except WorkbenchHTTPError as e:
                if e.status_code not in (401, 403):
                    raise
            else:
                for candidate in historical.get("jobs") or []:
                    job_id = candidate.get("id")
                    if job_id is not None:
                        statuses[job_id] = candidate

        # Adhoc jobs (launched via launch_job) aren't tied to a session, so include_all_jobs
        # is required to see them via get_session. Populated after historical so active
        # entries take precedence on id collision.
        active = rpc.call(self._ctx.client, "get_session", user=user, include_all_jobs=True)
        for candidate in active.get("jobs") or []:
            job_id = candidate.get("id")
            if job_id is not None:
                statuses[job_id] = candidate

        return statuses

    def _find_job(self, job_id: str, *, user: str | None) -> WorkbenchJob | None:
        # Adhoc jobs (launched via launch_job) aren't tied to a session, so include_all_jobs
        # is required to see them via get_session.
        active = rpc.call(self._ctx.client, "get_session", user=user, include_all_jobs=True)
        for candidate in active.get("jobs") or []:
            if candidate.get("id") == job_id:
                return candidate

        # A quick job may have already finished and rotated out of the active list by the
        # time we first poll -- fall back to historical jobs before giving up.
        historical = rpc.call(self._ctx.client, "get_historical_session", include_jobs=True)
        for candidate in historical.get("jobs") or []:
            if candidate.get("id") == job_id:
                return candidate

        return None

    def _wait_for_terminal_status(
        self,
        job_id: str,
        *,
        user: str | None,
        poll_interval: float,
        timeout: float | None,
    ) -> JobResult:
        start = time.monotonic()
        while True:
            job = self._find_job(job_id, user=user)
            if job is not None and job.get("status") in _TERMINAL_JOB_STATUSES:
                return JobResult(
                    job=job,
                    exit_code=job.get("exitCode"),
                    status=job.get("status"),
                    error_message=job.get("statusMessage") or None,
                )
            if timeout is not None and time.monotonic() - start >= timeout:
                raise TimeoutError(f"Timed out waiting for job {job_id!r} to finish")
            time.sleep(poll_interval)

    def stop(self, job_id: str, *, force_quit: bool | None = None) -> None:
        """Stop a running job.

        ``force_quit=True`` sends ``kill -9`` instead of ``kill``.
        """
        rpc.call(self._ctx.client, "stop_job", job_id=job_id, force_quit=force_quit)

    def stop_audited(self, audited_job_id: str, *, force_quit: bool | None = None) -> None:
        """Stop a running audited job."""
        rpc.call(
            self._ctx.client,
            "stop_audited_job",
            audited_job_id=audited_job_id,
            force_quit=force_quit,
        )

    def get_output(
        self,
        job_id: str,
        *,
        user: str | None = None,
    ) -> Iterator[JobOutputChunk]:
        """Stream stdout/stderr chunks for a live or recently-finished job."""
        chunks = rpc.call_stream(self._ctx.client, "get_job_output", job_id=job_id, user=user)
        return cast("Iterator[JobOutputChunk]", chunks)

    def get_audited_output(
        self,
        audited_job_id: str,
        *,
        user: str | None = None,
    ) -> Iterator[AuditedJobOutputChunk]:
        """Get output for an audited job.

        Yields one or more chunks: multiple bare streamed chunks for a live job, or a single
        combined-output chunk (unwrapped from the ``result``/``audited_job_output`` envelope)
        if the job has already finished.
        """
        for chunk in rpc.call_stream(
            self._ctx.client,
            "get_audited_job_output",
            audited_job_id=audited_job_id,
            user=user,
        ):
            if "result" in chunk:
                result = chunk["result"]
                yield cast("AuditedJobOutputChunk", result.get("audited_job_output", result))
            else:
                yield cast("AuditedJobOutputChunk", chunk)

    def get_audited_details(
        self,
        audited_job_id: str,
        *,
        user: str | None = None,
    ) -> AuditedJobDetails:
        """Get audit details (script output, environment info) for a completed audited job."""
        result = rpc.call(
            self._ctx.client,
            "get_audited_job_details",
            audited_job_id=audited_job_id,
            user=user,
        )
        # The doc's example nests the details under an "audited_details" key; fall back to the
        # raw result if a future/actual server returns the fields unwrapped.
        return result.get("audited_details", result)
