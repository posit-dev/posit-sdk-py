from typing import Any, Literal, Optional, TypedDict, overload

from typing_extensions import NotRequired, Required, Unpack

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

    @overload
    def __init__(self, ctx: Context, base: str, uid: str, /, **attributes: Unpack[_Job]):
        ...

    @overload
    def __init__(self, ctx: Context, base: str, uid: str, /, **attributes: Any): ...

    def __init__(self, ctx: Context, base: str, uid: str, /, **attributes: Any):
        """A Job.

        A Job represents single execution instance of Content on Connect. Whenever Content runs, whether it's a scheduled report, a script execution, or server processes related to an application, a Job is created to manage and encapsulate that execution.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        base : str
            The base HTTP path for the Job endpoint (e.g., '/jobs')
        uid : str
            The unique identifier
        **attributes
            Object items passed to the base resource dictionary.

        Notes
        -----
        A Job is a reference to a server process on Connect, it is not the process itself. Jobs are executed asynchronously.
        """
        super().__init__(ctx, **attributes)
        self._endpoint = ctx.url + base + uid

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
        self._ctx.session.delete(self._endpoint)


class Jobs(ActiveFinderMethods[Job], ActiveSequence[Job]):
    def __init__(self, ctx: Context, base: str, path: str = "jobs", uid="key"):
        """A collection of jobs.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions
        base : str
            The base HTTP path for the collection endpoint
        name : str
            The collection name, by default "jobs"
        uid : str, optional
            The field name used to uniquely identify records, by default "key"
        """
        super().__init__(ctx, base, path, uid)

    def _create_instance(self, base: str, uid: str, **kwargs: Any) -> Job:
        """Creates a Job instance.

        Parameters
        ----------
        base : str
            The base HTTP path for the instance endpoint
        uid : str
            The unique identifier for the instance.

        Returns
        -------
        Job
        """
        return Job(self._ctx, base, uid, **kwargs)

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
        ...

    @overload
    def find_by(self, **conditions): ...

    def find_by(self, **conditions) -> Optional[Job]:
        return super().find_by(**conditions)


class JobsMixin(Active, Resource):
    """Mixin class to add a jobs attribute to a resource."""

    def __init__(self, ctx: Context, base: str, /, **kwargs):
        """Mixin class which adds a `jobs` attribute to the Active Resource.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions
        base : str
            The base path associated with the instance.
        """
        super().__init__(ctx, **kwargs)
        self.jobs = Jobs(ctx, base)
