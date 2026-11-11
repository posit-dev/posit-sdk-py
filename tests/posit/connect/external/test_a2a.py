from __future__ import annotations

import asyncio
import base64
import json
import logging
import subprocess
import sys
import time
import uuid
from pathlib import Path

import httpx
import pytest
from a2a.types import AgentSkill
from a2a.utils.errors import UnsupportedOperationError
from fastapi.testclient import TestClient
from typing_extensions import TYPE_CHECKING, Any, cast

from posit.connect.external import a2a
from posit.connect.external._a2a_request import visitor_guid_from_token

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

ROOT = Path(__file__).resolve().parents[4]
CARD_PATH = "/.well-known/agent-card.json"
JSONRPC_PATH = "/a2a/jsonrpc"
TOKEN_HEADER = "Posit-Connect-User-Session-Token"
BASE_URL_HEADER = "RStudio-Connect-App-Base-URL"
FAILURE_TEXT = "The agent could not answer this request. Try again later."
ALLOWED_HEADERS = {
    "posit-connect-user-session-token",
    "rstudio-connect-credentials",
    "rstudio-connect-app-base-url",
    "a2a-version",
    "user-agent",
    "accept-language",
}
SKILL = AgentSkill(id="lookup", name="Lookup", description="Looks things up.", tags=["data"])
LOGGER_NAME = "posit.connect.external.a2a"


@pytest.fixture(autouse=True)
def _no_connect_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("CONNECT_SERVER", raising=False)
    monkeypatch.delenv("CONNECT_CONTENT_GUID", raising=False)


def _jwt_with_payload(payload: bytes) -> str:
    def encode(data: bytes) -> str:
        return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

    return f"{encode(b'{}')}.{encode(payload)}.signature"


def _token(sub: str, exp: int = 1) -> str:
    return _jwt_with_payload(json.dumps({"sub": sub, "exp": exp}).encode())


class RecordingAgent:
    """An agent that answers with fixed chunks and records each question.

    ``fail_at`` selects where the agent raises. ``"start"`` raises before it returns the stream,
    and ``"stream"`` raises after the first chunk.
    """

    def __init__(self, chunks: tuple[Any, ...], fail_at: str | None) -> None:
        self.chunks = chunks
        self.fail_at = fail_at
        self.questions: list[str] = []

    async def stream_async(self, text: str, *, content: str) -> AsyncIterator[Any]:
        self.questions.append(text)
        if self.fail_at == "start":
            raise RuntimeError("boom: start")
        return self._stream()

    async def _stream(self) -> AsyncIterator[Any]:
        for chunk in self.chunks:
            yield chunk
        if self.fail_at == "stream":
            raise RuntimeError("boom: stream")


class Factory:
    """Builds a `RecordingAgent` for each conversation and records the request that opened it.

    ``fail_at="factory"`` makes the factory itself raise.
    """

    def __init__(self, chunks: tuple[Any, ...] = ("Answer.",), fail_at: str | None = None) -> None:
        self.chunks = chunks
        self.fail_at = fail_at
        self.requests: list[Any] = []
        self.agents: list[RecordingAgent] = []

    def __call__(self, request: Any) -> RecordingAgent:
        self.requests.append(request)
        if self.fail_at == "factory":
            raise RuntimeError("boom: factory")
        agent_fail_at = self.fail_at if self.fail_at in ("start", "stream") else None
        agent = RecordingAgent(self.chunks, agent_fail_at)
        self.agents.append(agent)
        return agent


class SlowAgent:
    """An agent whose stream waits before it yields. It records start and end in ``events``."""

    def __init__(self, delay: float = 0.05, events: list[tuple[str, str]] | None = None) -> None:
        self.delay = delay
        self.events: list[tuple[str, str]] = [] if events is None else events

    async def stream_async(self, text: str, *, content: str) -> AsyncIterator[str]:
        async def stream() -> AsyncIterator[str]:
            self.events.append(("start", text))
            await asyncio.sleep(self.delay)
            self.events.append(("end", text))
            yield "done"

        return stream()


def _app(factory: Any, **kwargs: Any) -> Any:
    return a2a.create_a2a_app(
        factory,
        name="Test agent",
        description="Test agent.",
        skills=[SKILL],
        **kwargs,
    )


