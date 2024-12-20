"""Job resources."""

from __future__ import annotations

from typing_extensions import (
    Iterable,
    Literal,
    Protocol,
    runtime_checkable,
)

from .resources import Resource, ResourceSequence

JobTag = Literal[
    "unknown",
    "build_report",
    "build_site",
    "build_jupyter",
    "packrat_restore",
    "python_restore",
    "configure_report",
    "run_app",
    "run_api",
    "run_tensorflow",
    "run_python_api",
    "run_dash_app",
    "run_streamlit",
    "run_bokeh_app",
    "run_fastapi_app",
    "run_pyshiny_app",
    "render_shiny",
    "run_voila_app",
    "testing",
    "git",
    "val_py_ext_pkg",
    "val_r_ext_pkg",
    "val_r_install",
]


StatusCode = Literal[0, 1, 2]


class Job(Resource, Protocol):
    def destroy(self) -> None:
        """Destroy the job.

        Warnings
        --------
        This operation is irreversible.

        Note
        ----
        This action requires administrator, owner, or collaborator privileges.
        """


@runtime_checkable
class Jobs(ResourceSequence[Job], Protocol):
    def fetch(self) -> Iterable[Job]:
        """Fetch all jobs.

        Fetches all jobs from Connect.

        Returns
        -------
        List[Job]
        """
        ...

    def find(self, key: str, /) -> Job:
        """
        Find a Job by its key.

        Fetches the Job from Connect by it's key.

        Parameters
        ----------
        key : str
            The unique identifier of the Job.

        Returns
        -------
        Jobs
        """
        ...

    def find_by(
        self,
        *,
        # Identifiers
        id: str = ...,  # noqa: A002
        ppid: str | None = ...,
        pid: str = ...,
        key: str = ...,
        remote_id: str | None = ...,
        app_id: str = ...,
        variant_id: str = ...,
        bundle_id: str = ...,
        # Timestamps
        start_time: str = ...,
        end_time: str | None = ...,
        last_heartbeat_time: str = ...,
        queued_time: str | None = ...,
        # Status and Exit Information
        status: StatusCode = ...,
        exit_code: int | None = ...,
        # Environment Information
        hostname: str = ...,
        cluster: str | None = ...,
        image: str | None = ...,
        run_as: str = ...,
        queue_name: str | None = ...,
        tag: JobTag = ...,
    ) -> Job | None:
        """Find the first record matching the specified conditions.

        There is no implied ordering, so if order matters, you should specify it yourself.

        id : str, not required
            A unique identifier for the job.
        ppid : Optional[str], not required
            Identifier of the parent process.
        pid : str, not required
            Identifier of the process running the job.
        key : str, not required
            A unique key to identify this job.
        remote_id : Optional[str], not required
            Identifier for off-host execution configurations.
        app_id : str, not required
            Identifier of the parent content associated with the job.
        variant_id : str, not required
            Identifier of the variant responsible for the job.
        bundle_id : str, not required
            Identifier of the content bundle linked to the job.
        start_time : str, not required
            RFC3339 timestamp indicating when the job started.
        end_time : Optional[str], not required
            RFC3339 timestamp indicating when the job finished.
        last_heartbeat_time : str, not required
            RFC3339 timestamp of the last recorded activity for the job.
        queued_time : Optional[str], not required
            RFC3339 timestamp when the job was added to the queue.
        status : int, not required
            Current status. Options are 0 (Active), 1 (Finished), and 2 (Finalized)
        exit_code : Optional[int], not required
            The job's exit code, available after completion.
        hostname : str, not required
            Name of the node processing the job.
        cluster : Optional[str], not required
            Location where the job runs, either 'Local' or the cluster name.
        image : Optional[str], not required
            Location of the content in clustered environments.
        run_as : str, not required
            UNIX user responsible for executing the job.
        queue_name : Optional[str], not required
            Name of the queue processing the job, relevant for scheduled reports.
        tag : JobTag, not required
            A tag categorizing the job type. Options are build_jupyter, build_report, build_site, configure_report, git, packrat_restore, python_restore, render_shiny, run_api, run_app, run_bokeh_app, run_dash_app, run_fastapi_app, run_pyshiny_app, run_python_api, run_streamlit, run_tensorflow, run_voila_app, testing, unknown, val_py_ext_pkg, val_r_ext_pkg, and val_r_install.

        Returns
        -------
        Job | None

        Note
        ----
        This action requires administrator, owner, or collaborator privileges.
        """
        ...
