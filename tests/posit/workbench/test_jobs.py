"""Tests for the shared Jobs resource manager."""

import json

import pytest
import responses

from posit.workbench.errors import WorkbenchHTTPError
from posit.workbench.jobs import Jobs
from posit.workbench.urls import Url

SERVER_URL = "https://workbench.example.com"


class _FakeClient:
    """Minimal stand-in exposing just what the shared resource managers need."""

    def __init__(self, server_url: str = SERVER_URL):
        import requests

        self.server_url = Url(server_url)
        self.session = requests.Session()

    def post(self, path, **kwargs):
        """Post to the fake server, joining the base URL and path."""
        return self.session.post(f"{self.server_url}/{path}", **kwargs)


class _FakeContext:
    """Minimal stand-in for either concrete client's Context."""

    def __init__(self, client=None):
        self.client = client or _FakeClient()


def _api_url(method: str) -> str:
    return f"{SERVER_URL}/api/{method}"


def _jobs() -> Jobs:
    return Jobs(_FakeContext())


class TestLaunch:
    """Tests for Jobs.launch()."""

    @responses.activate
    def test_launch(self):
        """launch_job returns the launched job, and sends camelCase-free basic fields as-is."""
        responses.add(
            responses.POST,
            _api_url("launch_job"),
            json={
                "result": {
                    "job": {
                        "id": "abc",
                        "cluster": "Local",
                        "name": "JobTest.R",
                        "status": "Pending",
                    }
                }
            },
            status=200,
        )
        job = _jobs().launch("Local", "Job Test", "R", ["-f", "JobTest.R"])
        assert job["status"] == "Pending"  # pyright: ignore[reportTypedDictNotRequiredAccess]
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["kwparams"]["job"] == {
            "cluster": "Local",
            "name": "Job Test",
            "exe": "R",
            "args": ["-f", "JobTest.R"],
        }

    @responses.activate
    def test_sends_camel_case_job_fields(self):
        """Regression test: the job object's multi-word fields must stay camelCase on the wire.

        Confirmed against a live server (and the doc's launch_job result example): unlike the
        Session API (snake_case throughout), the Job Launcher API's job object is camelCase
        (workingDirectory/resourceLimits/placementConstraints). Sending snake_case here doesn't
        error -- the server silently ignores the fields and falls back to cluster defaults.
        """
        responses.add(
            responses.POST,
            _api_url("launch_job"),
            json={"result": {"job": {"id": "abc", "status": "Pending"}}},
            status=200,
        )
        _jobs().launch(
            "Local",
            "Job Test",
            "R",
            working_directory="/home/michael",
            resource_limits=[{"type": "cpuCount", "value": "2"}],
            placement_constraints=[{"name": "zone", "value": "us-east-1"}],
        )
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        job_body = body["kwparams"]["job"]
        assert job_body["workingDirectory"] == "/home/michael"
        assert job_body["resourceLimits"] == [{"type": "cpuCount", "value": "2"}]
        assert job_body["placementConstraints"] == [{"name": "zone", "value": "us-east-1"}]
        assert "working_directory" not in job_body
        assert "resource_limits" not in job_body
        assert "placement_constraints" not in job_body


class TestLaunchAudited:
    """Tests for Jobs.launch_audited()."""

    @responses.activate
    def test_launch_audited(self):
        """launch_audited_job returns the launched audited job."""
        responses.add(
            responses.POST,
            _api_url("launch_audited_job"),
            json={"result": {"audited_job": {"id": "abc", "status": "Pending"}}},
            status=200,
        )
        job = _jobs().launch_audited(
            "Kubernetes",
            "Job Test",
            "R",
            ["-f", "JobTest.R"],
            container={"image": "posit/r-base:4.3-jammy"},
        )
        assert job["id"] == "abc"  # pyright: ignore[reportTypedDictNotRequiredAccess]
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["kwparams"]["audited_job"]["container"] == {
            "image": "posit/r-base:4.3-jammy"
        }


class TestStop:
    """Tests for Jobs.stop() and Jobs.stop_audited()."""

    @responses.activate
    def test_stop(self):
        """stop_job sends the job id and force_quit flag."""
        responses.add(responses.POST, _api_url("stop_job"), json={"result": None}, status=200)
        _jobs().stop("id1", force_quit=True)
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["kwparams"] == {"job_id": "id1", "force_quit": True}

    @responses.activate
    def test_stop_audited(self):
        """stop_audited_job sends the audited job id."""
        responses.add(
            responses.POST, _api_url("stop_audited_job"), json={"result": None}, status=200
        )
        _jobs().stop_audited("id1")
        body = json.loads(responses.calls[0].request.body)  # pyright: ignore[reportArgumentType]
        assert body["kwparams"] == {"audited_job_id": "id1"}