def _message(parts: list[str], context_id: str | None = None) -> dict[str, Any]:
    message: dict[str, Any] = {
        "messageId": "m1",
        "role": "ROLE_USER",
        "parts": [{"text": part} for part in parts],
    }
    if context_id is not None:
        message["contextId"] = context_id
    return message


def _body(text: str, context_id: str | None = None) -> dict[str, Any]:
    return {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "SendMessage",
        "params": {"message": _message([text], context_id)},
    }


def _headers(extra: dict[str, str] | None) -> dict[str, str]:
    return {"A2A-Version": "1.0", **(extra or {})}


def _send(
    client: Any,
    text: str,
    context_id: str | None = None,
    headers: dict[str, str] | None = None,
) -> Any:
    return client.post(JSONRPC_PATH, json=_body(text, context_id), headers=_headers(headers))


def _rpc(client: Any, method: str, params: dict[str, Any], token: str) -> dict[str, Any]:
    body = {"jsonrpc": "2.0", "id": "1", "method": method, "params": params}
    return client.post(JSONRPC_PATH, json=body, headers=_headers({TOKEN_HEADER: token})).json()


async def _async_send(
    client: Any,
    text: str,
    context_id: str,
    headers: dict[str, str] | None = None,
) -> Any:
    response = await client.post(
        JSONRPC_PATH, json=_body(text, context_id), headers=_headers(headers)
    )
    return response.json()


def _reply_context(response: Any) -> str:
    return response.json()["result"]["message"]["contextId"]


def _async_client(app: Any) -> httpx.AsyncClient:
    transport = httpx.ASGITransport(app=app)
    return httpx.AsyncClient(transport=transport, base_url="http://testserver")


def test_agent_card_describes_the_agent_and_its_api_key_scheme():
    with TestClient(_app(Factory())) as client:
        response = client.get(CARD_PATH)

    assert response.status_code == 200
    assert response.json() == {
        "name": "Test agent",
        "description": "Test agent.",
        "version": "0.1.0",
        "supportedInterfaces": [
            {
                "url": "http://testserver/a2a/jsonrpc",
                "protocolBinding": "JSONRPC",
                "protocolVersion": "1.0",
            }
        ],
        "provider": {"organization": "Posit Connect", "url": "http://testserver"},
        "capabilities": {"streaming": False},
        "securitySchemes": {
            "connectApiKey": {
                "apiKeySecurityScheme": {
                    "description": "Posit Connect API key, sent as `Key <api-key>`.",
                    "location": "header",
                    "name": "Authorization",
                }
            }
        },
        "securityRequirements": [{"schemes": {"connectApiKey": {}}}],
        "defaultInputModes": ["text/plain"],
        "defaultOutputModes": ["text/plain"],
        "skills": [
            {
                "id": "lookup",
                "name": "Lookup",
                "description": "Looks things up.",
                "tags": ["data"],
            }
        ],
    }


def test_one_app_serves_each_card_with_its_own_base_url():
    async def fetch_both() -> tuple[Any, Any]:
        async with _async_client(_app(Factory())) as client:
            return await asyncio.gather(
                client.get(
                    CARD_PATH, headers=[(BASE_URL_HEADER, "https://one.example/content/a")]
                ),
                client.get(
                    CARD_PATH, headers=[(BASE_URL_HEADER, "https://two.example/content/b")]
                ),
            )

    first, second = asyncio.run(fetch_both())

    assert first.json()["supportedInterfaces"][0]["url"] == (
        "https://one.example/content/a/a2a/jsonrpc"
    )
    assert second.json()["supportedInterfaces"][0]["url"] == (
        "https://two.example/content/b/a2a/jsonrpc"
    )


