"""Public Workbench resource contracts over both authentication clients."""

from __future__ import annotations

import json

import pytest
import responses
from responses import matchers
from typing_extensions import TYPE_CHECKING, Iterator

from posit.workbench import Client as SessionClient
from posit.workbench.admin import Client as AdminClient

if TYPE_CHECKING:
    from posit.workbench.jobs import AuditedJob, Job, Jobs
    from posit.workbench.sessions import Session, Sessions

SERVER_URL = "https://workbench.example.com"
RPC_COOKIE = "test-cookie-value|Mon%2C%2001%20Jan%202030%2000%3A00%3A00%20GMT"

CASES = [
    (
        "users",
        "get_users",
        None,
        {},
        {"username": "alice", "status": "Active"},
        "username",
        "isAdmin",
        True,
    ),
    (
        "sessions",
        "get_session",
        "sessions",
        {},
        {"id": "s1", "username": "alice", "workbench": "RStudio"},
        "id",
        "activity_state",
        "running",
    ),
    (
        "jobs",
        "get_session",
        "jobs",
        {"include_all_jobs": True},
        {"id": "j1", "user": "alice", "status": "Running"},
        "id",
        "cluster",
        "Local",
    ),
    (
        "compute_envs",
        "get_compute_envs",
        "clusters",
        {},
        {"name": "Local", "type": "Local"},
        "name",
        "supportsContainers",
        True,
    ),
]


@pytest.fixture(params=["session", "bearer"])
def client(request, monkeypatch) -> Iterator[SessionClient | AdminClient]:
    if request.param == "session":
        monkeypatch.setenv("POSIT_PRODUCT", "WORKBENCH")
        monkeypatch.setenv("RS_SERVER_ADDRESS", SERVER_URL)
        monkeypatch.setenv("RS_SESSION_RPC_COOKIE", RPC_COOKIE)
        instance = SessionClient()
    else:
        instance = AdminClient(url=SERVER_URL, api_key="test-token")
    try:
        yield instance
    finally:
        instance.session.close()


@pytest.fixture(params=CASES, ids=[case[0] for case in CASES])
def collection(request, client):
    name, method, key, params, record, identity, missing_field, missing_value = request.param
    records = [{**record, identity: "other"}, record]
    result = records if key is None else {key: records}
    responses.post(
        f"{SERVER_URL}/api/{method}",
        json={"result": result},
        match=[matchers.json_params_matcher({"method": method, "kwparams": params})],
    )
    return getattr(client, name), records, identity, missing_field, missing_value


@responses.activate
def test_fetch_records_and_authentication(client, collection):
    manager, records, _, _, _ = collection
    fetched = list(manager.fetch())
    assert fetched == records
    assert all(record._ctx is client._ctx for record in fetched)
    headers = responses.calls[0].request.headers
    if isinstance(client, AdminClient):
        assert headers["Authorization"] == "Bearer test-token"
    else:
        assert headers["X-RS-Session-Server-RPC-Cookie"] == RPC_COOKIE


@pytest.mark.parametrize("operation", ["iterate", "length", "index", "slice", "str", "repr"])
@responses.activate
def test_sequence_access(collection, operation):
    manager, records, _, _, _ = collection
    if operation == "iterate":
        assert list(iter(manager)) == records
    elif operation == "length":
        assert len(manager) == len(records)
    elif operation == "index":
        assert manager[-1] == records[-1]
    elif operation == "slice":
        assert manager[1:] == records[1:]
    elif operation == "str":
        assert str(manager) == str(records)
    else:
        assert repr(manager) == repr(records)
    assert len(responses.calls) == 1


@responses.activate
def test_find_by_matches_locally_without_forwarding_fields(collection):
    manager, records, identity, _, _ = collection
    assert manager.find_by(**{identity: records[-1][identity]}) == records[-1]
    assert manager.find_by(**{identity: "missing"}) is None
    assert manager.find_by() == records[0]


@responses.activate
def test_find_by_skips_absent_fields(collection):
    manager, _, _, missing_field, missing_value = collection
    assert manager.find_by(**{missing_field: missing_value}) is None


@pytest.mark.parametrize("case", CASES, ids=[case[0] for case in CASES])
@responses.activate
def test_empty_collection(client, case):
    name, method, key, params, record, identity, _, _ = case
    result = [] if key is None else {key: []}
    responses.post(
        f"{SERVER_URL}/api/{method}",
        json={"result": result},
        match=[matchers.json_params_matcher({"method": method, "kwparams": params})],
    )
    manager = getattr(client, name)
    assert list(manager.fetch()) == []
    assert len(manager) == 0
    assert manager[:] == []
    assert manager.find_by(**{identity: record[identity]}) is None
    with pytest.raises(IndexError):
        manager[0]


@responses.activate
def test_find_by_requires_all_conditions(client):
    responses.post(
        f"{SERVER_URL}/api/get_users",
        json={
            "result": [
                {"username": "alice", "status": "Locked"},
                {"username": "bob", "status": "Active"},
            ]
        },
        match=[matchers.json_params_matcher({"method": "get_users", "kwparams": {}})],
    )
    assert client.users.find_by(username="alice", status="Active") is None
    assert client.users.find_by(username="bob", status="Active") == {
        "username": "bob",
        "status": "Active",
    }


@responses.activate
def test_collection_access_fetches_fresh_records(client):
    responses.post(f"{SERVER_URL}/api/get_users", json={"result": [{"username": "alice"}]})
    responses.post(f"{SERVER_URL}/api/get_users", json={"result": [{"username": "bob"}]})
    users = client.users
    assert users[0]["username"] == "alice"
    assert users[0]["username"] == "bob"
    assert len(responses.calls) == 2