class TestGetOutput:
    """Tests for Jobs.get_output() and Jobs.get_audited_output()."""

    @responses.activate
    def test_get_output_streams_chunks(self):
        """get_job_output yields each streamed stdout/stderr chunk."""
        body = "\n".join(
            [
                json.dumps({"jobId": "j1", "outputType": "stdout", "output": "A chunk"}),
                json.dumps({"jobId": "j1", "outputType": "stderr", "output": "An error chunk"}),
            ]
        )
        responses.add(responses.POST, _api_url("get_job_output"), body=body, status=200)
        chunks = list(_jobs().get_output("j1"))
        assert chunks[0]["outputType"] == "stdout"  # pyright: ignore[reportTypedDictNotRequiredAccess]
        assert chunks[1]["outputType"] == "stderr"  # pyright: ignore[reportTypedDictNotRequiredAccess]

    @responses.activate
    def test_get_audited_output_finished_job_unwraps_envelope(self):
        """A finished audited job's single combined chunk is unwrapped from its envelope."""
        body = json.dumps(
            {
                "result": {
                    "audited_job_output": {
                        "jobId": "aj1",
                        "outputType": "stdout",
                        "output": "The entire job output",
                        "outputSource": "audit_details_store",
                    }
                }
            }
        )
        responses.add(responses.POST, _api_url("get_audited_job_output"), body=body, status=200)
        chunks = list(_jobs().get_audited_output("aj1"))
        assert chunks == [
            {
                "jobId": "aj1",
                "outputType": "stdout",
                "output": "The entire job output",
                "outputSource": "audit_details_store",
            }
        ]

    @responses.activate
    def test_get_audited_output_live_job_yields_bare_chunks(self):
        """A live audited job's streamed chunks are yielded as-is (no envelope)."""
        body = json.dumps(
            {
                "jobId": "aj1",
                "outputType": "stdout",
                "output": "A chunk",
                "outputSource": "job_launcher",
            }
        )
        responses.add(responses.POST, _api_url("get_audited_job_output"), body=body, status=200)
        chunks = list(_jobs().get_audited_output("aj1"))
        assert chunks[0]["outputSource"] == "job_launcher"  # pyright: ignore[reportTypedDictNotRequiredAccess]


class TestGetAuditedDetails:
    """Tests for Jobs.get_audited_details()."""

    @responses.activate
    def test_get_audited_details(self):
        """get_audited_job_details unwraps the audited_details envelope."""
        responses.add(
            responses.POST,
            _api_url("get_audited_job_details"),
            json={
                "result": {
                    "audited_details": {
                        "script_output": {"checksum": "kFe4sdpdad"},
                        "environment": {"summary": "..."},
                    }
                }
            },
            status=200,
        )
        details = _jobs().get_audited_details("aj1")
        assert details["script_output"]["checksum"] == "kFe4sdpdad"  # pyright: ignore[reportTypedDictNotRequiredAccess]


class TestGetStatusMap:
    """Tests for Jobs.get_status_map()."""

    @responses.activate
    def test_merges_active_and_historical(self):
        """Active and historical jobs are merged into a single id-keyed dict."""
        responses.add(
            responses.POST,
            _api_url("get_historical_session"),
            json={"result": {"jobs": [{"id": "old1", "status": "Finished", "exitCode": 0}]}},
            status=200,
        )
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={"result": {"jobs": [{"id": "active1", "status": "Running"}]}},
            status=200,
        )
        statuses = _jobs().get_status_map()
        assert set(statuses) == {"old1", "active1"}
        assert statuses["active1"]["status"] == "Running"  # pyright: ignore[reportTypedDictNotRequiredAccess]
        assert statuses["old1"]["status"] == "Finished"  # pyright: ignore[reportTypedDictNotRequiredAccess]

    @responses.activate
    def test_active_wins_on_id_collision(self):
        """If a job id appears in both lists, the active entry wins."""
        responses.add(
            responses.POST,
            _api_url("get_historical_session"),
            json={"result": {"jobs": [{"id": "j1", "status": "Failed"}]}},
            status=200,
        )
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={"result": {"jobs": [{"id": "j1", "status": "Running"}]}},
            status=200,
        )
        statuses = _jobs().get_status_map()
        assert statuses["j1"]["status"] == "Running"  # pyright: ignore[reportTypedDictNotRequiredAccess]

    @responses.activate
    def test_skips_historical_when_disabled(self):
        """include_historical=False skips the historical round-trip entirely."""
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={"result": {"jobs": [{"id": "active1", "status": "Running"}]}},
            status=200,
        )
        statuses = _jobs().get_status_map(include_historical=False)
        assert set(statuses) == {"active1"}

    @responses.activate
    def test_degrades_to_active_only_on_unauthorized_historical(self):
        """A 401/403 from get_historical_session degrades to active-job-only status.

        Regular users' in-session cookies can launch/poll their own jobs but may lack the
        broader visibility get_historical_session requires -- this shouldn't break polling.
        """
        responses.add(
            responses.POST,
            _api_url("get_historical_session"),
            status=401,
        )
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={"result": {"jobs": [{"id": "active1", "status": "Running"}]}},
            status=200,
        )
        statuses = _jobs().get_status_map()
        assert set(statuses) == {"active1"}

    @responses.activate
    def test_reraises_other_historical_http_errors(self):
        """A non-auth HTTP error from get_historical_session still propagates."""
        responses.add(
            responses.POST,
            _api_url("get_historical_session"),
            status=502,
        )
        with pytest.raises(WorkbenchHTTPError) as exc_info:
            _jobs().get_status_map()
        assert exc_info.value.status_code == 502