@pytest.mark.parametrize(
    ("headers", "env", "interface_base", "provider_url"),
    [
        pytest.param(
            [(BASE_URL_HEADER, "https://connect.example/content/abc/")],
            {"CONNECT_SERVER": "https://other.example/", "CONNECT_CONTENT_GUID": "guid-1"},
            "https://connect.example/content/abc",
            "https://other.example",
            id="forwarded-header-wins",
        ),
        pytest.param(
            [
                (BASE_URL_HEADER, "https://evil.example/content/x"),
                (BASE_URL_HEADER, "https://connect.example/content/real/"),
            ],
            {},
            "https://connect.example/content/real",
            "https://connect.example/content/real",
            id="last-forwarded-value-wins",
        ),
        pytest.param(
            [
                (BASE_URL_HEADER, "https://connect.example/content/real"),
                (BASE_URL_HEADER, "/"),
            ],
            {},
            "http://testserver",
            "http://testserver",
            id="invalid-last-value-falls-back-to-request",
        ),
        pytest.param(
            [(BASE_URL_HEADER, "javascript:alert(1)")],
            {},
            "http://testserver",
            "http://testserver",
            id="non-http-value-falls-back-to-request",
        ),
        pytest.param(
            [(BASE_URL_HEADER, "")],
            {"CONNECT_SERVER": "https://connect.example/", "CONNECT_CONTENT_GUID": "guid-1"},
            "https://connect.example/content/guid-1",
            "https://connect.example",
            id="empty-header-is-ignored",
        ),
        pytest.param(
            [],
            {"CONNECT_SERVER": "https://connect.example/", "CONNECT_CONTENT_GUID": "guid-1"},
            "https://connect.example/content/guid-1",
            "https://connect.example",
            id="server-and-guid-env",
        ),
        pytest.param(
            [],
            {"CONNECT_SERVER": "https://connect.example"},
            "http://testserver",
            "https://connect.example",
            id="server-without-guid-uses-request",
        ),
        pytest.param(
            [],
            {"CONNECT_CONTENT_GUID": "guid-1"},
            "http://testserver",
            "http://testserver",
            id="guid-without-server-uses-request",
        ),
        pytest.param([], {}, "http://testserver", "http://testserver", id="request-base-url"),
    ],
)
def test_agent_card_public_urls_follow_the_precedence(
    monkeypatch: pytest.MonkeyPatch,
    headers: list[tuple[str, str]],
    env: dict[str, str],
    interface_base: str,
    provider_url: str,
):
    for name, value in env.items():
        monkeypatch.setenv(name, value)

    with TestClient(_app(Factory())) as client:
        card = client.get(CARD_PATH, headers=headers).json()

    assert card["supportedInterfaces"][0]["url"] == f"{interface_base}/a2a/jsonrpc"
    assert card["provider"]["url"] == provider_url


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param("plain text", ("plain text", None), id="no-markup"),
        pytest.param(
            'Answer.<shiny-aside label="Trusted" icon="i.svg">'
            "<commons-provenance-info></commons-provenance-info></shiny-aside>",
            ("Answer.", "Trusted"),
            id="provenance-aside-removed",
        ),
        pytest.param(
            "Answer <b>bold</b> stays.",
            ("Answer <b>bold</b> stays.", None),
            id="unknown-tags-kept",
        ),
        pytest.param(
            "Answer <span>highlighted</span>.",
            ("Answer highlighted.", None),
            id="commons-tag-outside-aside-removed",
        ),
        pytest.param("x<br/>y", ("x<br/>y", None), id="self-closing-tag-kept"),
        pytest.param("a<b and c>d", ("a<b and c>d", None), id="no-space-comparison-kept"),
        pytest.param("a < b and c > d", ("a < b and c > d", None), id="spaced-comparison-kept"),
        pytest.param(
            "List<int> and Map<String, int>",
            ("List<int> and Map<String, int>", None),
            id="generics-kept",
        ),
        pytest.param(
            "Example:\n```\nVec<T>::new()\n```",
            ("Example:\n```\nVec<T>::new()\n```", None),
            id="code-fence-kept",
        ),
        pytest.param(
            "Line one\n\n\n\nLine two\n \n \nLine three  \n",
            ("Line one\n\nLine two\n\nLine three", None),
            id="blank-lines-collapsed",
        ),
        pytest.param(
            '<shiny-aside label="Trusted"></shiny-aside>\n  Answer',
            ("Answer", "Trusted"),
            id="leading-whitespace-stripped",
        ),
        pytest.param(
            'Fact.<shiny-aside label="Sales data"><p>quote</p></shiny-aside> More.'
            '<shiny-aside label="Cited"><span></span></shiny-aside>',
            ("Fact. More.", "Cited"),
            id="citation-aside-then-provenance",
        ),
        pytest.param(
            'Fact.<shiny-aside label="Sales data">quote</shiny-aside>',
            ("Fact.", None),
            id="citation-aside-only",
        ),
        pytest.param(
            'Answer.<shiny-aside label="Cited">\nline one\nline two\n</shiny-aside>',
            ("Answer.", "Cited"),
            id="aside-body-spans-lines",
        ),
        pytest.param(
            'Answer.<shiny-aside label="Trusted">partial body',
            ("Answer.", "Trusted"),
            id="unclosed-aside-runs-to-end",
        ),
        pytest.param(
            'Answer.<shiny-aside label="Trusted">first<shiny-aside label="Cited">second</shiny-aside>',
            ("Answer.", "Cited"),
            id="unclosed-aside-ends-at-next-aside",
        ),
        pytest.param(
            "stray </shiny-aside> closer",
            ("stray  closer", None),
            id="stray-closer-removed",
        ),
        pytest.param(
            "<shiny-aside label='Cited'>x</shiny-aside>",
            ("", "Cited"),
            id="single-quoted-label",
        ),
        pytest.param(
            'Use label="Trusted" in text.',
            ('Use label="Trusted" in text.', None),
            id="label-text-outside-aside-is-not-provenance",
        ),
        pytest.param(
            '<shiny-aside data-label="Trusted">x</shiny-aside>',
            ("", None),
            id="data-label-is-not-provenance",
        ),
        pytest.param(
            '<shiny-aside label="Trusted">a</shiny-aside>'
            '<shiny-aside label="Untrusted">b</shiny-aside>',
            ("", "Untrusted"),
            id="least-trusted-label-wins",
        ),
        pytest.param(
            '<shiny-aside label="Untrusted">a</shiny-aside>'
            '<shiny-aside label="Trusted">b</shiny-aside>',
            ("", "Untrusted"),
            id="trusted-label-cannot-mask-untrusted",
        ),
        pytest.param(
            '<shiny-aside label="Cited">a</shiny-aside>'
            '<shiny-aside label="Trusted">b</shiny-aside>',
            ("", "Cited"),
            id="cited-outranks-trusted",
        ),
    ],
)
def test_clean_answer_strips_markup_and_reads_provenance(raw: str, expected: tuple[str, Any]):
    assert a2a._clean_answer(raw) == expected


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        pytest.param('<shiny-aside label="Trusted">' * 8000, ("", "Trusted"), id="closed-openers"),
        pytest.param(
            '<shiny-aside label="Trusted"' * 8000, ("", "Trusted"), id="unterminated-tags"
        ),
    ],
)
def test_adversarial_unclosed_asides_are_cleaned_quickly(raw: str, expected: tuple[str, Any]):
    started = time.perf_counter()
    result = a2a._clean_answer(raw)
    elapsed = time.perf_counter() - started

    assert elapsed < 1.0
    assert result == expected


