"""TypedDicts mirroring the Workbench launcher API's documented data schemas.

These are structural hints only (the client returns plain dicts) -- the API does not version
its schemas strictly, so all fields are marked as not required (`total=False`) to avoid runtime
constraints and only aid static typing / editor autocomplete.
"""

from __future__ import annotations

from typing_extensions import Any, TypedDict


class PlacementConstraint(TypedDict, total=False):
    """A single launcher placement constraint."""

    name: str
    value: str


class ResourceLimit(TypedDict, total=False):
    """A single job/session resource limit.

    Confirmed camelCase against a live get_compute_envs() response (Job/ComputeEnv context);
    the doc's paraphrased table said "max_value"/"default_value", which was wrong.
    """

    type: str
    value: str
    maxValue: str
    defaultValue: str


class LaunchParameters(TypedDict, total=False):
    """Extra launch configuration accepted by launch_session/resume_session."""

    name: str
    cluster: str
    container_image: str
    placement_constraints: list[PlacementConstraint]
    resource_limits: list[ResourceLimit]
    queues: list[str]
    default_image: str
    resource_profile: str
    aws_role_arn: str
    databricks_instance: str
    snowflake_account: str
    snowflake_role: str


class EnvironmentVariable(TypedDict, total=False):
    """A single job/session environment variable."""

    name: str
    value: str


class SessionHook(TypedDict, total=False):
    """A session start/stop hook."""

    exe: str


class LaunchSessionResult(TypedDict, total=False):
    """The result of launch_session/resume_session."""

    id: str
    url: str
    project_id: str


class WorkbenchJob(TypedDict, total=False):
    """A Workbench job (regular or audited)."""

    id: str
    cluster: str
    name: str
    user: str
    exe: str
    args: list[str]
    command: str
    workingDirectory: str
    queues: list[str]
    tags: list[str]
    container: Any
    host: str
    group: str
    status: str
    statusMessage: str
    statusCode: int
    pid: int
    exitCode: int
    stdoutFile: str
    stderrFile: str
    submissionTime: str
    lastUpdateTime: str
    terminatedTime: str
    runningTimestamp: str
    environment: list[EnvironmentVariable]
    placementConstraints: list[PlacementConstraint]
    resourceLimits: list[ResourceLimit]
    metadata: Any


class WorkbenchProject(TypedDict, total=False):
    """A Workbench project, as returned by get_session."""

    name: str
    path: str
    project_paths: list[str]
    canonical_path: str
    display_name: str
    id: str
    last_session_id: str
    last_editor: str
    editors: list[str]
    last_r_version: str
    last_python_version: str
    last_used: Any
    created: Any
    workspace: bool
    rstudioProject: bool
    not_found: bool
    owner: str
    launch_parameters: LaunchParameters


class WorkbenchSession(TypedDict, total=False):
    """A Workbench IDE session."""

    id: str
    username: str
    url: str
    launch_parameters: LaunchParameters
    created: Any
    activity_state: str
    last_state_updated: Any
    label: str
    display_name: str
    status_detail: str
    project: Any
    project_id: str
    running: bool
    working_dir: str
    executing: bool
    save_prompt_required: bool
    last_used: Any
    workbench: str
    job: WorkbenchJob


class GetSessionResult(TypedDict, total=False):
    """The result of get_session."""

    sessions: list[WorkbenchSession]
    jobs: list[WorkbenchJob]
    projects: list[WorkbenchProject]
    timestamp: float


class GetHistoricalSessionResult(TypedDict, total=False):
    """The result of get_historical_session."""

    sessions: list[WorkbenchSession]
    jobs: list[WorkbenchJob]


class JobOutputChunk(TypedDict, total=False):
    """A single streamed chunk from get_job_output."""

    jobId: str
    outputType: str
    output: str


class AuditedJobOutputChunk(TypedDict, total=False):
    """A single streamed (or unwrapped finished-job) chunk from get_audited_job_output."""

    jobId: str
    outputType: str
    output: str
    outputSource: str


class AuditedJobDetails(TypedDict, total=False):
    """The result of get_audited_job_details."""

    script_output: Any
    environment: Any


class WorkbenchIDEInfo(TypedDict, total=False):
    """Per-IDE defaults, as returned by get_compute_envs."""

    default_cluster: str
    default_image: str
    lang: Any


class ComputeEnv(TypedDict, total=False):
    """A single compute environment/cluster, as returned by get_compute_envs."""

    name: str
    type: str
    supportsContainers: bool
    queues: list[str]
    config: list[Any]
    resourceLimits: list[ResourceLimit]
    placementConstraints: list[PlacementConstraint]
    resourceProfiles: list[Any]
    images: list[Any]
    workbenches: Any


class ComputeEnvsResult(TypedDict, total=False):
    """The result of get_compute_envs."""

    clusters: list[ComputeEnv]
    workbenches: Any


class WorkbenchUser(TypedDict, total=False):
    """A single registered Workbench user, as returned by get_users."""

    username: str
    status: str
    isAdmin: bool
    isSuperAdmin: bool
    uid: int
    lastSignIn: str
    created: str


class VersionInfo(TypedDict, total=False):
    """The result of the version method."""

    version: Any
    features: list[str]