class TestLaunchAndWait:
    """Tests for Jobs.launch_and_wait()."""

    @responses.activate
    def test_polls_until_finished(self):
        """launch_and_wait polls status until the job reaches a terminal state."""
        responses.add(
            responses.POST,
            _api_url("launch_job"),
            json={"result": {"job": {"id": "j1", "status": "Pending"}}},
            status=200,
        )
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={"result": {"jobs": [{"id": "j1", "status": "Finished", "exitCode": 0}]}},
            status=200,
        )

        result = _jobs().launch_and_wait(
            "Local", "test-job", "python", ["test.py"], poll_interval=0, capture_output=False
        )

        assert result.status == "Finished"
        assert result.exit_code == 0
        assert result.error_message is None
        assert result.job["id"] == "j1"  # pyright: ignore[reportTypedDictNotRequiredAccess]

    @responses.activate
    def test_reports_failure_message(self):
        """A failed job's statusMessage is surfaced as error_message."""
        responses.add(
            responses.POST,
            _api_url("launch_job"),
            json={"result": {"job": {"id": "j1", "status": "Pending"}}},
            status=200,
        )
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={
                "result": {
                    "jobs": [
                        {"id": "j1", "status": "Failed", "exitCode": 1, "statusMessage": "boom"}
                    ]
                }
            },
            status=200,
        )

        result = _jobs().launch_and_wait(
            "Local", "test-job", "python", ["test.py"], poll_interval=0, capture_output=False
        )

        assert result.status == "Failed"
        assert result.exit_code == 1
        assert result.error_message == "boom"

    @responses.activate
    def test_raises_timeout_error(self):
        """launch_and_wait raises TimeoutError if the job never reaches a terminal state."""
        responses.add(
            responses.POST,
            _api_url("launch_job"),
            json={"result": {"job": {"id": "j1", "status": "Pending"}}},
            status=200,
        )
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={"result": {"jobs": [{"id": "j1", "status": "Running"}]}},
            status=200,
        )

        with pytest.raises(TimeoutError):
            _jobs().launch_and_wait(
                "Local",
                "test-job",
                "python",
                ["test.py"],
                poll_interval=0.01,
                timeout=0.03,
                capture_output=False,
            )

    @responses.activate
    def test_captures_stdout_and_stderr(self):
        """capture_output=True (default) drains get_output and splits stdout/stderr."""
        responses.add(
            responses.POST,
            _api_url("launch_job"),
            json={"result": {"job": {"id": "j1", "status": "Pending"}}},
            status=200,
        )
        output_body = "\n".join(
            [
                json.dumps({"jobId": "j1", "outputType": "stdout", "output": "hello "}),
                json.dumps({"jobId": "j1", "outputType": "stdout", "output": "world\n"}),
                json.dumps({"jobId": "j1", "outputType": "stderr", "output": "uh oh\n"}),
            ]
        )
        responses.add(responses.POST, _api_url("get_job_output"), body=output_body, status=200)
        responses.add(
            responses.POST,
            _api_url("get_session"),
            json={"result": {"jobs": [{"id": "j1", "status": "Finished", "exitCode": 0}]}},
            status=200,
        )

        result = _jobs().launch_and_wait("Local", "test-job", "python", ["test.py"], poll_interval=0)

        assert result.stdout == "hello world\n"
        assert result.stderr == "uh oh\n"
        assert result.status == "Finished"