def test_message_returns_one_agent_message_with_provenance():
    chunks = (
        "Hello <b>there</b>.\n\n\n\n",
        (
            '<shiny-aside label="Trusted" icon="x.svg">'
            "<commons-provenance-info></commons-provenance-info></shiny-aside>"
        ),
    )
    with TestClient(_app(Factory(chunks=chunks))) as client:
        body = _send(client, "hi", "ctx-1").json()

    assert set(body) == {"jsonrpc", "id", "result"}
    assert body["jsonrpc"] == "2.0"
    assert body["id"] == "1"
    assert set(body["result"]) == {"message"}
    message = body["result"]["message"]
    assert uuid.UUID(message.pop("messageId")).version == 4
    assert message == {
        "contextId": "ctx-1",
        "role": "ROLE_AGENT",
        "parts": [{"text": "Hello <b>there</b>."}],
        "metadata": {"commons": {"provenance": "Trusted"}},
    }


def test_message_without_provenance_reports_null():
    with TestClient(_app(Factory(chunks=("Plain answer.",)))) as client:
        message = _send(client, "hi", "ctx-1").json()["result"]["message"]

    assert message["metadata"] == {"commons": {"provenance": None}}
    assert message["parts"] == [{"text": "Plain answer."}]


def test_stream_chunks_are_joined_without_separators():
    with TestClient(_app(Factory(chunks=("Hel", "lo")))) as client:
        message = _send(client, "hi", "ctx-1").json()["result"]["message"]

    assert message["parts"] == [{"text": "Hello"}]


def test_non_text_chunks_are_skipped():
    with TestClient(_app(Factory(chunks=("Hi", {"kind": "tool"}, " there")))) as client:
        message = _send(client, "hi", "ctx-1").json()["result"]["message"]

    assert message["parts"] == [{"text": "Hi there"}]


def test_multi_part_message_is_joined_with_newlines():
    factory = Factory()
    body = _body("unused", "ctx-1")
    body["params"]["message"] = _message(["first", "second"], "ctx-1")
    with TestClient(_app(factory)) as client:
        client.post(JSONRPC_PATH, json=body, headers=_headers(None))

    assert factory.agents[0].questions == ["first\nsecond"]