@responses.activate
def test_sessions_fetch_translates_filters_and_wraps_projected_records(client):
    identifiers = ["s1", "s2"]
    responses.post(
        f"{SERVER_URL}/api/get_session",
        json={"result": {"sessions": [{"workbench": "RStudio"}], "projects": []}},
        match=[
            matchers.json_params_matcher(
                {
                    "method": "get_session",
                    "kwparams": {
                        "session_id": "s1,s2",
                        "user": "alice",
                        "fields": ["workbench"],
                        "timestamp": 123.0,
                    },
                }
            )
        ],
    )
    sessions: Sessions = client.sessions
    records = list(
        sessions.fetch(session_id=identifiers, user="alice", fields=["workbench"], timestamp=123.0)
    )
    assert records == [{"workbench": "RStudio"}]
    assert identifiers == ["s1", "s2"]


@pytest.mark.parametrize(
    ("name", "method", "key", "params"),
    [
        ("jobs", "get_session", "jobs", {"user": "alice", "include_all_jobs": True}),
        ("compute_envs", "get_compute_envs", "clusters", {"user": "alice"}),
    ],
)
@responses.activate
def test_fetch_passes_server_user_filter(client, name, method, key, params):
    responses.post(
        f"{SERVER_URL}/api/{method}",
        json={"result": {key: []}},
        match=[matchers.json_params_matcher({"method": method, "kwparams": params})],
    )
    assert list(getattr(client, name).fetch(user="alice")) == []


@responses.activate
def test_composite_responses_retain_metadata(client):
    session_result = {"sessions": [], "projects": [{"id": "p1"}], "jobs": [], "timestamp": 123.0}
    responses.post(f"{SERVER_URL}/api/get_session", json={"result": session_result})
    assert client.sessions.get(include_jobs=True, include_projects=True) == session_result
    compute_result = {
        "clusters": [{"name": "Local"}],
        "workbenches": {"RStudio": {"default_cluster": "Local"}},
    }
    responses.post(f"{SERVER_URL}/api/get_compute_envs", json={"result": compute_result})
    assert client.compute_envs.list(user="alice") == compute_result


@responses.activate
def test_session_item_operations(client):
    responses.post(
        f"{SERVER_URL}/api/get_session",
        json={"result": {"sessions": [{"id": "s1", "url": "/s/s1/"}]}},
    )
    session: Session = next(iter(client.sessions.fetch()))
    assert session.connection_url == f"{SERVER_URL}/s/s1"
    responses.post(
        f"{SERVER_URL}/api/stop_session",
        json={"result": None},
        match=[
            matchers.json_params_matcher(
                {"method": "stop_session", "kwparams": {"session_ids": "s1", "suspend": True}}
            )
        ],
    )
    session.stop(suspend=True)
    launch_result = {"id": "s1", "url": "/s/s1/", "project_id": "p1"}
    responses.post(
        f"{SERVER_URL}/api/resume_session",
        json={"result": launch_result},
        match=[
            matchers.json_params_matcher(
                {"method": "resume_session", "kwparams": {"session_id": "s1", "username": "alice"}}
            )
        ],
    )
    assert session.resume(username="alice") == launch_result


@responses.activate
def test_job_item_operations(client):
    responses.post(f"{SERVER_URL}/api/launch_job", json={"result": {"job": {"id": "j1"}}})
    jobs: Jobs = client.jobs
    job: Job = jobs.launch("Local", "job", "python")
    responses.post(
        f"{SERVER_URL}/api/stop_job",
        json={"result": None},
        match=[
            matchers.json_params_matcher(
                {"method": "stop_job", "kwparams": {"job_id": "j1", "force_quit": True}}
            )
        ],
    )
    job.stop(force_quit=True)
    chunk = {"jobId": "j1", "outputType": "stdout", "output": "hello"}
    responses.post(
        f"{SERVER_URL}/api/get_job_output",
        body=json.dumps(chunk),
        match=[
            matchers.json_params_matcher(
                {"method": "get_job_output", "kwparams": {"job_id": "j1", "user": "alice"}}
            )
        ],
    )
    assert list(job.get_output(user="alice")) == [chunk]


@responses.activate
def test_audited_job_item_operations(client):
    responses.post(
        f"{SERVER_URL}/api/launch_audited_job",
        json={"result": {"audited_job": {"id": "a1"}}},
    )
    job: AuditedJob = client.jobs.launch_audited("Local", "job", "python")
    responses.post(
        f"{SERVER_URL}/api/stop_audited_job",
        json={"result": None},
        match=[
            matchers.json_params_matcher(
                {"method": "stop_audited_job", "kwparams": {"audited_job_id": "a1"}}
            )
        ],
    )
    job.stop()
    chunk = {"jobId": "a1", "output": "hello", "outputSource": "audit_details_store"}
    responses.post(
        f"{SERVER_URL}/api/get_audited_job_output",
        json={"result": {"audited_job_output": chunk}},
    )
    assert list(job.get_output()) == [chunk]
    details = {"script_output": {"checksum": "abc"}, "environment": {}}
    responses.post(
        f"{SERVER_URL}/api/get_audited_job_details",
        json={"result": {"audited_details": details}},
    )
    assert job.get_details() == details


@responses.activate
def test_server_service_keeps_bare_version_response(client):
    info = {"version": {"major": "2026", "minor": "7"}, "features": ["jobs"]}
    responses.post(
        f"{SERVER_URL}/api/version",
        json=info,
        match=[matchers.json_params_matcher({"method": "version", "kwparams": {}})],
    )
    assert client.server.version() == info
