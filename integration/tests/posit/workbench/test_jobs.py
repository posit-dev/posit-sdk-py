# The SDK's response TypedDicts are total=False; these tests index keys a live server returns.
# pyright: reportTypedDictNotRequiredAccess=false

from __future__ import annotations

import time

import pytest

from posit.workbench import admin
from posit.workbench.jobs import _TERMINAL_JOB_STATUSES

from . import CLUSTER, RESOURCE_PROFILE, TAG, WORKBENCH_USER


def _bash(script: str) -> dict:
    """Common launch arguments for a bash job on the Local cluster."""
    return {
        "cluster": CLUSTER,
        "exe": "/bin/bash",
        "args": ["-c", script],
        "tags": [TAG],
        "resource_profile": RESOURCE_PROFILE,
    }


def _find_job(client, job_id: str) -> dict | None:
    """Find a job by launcher job id, or by audited job id.

    Audited jobs are listed under their own launcher job id, tagged with the audited job id.
    """
    statuses = client.jobs.get_status_map()
    if job_id in statuses:
        return statuses[job_id]
    tag = f"pwb-audited-job-id:{job_id}"
    return next((job for job in statuses.values() if tag in (job.get("tags") or [])), None)


def _wait_for_status(client, job_id: str, statuses, timeout: float = 60) -> dict:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        job = _find_job(client, job_id)
        if job is not None and job.get("status") in statuses:
            return job
        time.sleep(1)
    pytest.fail(f"Job {job_id} did not reach any of {sorted(statuses)} within {timeout}s")


def _wait_for_terminal(client, job_id: str, timeout: float = 60) -> dict:
    return _wait_for_status(client, job_id, _TERMINAL_JOB_STATUSES, timeout)


class TestJobs:
    @classmethod
    def setup_class(cls):
        cls.client = admin.Client()

    @classmethod
    def teardown_class(cls):
        for job in cls.client.jobs.get_status_map().values():
            if TAG in (job.get("tags") or []) and job.get("status") == "Running":
                cls.client.jobs.stop(job["id"], force_quit=True)

    def test_launch(self):
        job = self.client.jobs.launch(name="it-launch", **_bash("true"))
        assert job["id"]
        assert job["status"] == "Pending"
        assert job["user"] == WORKBENCH_USER
        assert job["submissionTime"]
        assert TAG in job["tags"]
        _wait_for_terminal(self.client, job["id"])

    def test_launch_and_wait_captures_output(self):
        result = self.client.jobs.launch_and_wait(
            name="it-output",
            **_bash("echo hello; echo oops >&2"),
            poll_interval=1,
            timeout=120,
        )
        assert result.status == "Finished"
        assert result.exit_code == 0
        assert result.stdout == "hello\n"
        # Only check that stderr was captured separately: inside a container, the launcher's
        # own cgroup warning and the job's stderr overwrite each other in the stderr file, so
        # the server returns garbled stderr content even after the job has finished.
        assert result.stderr
        assert "oops" not in result.stdout

    def test_launch_and_wait_reports_exit_code(self):
        result = self.client.jobs.launch_and_wait(
            name="it-exit-code",
            **_bash("exit 3"),
            poll_interval=1,
            timeout=120,
            capture_output=False,
        )
        assert result.exit_code == 3
        assert result.stdout == ""

    def test_launch_and_wait_as_token_user(self):
        result = self.client.jobs.launch_and_wait(
            name="it-user",
            **_bash("id -un"),
            user=WORKBENCH_USER,
            poll_interval=1,
            timeout=120,
        )
        assert result.stdout == f"{WORKBENCH_USER}\n"

    def test_get_output_streams_chunks(self):
        job = self.client.jobs.launch(name="it-stream", **_bash("echo one; echo two"))
        chunks = list(self.client.jobs.get_output(job["id"]))
        stdout = "".join(c["output"] for c in chunks if c.get("outputType") == "stdout")
        assert stdout == "one\ntwo\n"

    def test_stop(self):
        job = self.client.jobs.launch(name="it-stop", **_bash("sleep 300"))
        # The launcher refuses to stop a job that isn't running yet (HTTP 409).
        _wait_for_status(self.client, job["id"], {"Running"})
        self.client.jobs.stop(job["id"])
        _wait_for_terminal(self.client, job["id"])

    def test_get_status_map(self):
        job = self.client.jobs.launch(name="it-status-map", **_bash("true"))
        _wait_for_terminal(self.client, job["id"])

        assert job["id"] in self.client.jobs.get_status_map()
        assert job["id"] in self.client.jobs.get_status_map(user=WORKBENCH_USER)
        assert job["id"] in self.client.jobs.get_status_map(
            filter_time_begin=job["submissionTime"]
        )
        assert job["id"] in self.client.jobs.get_status_map(include_historical=False)


class TestAuditedJobs:
    @classmethod
    def setup_class(cls):
        cls.client = admin.Client()

    def test_launch_audited(self):
        job = self.client.jobs.launch_audited(name="it-audited", **_bash("echo audited"))
        assert job["id"]
        _wait_for_terminal(self.client, job["id"])

        # Only the shape is checked, not the content: for a finished audited job the server
        # returns a single stored chunk -- whichever stream was written first, which inside a
        # container is often the launcher's cgroup warning on stderr rather than the job's
        # stdout (observed on 2026.10.0, regardless of output_type).
        chunks = list(self.client.jobs.get_audited_output(job["id"]))
        assert chunks
        for chunk in chunks:
            assert chunk["outputType"] in ("stdout", "stderr")
            assert "output" in chunk

        details = self.client.jobs.get_audited_details(job["id"])
        assert "script_output" in details
        assert "environment" in details

    def test_stop_audited(self):
        job = self.client.jobs.launch_audited(name="it-audited-stop", **_bash("sleep 300"))
        # As with regular jobs, a stop sent before the job is running has no effect.
        _wait_for_status(self.client, job["id"], {"Running"})
        self.client.jobs.stop_audited(job["id"])
        _wait_for_terminal(self.client, job["id"])