def test_context_id_is_reused_and_each_context_gets_its_own_agent():
    factory = Factory()
    with TestClient(_app(factory)) as client:
        first = _send(client, "one", "ctx-a")
        second = _send(client, "two", "ctx-a")
        other = _send(client, "three", "ctx-b")

    assert _reply_context(first) == "ctx-a"
    assert _reply_context(second) == "ctx-a"
    assert _reply_context(other) == "ctx-b"
    assert [request.context_id for request in factory.requests] == ["ctx-a", "ctx-b"]
    assert factory.agents[0].questions == ["one", "two"]
    assert factory.agents[1].questions == ["three"]


def test_missing_context_id_starts_a_new_context_with_a_uuid4():
    factory = Factory()
    with TestClient(_app(factory)) as client:
        first = _send(client, "one")
        second = _send(client, "two")

    first_context = _reply_context(first)
    second_context = _reply_context(second)
    assert uuid.UUID(first_context).version == 4
    assert first_context != second_context
    assert [request.context_id for request in factory.requests] == [first_context, second_context]


def test_same_context_id_from_two_visitors_gets_separate_agents():
    factory = Factory()
    with TestClient(_app(factory)) as client:
        _send(client, "alice question", "shared", {TOKEN_HEADER: _token("alice")})
        _send(client, "bob question", "shared", {TOKEN_HEADER: _token("bob")})
        _send(client, "alice again", "shared", {TOKEN_HEADER: _token("alice", exp=2)})

    assert [request.visitor_guid for request in factory.requests] == ["alice", "bob"]
    assert factory.agents[0].questions == ["alice question", "alice again"]
    assert factory.agents[1].questions == ["bob question"]


def test_anonymous_request_does_not_share_an_agent_with_a_visitor():
    factory = Factory()
    with TestClient(_app(factory)) as client:
        _send(client, "anonymous", "shared")
        _send(client, "visitor", "shared", {TOKEN_HEADER: _token("alice")})

    assert [request.visitor_guid for request in factory.requests] == [None, "alice"]
    assert factory.agents[0].questions == ["anonymous"]
    assert factory.agents[1].questions == ["visitor"]


@pytest.mark.parametrize(
    "token",
    [
        pytest.param("not-a-jwt", id="no-separators"),
        pytest.param("a.b.c", id="payload-not-base64"),
        pytest.param(_jwt_with_payload(b"[1]"), id="payload-not-object"),
        pytest.param(_jwt_with_payload(b'{"sub": 5}'), id="subject-not-string"),
        pytest.param(_jwt_with_payload(b"\xff\xfe"), id="payload-not-utf8"),
    ],
)
def test_malformed_session_token_has_no_visitor_and_does_not_fail(token: str):
    factory = Factory()
    with TestClient(_app(factory)) as client:
        response = _send(client, "hi", "ctx-1", {TOKEN_HEADER: token})

    assert "result" in response.json()
    (request,) = factory.requests
    assert request.visitor_guid is None
    assert request.user_session_token == token


@pytest.mark.parametrize(
    ("token", "expected"),
    [
        pytest.param(_token("alice"), "alice", id="subject"),
        pytest.param(None, None, id="absent"),
        pytest.param("", None, id="empty"),
        pytest.param("not-a-jwt", None, id="no-separators"),
        pytest.param("a.b.c", None, id="payload-not-base64"),
        pytest.param(_jwt_with_payload(b"not json"), None, id="payload-not-json"),
        pytest.param(_jwt_with_payload(b"[1]"), None, id="payload-not-object"),
        pytest.param(_jwt_with_payload(b'{"sub": ""}'), None, id="empty-subject"),
        pytest.param(_jwt_with_payload(b'{"name": "x"}'), None, id="no-subject"),
    ],
)
def test_visitor_guid_is_the_subject_claim_of_a_well_formed_token(
    token: str | None, expected: str | None
):
    assert visitor_guid_from_token(token) == expected


def test_least_recently_used_context_is_evicted_at_the_limit():
    factory = Factory()
    with TestClient(_app(factory, max_contexts=2)) as client:
        for context_id in ["a", "b", "a", "c", "a", "b"]:
            _send(client, "question", context_id)

    assert [request.context_id for request in factory.requests] == ["a", "b", "c", "b"]


