import posixpath
from typing import Any, Literal, Optional, overload

from typing_extensions import NotRequired, Required, TypedDict, Unpack

from .context import Context
from .resources import Active, ActiveFinderMethods, ActiveSequence, Resource

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


class Job(Active):
    class _Job(TypedDict):
        # Identifiers
        id: Required[str]
        """A unique identifier for the job."""

        ppid: Required[Optional[str]]
        """Identifier of the parent process."""

        pid: Required[str]
        """Identifier of the process running the job."""

        key: Required[str]
        """A unique key to identify this job."""

        remote_id: Required[Optional[str]]
        """Identifier for off-host execution configurations."""

        app_id: Required[str]
        """Identifier of the parent content associated with the job."""

        variant_id: Required[str]
        """Identifier of the variant responsible for the job."""

        bundle_id: Required[str]
        """Identifier of the content bundle linked to the job."""

        # Timestamps
        start_time: Required[str]
        """RFC3339 timestamp indicating when the job started."""

        end_time: Required[Optional[str]]
        """RFC3339 timestamp indicating when the job finished."""

        last_heartbeat_time: Required[str]
        """RFC3339 timestamp of the last recorded activity for the job."""

        queued_time: Required[Optional[str]]
        """RFC3339 timestamp when the job was added to the queue."""

        # Status and Exit Information
        status: Required[Literal[0, 1, 2]]
        """Current status. Options are 0 (Active), 1 (Finished), and 2 (Finalized)"""

        exit_code: Required[Optional[int]]
        """The job's exit code, available after completion."""

        # Environment Information
        hostname: Required[str]
        """Name of the node processing the job."""

        cluster: Required[Optional[str]]
        """Location where the job runs, either 'Local' or the cluster name."""

        image: Required[Optional[str]]
        """Location of the content in clustered environments."""

        run_as: Required[str]
        """UNIX user responsible for executing the job."""

        # Queue and Scheduling Information
        queue_name: Required[Optional[str]]
        """Name of the queue processing the job, relevant for scheduled reports."""

        # Job Metadata
        tag: Required[JobTag]
        """A tag categorizing the job type. Options are build_jupyter, build_report, build_site, configure_report, git, packrat_restore, python_restore, render_shiny, run_api, run_app, run_bokeh_app, run_dash_app, run_fastapi_app, run_pyshiny_app, run_python_api, run_streamlit, run_tensorflow, run_voila_app, testing, unknown, val_py_ext_pkg, val_r_ext_pkg, and val_r_install."""

    def __init__(self, ctx: Context, path: str, /, **attributes: Unpack[_Job]):
        super().__init__(ctx, path, **attributes)

    def destroy(self) -> None:
        """Destroy the job.

        Submit a request to kill the job.

        Warnings
        --------
        This operation is irreversible.

        Note
        ----
        This action requires administrator, owner, or collaborator privileges.
        """
        endpoint = self._ctx.url + self._path
        self._ctx.session.delete(endpoint)


class Jobs(ActiveFinderMethods[Job], ActiveSequence[Job]):
    def __init__(self, ctx: Context, path: str):
        """A collection of jobs.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions
        path : str
            The HTTP path component for the jobs endpoint (e.g., 'v1/content/544509fc-e4f0-41de-acb4-1fe3a2c1d797/jobs')
        """
        super().__init__(ctx, path, "key")

    def _create_instance(self, path: str, /, **attributes: Any) -> Job:
        """Creates a Job instance.

        Parameters
        ----------
        path : str
            The HTTP path component for the Job resource endpoint (e.g., 'v1/content/544509fc-e4f0-41de-acb4-1fe3a2c1d797/jobs/7add0bc0-0d89-4397-ab51-90ad4bc3f5c9')

        Returns
        -------
        Job
        """
        return Job(self._ctx, path, **attributes)

    class _FindByRequest(TypedDict, total=False):
        # Identifiers
        id: Required[str]
        """A unique identifier for the job."""

        ppid: NotRequired[Optional[str]]
        """Identifier of the parent process."""

        pid: NotRequired[str]
        """Identifier of the process running the job."""

        key: NotRequired[str]
        """A unique key to identify this job."""

        remote_id: NotRequired[Optional[str]]
        """Identifier for off-host execution configurations."""

        app_id: NotRequired[str]
        """Identifier of the parent content associated with the job."""

        variant_id: NotRequired[str]
        """Identifier of the variant responsible for the job."""

        bundle_id: NotRequired[str]
        """Identifier of the content bundle linked to the job."""

        # Timestamps
        start_time: NotRequired[str]
        """RFC3339 timestamp indicating when the job started."""

        end_time: NotRequired[Optional[str]]
        """RFC3339 timestamp indicating when the job finished."""

        last_heartbeat_time: NotRequired[str]
        """RFC3339 timestamp of the last recorded activity for the job."""

        queued_time: NotRequired[Optional[str]]
        """RFC3339 timestamp when the job was added to the queue."""

        # Status and Exit Information
        status: NotRequired[Literal[0, 1, 2]]
        """Current status. Options are 0 (Active), 1 (Finished), and 2 (Finalized)"""

        exit_code: NotRequired[Optional[int]]
        """The job's exit code, available after completion."""

        # Environment Information
        hostname: NotRequired[str]
        """Name of the node processing the job."""

        cluster: NotRequired[Optional[str]]
        """Location where the job runs, either 'Local' or the cluster name."""

        image: NotRequired[Optional[str]]
        """Location of the content in clustered environments."""

        run_as: NotRequired[str]
        """UNIX user responsible for executing the job."""

        # Queue and Scheduling Information
        queue_name: NotRequired[Optional[str]]
        """Name of the queue processing the job, relevant for scheduled reports."""

        # Job Metadata
        tag: NotRequired[JobTag]
        """A tag categorizing the job type. Options are build_jupyter, build_report, build_site, configure_report, git, packrat_restore, python_restore, render_shiny, run_api, run_app, run_bokeh_app, run_dash_app, run_fastapi_app, run_pyshiny_app, run_python_api, run_streamlit, run_tensorflow, run_voila_app, testing, unknown, val_py_ext_pkg, val_r_ext_pkg, and val_r_install."""

    @overload
    def find_by(self, **conditions: Unpack[_FindByRequest]) -> Optional[Job]:
        """Finds the first record matching the specified conditions.

        There is no implied ordering so if order matters, you should specify it yourself.

        Parameters
        ----------
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
        Optional[Job]
        """

    @overload
    def find_by(self, **conditions): ...

    def find_by(self, **conditions) -> Optional[Job]:
        return super().find_by(**conditions)


class JobsMixin(Active, Resource):
    """Mixin class to add a jobs attribute to a resource."""

    def __init__(self, ctx, path, /, **attributes):
        """Mixin class which adds a `jobs` attribute to the Active Resource.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions
        path : str
            The HTTP path component for the resource endpoint
        **attributes : dict
            Resource attributes passed
        """
        super().__init__(ctx, path, **attributes)

        path = posixpath.join(path, "jobs")
        self.jobs = Jobs(ctx, path)
