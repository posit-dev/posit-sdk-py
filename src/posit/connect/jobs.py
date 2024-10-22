from typing import List, Literal, Optional, Sequence, TypedDict, overload

from typing_extensions import NotRequired, Required, Unpack

from .errors import ClientError
from .resources import FinderMethods, Resource, ResourceParameters, Resources

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


class Job(Resource):
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

    def __init__(self, /, params, endpoint, **kwargs: Unpack[_Job]):
        super().__init__(params, **kwargs)
        key = kwargs["key"]
        self._endpoint = endpoint + key

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
        self.params.session.delete(self._endpoint)


class Jobs(FinderMethods[Job], Sequence[Job], Resources):
    """A collection of jobs."""

    def __init__(self, params, endpoint):
        super().__init__(Job, params, endpoint)
        self._endpoint = endpoint + "jobs"
        self._cache = None

    @property
    def _data(self) -> List[Job]:
        if self._cache:
            return self._cache

        response = self.params.session.get(self._endpoint)
        results = response.json()
        self._cache = [Job(self.params, self._endpoint, **result) for result in results]
        return self._cache

    def __getitem__(self, index):
        """Retrieve an item or slice from the sequence."""
        return self._data[index]

    def __len__(self):
        """Return the length of the sequence."""
        return len(self._data)

    def __repr__(self):
        """Return the string representation of the sequence."""
        return f"Jobs({', '.join(map(str, self._data))})"

    def count(self, value):
        """Return the number of occurrences of a value in the sequence."""
        return self._data.count(value)

    def index(self, value, start=0, stop=None):
        """Return the index of the first occurrence of a value in the sequence."""
        if stop is None:
            stop = len(self._data)
        return self._data.index(value, start, stop)

    class _FindByRequest(TypedDict, total=False):
        # Identifiers
        id: NotRequired[str]
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

    def find_by(self, **conditions):
        if "key" in conditions and self._cache is None:
            key = conditions["key"]
            try:
                return self.find(key)
            except ClientError as e:
                if e.http_status == 404:
                    return None
                raise e

        return super().find_by(**conditions)

    def reload(self) -> "Jobs":
        """Unload the cached jobs.

        Forces the next access, if any, to query the jobs from the Connect server.
        """
        self._cache = None
        return self


class JobsMixin(Resource):
    """Mixin class to add a jobs attribute to a resource."""

    class HasGuid(TypedDict):
        """Has a guid."""

        guid: Required[str]

    def __init__(self, params: ResourceParameters, **kwargs: Unpack[HasGuid]):
        super().__init__(params, **kwargs)
        uid = kwargs["guid"]
        endpoint = self.params.url + f"v1/content/{uid}"
        self.jobs = Jobs(self.params, endpoint)