def test_limit_of_one_keeps_only_the_latest_context():
    factory = Factory()
    with TestClient(_app(factory, max_contexts=1)) as client:
        for context_id in ["a", "b", "a"]:
            _send(client, "question", context_id)

    assert [request.context_id for request in factory.requests] == ["a", "b", "a"]


def test_default_limit_is_one_hundred_contexts():
    factory = Factory()
    with TestClient(_app(factory)) as client:
        for index in range(101):
            _send(client, "question", f"c{index}")
        _send(client, "question", "c0")

    assert len(factory.requests) == 102
    assert factory.requests[-1].context_id == "c0"


def test_busy_context_is_not_evicted_at_the_limit():
    requests: list[Any] = []

    def factory(request: Any) -> SlowAgent:
        requests.append(request)
        return SlowAgent(delay=0.5)

    async def run() -> None:
        async with _async_client(_app(factory, max_contexts=1)) as client:
            busy = asyncio.create_task(_async_send(client, "busy", "a"))
            await asyncio.sleep(0.1)
            await _async_send(client, "other", "b")
            await busy
            await _async_send(client, "again", "a")

    asyncio.run(run())

    assert [request.context_id for request in requests] == ["a", "b"]


def test_max_contexts_below_one_is_rejected():
    with pytest.raises(ValueError, match="max_contexts must be at least 1."):
        _app(Factory(), max_contexts=0)


def test_messages_in_one_context_run_one_at_a_time():
    events: list[tuple[str, str]] = []
    agent = SlowAgent(events=events)

    async def send_both() -> None:
        async with _async_client(_app(lambda request: agent)) as client:
            await asyncio.gather(
                _async_send(client, "one", "ctx"),
                _async_send(client, "two", "ctx"),
            )

    asyncio.run(send_both())

    assert [kind for kind, _ in events] == ["start", "end", "start", "end"]
    assert events[1][1] == events[0][1]
    assert events[3][1] == events[2][1]


def test_different_contexts_do_not_wait_for_each_other():
    events: list[tuple[str, str]] = []

    async def send_both() -> None:
        async with _async_client(_app(lambda request: SlowAgent(events=events))) as client:
            await asyncio.gather(
                _async_send(client, "one", "ctx-1"),
                _async_send(client, "two", "ctx-2"),
            )

    asyncio.run(send_both())

    assert [kind for kind, _ in events[:2]] == ["start", "start"]


class TokenRecordingAgent:
    """Records the session token that ``current_a2a_request`` reports inside its stream."""

    def __init__(self, seen: list[str | None]) -> None:
        self.seen = seen

    async def stream_async(self, text: str, *, content: str) -> AsyncIterator[str]:
        async def stream() -> AsyncIterator[str]:
            request = a2a.current_a2a_request()
            assert request is not None
            self.seen.append(request.user_session_token)
            yield "ok"

        return stream()


def test_tool_inside_a_turn_sees_the_current_message_token():
    seen: list[str | None] = []
    first_token = _token("alice", exp=1)
    second_token = _token("alice", exp=2)
    agent = TokenRecordingAgent(seen)
    with TestClient(_app(lambda request: agent)) as client:
        _send(client, "one", "ctx", {TOKEN_HEADER: first_token})
        _send(client, "two", "ctx", {TOKEN_HEADER: second_token})

    assert seen == [first_token, second_token]
    assert a2a.current_a2a_request() is None


def test_factory_request_carries_session_token_and_only_allowlisted_headers():
    factory = Factory()
    token = _token("alice")
    with TestClient(_app(factory)) as client:
        _send(
            client,
            "hi",
            headers={
                TOKEN_HEADER: token,
                "RStudio-Connect-Credentials": "creds",
                "X-Custom": "Value",
            },
        )

    (request,) = factory.requests
    assert request.user_session_token == token
    assert request.visitor_guid == "alice"
    assert request.headers["posit-connect-user-session-token"] == token
    assert request.headers["rstudio-connect-credentials"] == "creds"
    assert "x-custom" not in request.headers
    assert set(request.headers) <= ALLOWED_HEADERS
    assert uuid.UUID(request.context_id).version == 4


def test_factory_request_has_no_session_token_without_the_header():
    factory = Factory()
    with TestClient(_app(factory)) as client:
        _send(client, "hi")

    (request,) = factory.requests
    assert request.user_session_token is None
    assert request.visitor_guid is None


@pytest.mark.parametrize("fail_at", ["factory", "start", "stream"])
def test_agent_failure_returns_failed_task_without_details(
    fail_at: str,
    caplog: pytest.LogCaptureFixture,
):
    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        with TestClient(_app(Factory(fail_at=fail_at))) as client:
            response = _send(client, "hi", "ctx-fail")

    body = response.json()
    assert set(body["result"]) == {"task"}
    task = body["result"]["task"]
    assert task["contextId"] == "ctx-fail"
    assert uuid.UUID(task["id"]).version == 4
    assert task["status"]["state"] == "TASK_STATE_FAILED"
    assert task["status"]["message"]["parts"] == [{"text": FAILURE_TEXT}]
    assert "error" not in body
    assert "boom" not in response.text
    assert "Traceback" not in response.text
    (record,) = [record for record in caplog.records if record.name == LOGGER_NAME]
    assert record.exc_info is not None
    assert "'ctx-fail'" in record.getMessage()


def test_failed_turn_starts_a_new_agent_on_the_next_message():
    failures_left = [1]

    class FailsOnce:
        async def stream_async(self, text: str, *, content: str) -> AsyncIterator[str]:
            if failures_left[0]:
                failures_left[0] = 0
                raise RuntimeError("boom: first turn")

            async def stream() -> AsyncIterator[str]:
                yield "recovered"

            return stream()

    factory_calls: list[str] = []

    def factory(request: Any) -> Any:
        factory_calls.append(request.context_id)
        return FailsOnce()

    with TestClient(_app(factory)) as client:
        failed = _send(client, "one", "ctx")
        recovered = _send(client, "two", "ctx")

    assert "task" in failed.json()["result"]
    assert recovered.json()["result"]["message"]["parts"] == [{"text": "recovered"}]
    assert factory_calls == ["ctx", "ctx"]


def test_failed_task_is_visible_only_to_its_visitor():
    factory = Factory(fail_at="start")
    with TestClient(_app(factory)) as client:
        failed = _send(client, "hi", "ctx", {TOKEN_HEADER: _token("alice")}).json()
        task_id = failed["result"]["task"]["id"]
        alice_get = _rpc(client, "GetTask", {"id": task_id}, _token("alice"))
        bob_get = _rpc(client, "GetTask", {"id": task_id}, _token("bob"))
        alice_list = _rpc(client, "ListTasks", {}, _token("alice"))
        bob_list = _rpc(client, "ListTasks", {}, _token("bob"))

    assert alice_get["result"]["id"] == task_id
    assert "error" in bob_get
    assert "result" not in bob_get
    assert alice_list["result"]["totalSize"] == 1
    assert bob_list["result"].get("totalSize", 0) == 0
    assert bob_list["result"].get("tasks", []) == []


def test_stored_failed_tasks_are_bounded(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(a2a, "_MAX_STORED_TASKS", 3)
    factory = Factory(fail_at="start")
    with TestClient(_app(factory)) as client:
        task_ids = [
            _send(client, "hi", f"ctx-{index}", {TOKEN_HEADER: _token("alice")}).json()["result"][
                "task"
            ]["id"]
            for index in range(5)
        ]
        listed = _rpc(client, "ListTasks", {}, _token("alice"))
        evicted = _rpc(client, "GetTask", {"id": task_ids[0]}, _token("alice"))

    assert listed["result"]["totalSize"] == 3
    assert "error" in evicted


def test_cancel_is_not_supported():
    executor = a2a._CommonsExecutor(a2a._Sessions(Factory(), 1))

    with pytest.raises(UnsupportedOperationError):
        asyncio.run(executor.cancel(cast("Any", None), cast("Any", None)))


@pytest.mark.parametrize(
    ("blocked", "message"),
    [
        (
            "fastapi",
            (
                "The 'fastapi' package is required to use this module. "
                "Install it with: pip install 'posit-sdk[a2a]'"
            ),
        ),
        (
            "a2a",
            (
                "The 'a2a-sdk' package is required to use this module. "
                "Install it with: pip install 'posit-sdk[a2a]'"
            ),
        ),
    ],
)
def test_import_without_dependency_raises_guard_message(blocked: str, message: str):
    code = f"import sys; sys.modules[{blocked!r}] = None; import posit.connect.external.a2a"

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )

    assert result.returncode != 0
    assert f"ImportError: {message}" in result.stderr
