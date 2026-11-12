"""Serve a Commons agent over the Agent2Agent (A2A) protocol.

`create_a2a_app` returns a FastAPI application with an agent card and a JSON-RPC endpoint. Each
conversation, identified by the visitor and the A2A context, has its own agent. The agent factory
builds it when the conversation first sends a message.

Routes
------
``GET /.well-known/agent-card.json``
    The agent card. Its public URLs come from the request. See `create_a2a_app`.
``POST /a2a/jsonrpc``
    The JSON-RPC endpoint. The ``SendMessage`` method starts an agent turn.

Notes
-----
The APIs in this module are provided as a convenience and are subject to breaking changes.
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from collections import OrderedDict
from collections.abc import AsyncIterable, Awaitable, Callable, Sequence
from contextvars import ContextVar
from dataclasses import dataclass
from urllib.parse import urlsplit

from typing_extensions import TYPE_CHECKING, Any, Literal, NamedTuple, Protocol

from ._a2a_request import A2ARequest, _request_scope, current_a2a_request, visitor_guid_from_token

try:
    from fastapi import FastAPI, Request
except ImportError as e:
    raise ImportError(
        "The 'fastapi' package is required to use this module. "
        "Install it with: pip install 'posit-sdk[a2a]'"
    ) from e

try:
    from a2a.auth.user import User
    from a2a.helpers.proto_helpers import new_text_message
    from a2a.server.agent_execution import AgentExecutor
    from a2a.server.request_handlers import DefaultRequestHandler
    from a2a.server.routes import (
        DefaultServerCallContextBuilder,
        ServerCallContextBuilder,
        add_a2a_routes_to_fastapi,
        create_agent_card_routes,
        create_jsonrpc_routes,
    )
    from a2a.server.tasks.inmemory_task_store import InMemoryTaskStore
    from a2a.server.tasks.task_store import TaskStore
    from a2a.types import (
        AgentCapabilities,
        AgentCard,
        AgentInterface,
        AgentProvider,
        APIKeySecurityScheme,
        Part,
        SecurityRequirement,
        SecurityScheme,
        StringList,
        Task,
        TaskState,
        TaskStatus,
    )
    from a2a.utils.constants import PROTOCOL_VERSION_1_0
    from a2a.utils.errors import UnsupportedOperationError
except ImportError as e:
    raise ImportError(
        "The 'a2a-sdk' package is required to use this module. "
        "Install it with: pip install 'posit-sdk[a2a]'"
    ) from e

if TYPE_CHECKING:
    from a2a.server.agent_execution import RequestContext
    from a2a.server.context import ServerCallContext
    from a2a.server.events.event_queue import EventQueue
    from a2a.types import AgentSkill, ListTasksRequest, ListTasksResponse, Message
    from starlette.types import ASGIApp, Receive, Scope, Send

__all__ = [
    "A2ARequest",
    "Agent",
    "AgentFactory",
    "create_a2a_app",
    "current_a2a_request",
]

logger = logging.getLogger(__name__)

_JSONRPC_PATH = "/a2a/jsonrpc"
_SESSION_TOKEN_HEADER = "posit-connect-user-session-token"
_BASE_URL_HEADER = "rstudio-connect-app-base-url"
_ALLOWED_HEADERS = frozenset(
    {
        _SESSION_TOKEN_HEADER,
        "rstudio-connect-credentials",
        _BASE_URL_HEADER,
        "a2a-version",
        "user-agent",
        "accept-language",
    }
)
_MAX_STORED_TASKS = 1000
_FAILURE_TEXT = "The agent could not answer this request. Try again later."
_CARD_API_KEY_SCHEME = "connectApiKey"
_CURRENT_REQUEST: ContextVar[Request | None] = ContextVar(
    "commons_a2a_current_request", default=None
)

_CITED = "Cited"
# The label of an answer that Commons gave no label. Commons derives no tag when no successful data
# tool ran, such as for a clarifying question or a tool error, so the server reports such an answer
# as Untrusted.
_UNTRUSTED = "Untrusted"
# A label that ranks higher is less trusted. The least trusted label in an answer is reported.
_PROVENANCE_RANK = {"Trusted": 0, _CITED: 1, _UNTRUSTED: 2}
_ASIDE_OPEN = "<shiny-aside"
_ASIDE_CLOSE = "</shiny-aside>"
_LABEL = re.compile(r"""\slabel=["'](?P<label>[^"']*)["']""")
# The tags that Commons writes. Each one appears only inside an aside, so a stray one is removed.
_COMMONS_TAGS = re.compile(r"</?(?:span|blockquote|commons-provenance-info)\b[^<>]*>")
_BLANK_LINE = re.compile(r"\n\s*\n")
# The opening tag of a Commons aside: its label, and its icon when Commons serves one.
_OPEN_TAG = re.compile(r"""<shiny-aside label="(?P<label>[^"]*)"(?: icon="(?P<icon>[^"]*)")?>""")
# A provenance badge is an aside whose label, icon, and body match a badge that Commons writes.
# Any other aside, including a citation, is not a badge, so its HTML is not forwarded.
# A verified citation's body starts with this title row, which Commons writes before the quote.
_CITATION_TITLE = '<span class="commons-citation-title">'
_BADGE_INFO = '<commons-provenance-info class="commons-provenance-info"></commons-provenance-info>'
# The icon's base is a relative path or an http(s) URL with no quote, angle bracket, or whitespace.
_ICON_BASE = re.compile(r"""(?:https?://|/)[^\s"<>]*""")
_BADGE_MAX_CHARS = 20_000
_TRUSTED_BODY = "This answer comes from a trusted calculation."
_CITED_BODY = "This answer cites context from a trusted source that supports its approach."
_UNTRUSTED_BODY = (
    "This answer was not produced by a trusted calculation and does not cite trusted context."
)


class _Badge(NamedTuple):
    body: str
    icon_file: str | None


# The text and icon file of each badge, as Commons writes them. Cited has no icon.
_BADGES = {
    "Trusted": _Badge(_TRUSTED_BODY, "trusted-icon.svg"),
    "Cited": _Badge(_CITED_BODY, None),
    "Untrusted": _Badge(_UNTRUSTED_BODY, "warning-icon.svg"),
}
# Commons writes no badge for a Cited answer or for an answer with no label. The server builds those
# badges from the table, without an icon.
_BUILT_BADGES = {
    label: f'<shiny-aside label="{label}">{_BADGES[label].body} {_BADGE_INFO}{_ASIDE_CLOSE}'
    for label in (_CITED, _UNTRUSTED)
}


class Agent(Protocol):
    """The part of a Commons agent that the A2A server uses.

    ``stream_async`` returns an async iterable of chunks. Only ``str`` chunks are kept. Other
    chunks are skipped.
    """

    async def stream_async(self, text: str, *, content: Literal["text"]) -> AsyncIterable[Any]:
        """Answer a question and return the answer as a stream of chunks."""
        ...


AgentFactory = Callable[[A2ARequest], Agent]
"""Builds the agent for a conversation.

The server calls it synchronously, on the event loop. It runs for the first message of a
conversation, and again after the conversation's agent is evicted or its turn fails.
"""


def create_a2a_app(
    agent_factory: AgentFactory,
    *,
    name: str,
    description: str,
    skills: Sequence[AgentSkill],
    version: str = "0.1.0",
    max_contexts: int = 100,
) -> FastAPI:
    """Create a FastAPI application that serves agents over A2A.

    The agent card's public URLs are computed for each request, in this order:

    1. The ``RStudio-Connect-App-Base-URL`` header. Connect appends its own value after any value
       that the client sent, so the last value is used. It must be an ``http`` or ``https`` URL.
    2. ``CONNECT_SERVER`` and ``CONNECT_CONTENT_GUID``, joined as ``<server>/content/<guid>``.
    3. The base URL of the request.

    Trailing slashes are removed from the base URL. The card's provider URL is
    ``CONNECT_SERVER`` when it is set, and the base URL otherwise.

    The application does not check API keys. Connect authenticates the request before it reaches
    the content, and Connect removes the ``Authorization`` header.

    A message with several text parts is one prompt. The parts are joined with newlines.

    An answer with a provenance badge has a second part after its text. The part's text is the
    badge's HTML, its media type is ``text/html``, and its metadata sets ``commons.kind`` to
    ``provenance-badge``. The part is omitted when the HTML is longer than 20,000 characters.
    An answer with no label from Commons is Untrusted, and its second part is the Untrusted badge.
    A Cited answer's second part is the Cited badge. The server builds both badges, because Commons
    writes neither for these answers.

    A turn that fails is stored as a failed task. The task is visible only to the visitor who sent
    the message. The store keeps the most recent 1000 saved tasks and deletes older ones. Requests
    without a session token share one owner, so they can see each other's tasks.

    Parameters
    ----------
    agent_factory
        Builds the agent for a conversation. A conversation is one visitor and one A2A context. The
        factory runs on the first message of each conversation. The server keeps that agent for
        later messages, so the factory does not see later messages' session tokens. A tool that
        needs the visitor's credentials calls `current_a2a_request` at call time. The factory must
        return quickly, because it runs on the event loop.
    name
        The agent's name, shown in the agent card and the API docs.
    description
        The agent's description.
    skills
        The skills that the agent card lists.
    version
        The agent's version.
    max_contexts
        The number of conversations that keep an agent in memory. When a new conversation needs a
        slot, the least recently used idle conversation loses its agent, and its next message starts
        a new conversation. A conversation with a message in flight is not evicted, so the limit can
        be exceeded while every other conversation is busy. A conversation whose turn fails also
        loses its agent.

    Returns
    -------
    FastAPI
        The application. It serves the agent card at ``/.well-known/agent-card.json`` and the
        JSON-RPC endpoint at ``/a2a/jsonrpc``.

    Raises
    ------
    ValueError
        If ``max_contexts`` is less than 1.
    """
    if max_contexts < 1:
        raise ValueError("max_contexts must be at least 1.")
    template = _build_card(name, description, version, skills, base_url="")
    handler = DefaultRequestHandler(
        agent_executor=_CommonsExecutor(_Sessions(agent_factory, max_contexts)),
        task_store=_BoundedTaskStore(_MAX_STORED_TASKS),
        agent_card=template,
    )
    app = FastAPI(title=name, description=description, version=version)
    app.add_middleware(_RequestCapture)
    add_a2a_routes_to_fastapi(
        app,
        agent_card_routes=create_agent_card_routes(
            template,
            card_modifier=_localized_card(name, description, version, skills),
        ),
        jsonrpc_routes=create_jsonrpc_routes(
            handler,
            rpc_url=_JSONRPC_PATH,
            context_builder=_VisitorContextBuilder(),
        ),
    )
    return app


def _localized_card(
    name: str,
    description: str,
    version: str,
    skills: Sequence[AgentSkill],
) -> Callable[[AgentCard], Awaitable[AgentCard]]:
    async def modify(_: AgentCard) -> AgentCard:
        request = _CURRENT_REQUEST.get()
        base_url = "" if request is None else _public_base_url(request)
        return _build_card(name, description, version, skills, base_url)

    return modify


def _build_card(
    name: str,
    description: str,
    version: str,
    skills: Sequence[AgentSkill],
    base_url: str,
) -> AgentCard:
    api_key = APIKeySecurityScheme(
        location="header",
        name="Authorization",
        description="Posit Connect API key, sent as `Key <api-key>`.",
    )
    card = AgentCard(
        name=name,
        description=description,
        version=version,
        skills=list(skills),
        default_input_modes=["text/plain"],
        default_output_modes=["text/plain"],
        capabilities=AgentCapabilities(streaming=False),
        supported_interfaces=[
            AgentInterface(
                url=f"{base_url}{_JSONRPC_PATH}",
                protocol_binding="JSONRPC",
                protocol_version=PROTOCOL_VERSION_1_0,
            )
        ],
        security_schemes={_CARD_API_KEY_SCHEME: SecurityScheme(api_key_security_scheme=api_key)},
        security_requirements=[
            SecurityRequirement(schemes={_CARD_API_KEY_SCHEME: StringList(list=[])})
        ],
    )
    provider_url = _connect_server() or base_url
    if provider_url:
        card.provider.CopyFrom(AgentProvider(organization="Posit Connect", url=provider_url))
    return card


def _connect_server() -> str:
    return os.environ.get("CONNECT_SERVER", "").rstrip("/")


def _public_base_url(request: Request) -> str:
    forwarded = _forwarded_base_url(request)
    if forwarded is not None:
        return forwarded
    guid = os.environ.get("CONNECT_CONTENT_GUID", "")
    server = _connect_server()
    if server and guid:
        return f"{server}/content/{guid}"
    return str(request.base_url).rstrip("/")


def _forwarded_base_url(request: Request) -> str | None:
    # Connect appends its own header value after any value the client sent, so the last one is
    # Connect's. An earlier value is client-controlled and is never used.
    values = request.headers.getlist(_BASE_URL_HEADER)
    if not values:
        return None
    candidate = values[-1].strip().rstrip("/")
    parts = urlsplit(candidate)
    if parts.scheme in ("http", "https") and parts.netloc:
        return candidate
    return None


class _RequestCapture:
    """Record each HTTP request so that the card modifier can read its headers and URL."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        token = _CURRENT_REQUEST.set(Request(scope))
        try:
            await self.app(scope, receive, send)
        finally:
            _CURRENT_REQUEST.reset(token)


class _VisitorUser(User):
    """The visitor named by the session token. The SDK scopes tasks by ``user_name``."""

    def __init__(self, visitor_guid: str | None) -> None:
        self._visitor_guid = visitor_guid

    @property
    def is_authenticated(self) -> bool:
        return self._visitor_guid is not None

    @property
    def user_name(self) -> str:
        return self._visitor_guid or ""


class _VisitorContextBuilder(ServerCallContextBuilder):
    """Builds call contexts whose user is the visitor, so that tasks are scoped to the visitor."""

    def __init__(self) -> None:
        self._default = DefaultServerCallContextBuilder()

    def build(self, request: Request) -> ServerCallContext:
        context = self._default.build(request)
        token = request.headers.get(_SESSION_TOKEN_HEADER)
        context.user = _VisitorUser(visitor_guid_from_token(token))
        return context


class _BoundedTaskStore(TaskStore):
    """In-memory tasks, scoped by owner, that keeps the most recently saved ``limit`` tasks.

    The store records the call context of each saved task, so an evicted task is deleted under the
    owner that saved it.
    """

    def __init__(self, limit: int) -> None:
        self._store = InMemoryTaskStore()
        self._limit = limit
        self._saved: OrderedDict[tuple[str, str], ServerCallContext] = OrderedDict()

    async def save(self, task: Task, context: ServerCallContext) -> None:
        await self._store.save(task, context)
        key = (context.user.user_name, task.id)
        self._saved[key] = context
        self._saved.move_to_end(key)
        while len(self._saved) > self._limit:
            (_, task_id), evicted = self._saved.popitem(last=False)
            await self._store.delete(task_id, evicted)

    async def get(self, task_id: str, context: ServerCallContext) -> Task | None:
        return await self._store.get(task_id, context)

    async def list(
        self, params: ListTasksRequest, context: ServerCallContext
    ) -> ListTasksResponse:
        return await self._store.list(params, context)

    async def delete(self, task_id: str, context: ServerCallContext) -> None:
        await self._store.delete(task_id, context)
        self._saved.pop((context.user.user_name, task_id), None)


@dataclass
class _Session:
    agent: Agent
    lock: asyncio.Lock


_SessionKey = tuple[str | None, str]


def _session_key(request: A2ARequest) -> _SessionKey:
    return (request.visitor_guid, request.context_id)


class _Sessions:
    """Agents for conversations, keyed by visitor and A2A context.

    The key includes the visitor, so a context ID that another visitor sends never reaches
    the first visitor's agent.
    """

    def __init__(self, factory: AgentFactory, max_contexts: int) -> None:
        self._factory = factory
        self._max_contexts = max_contexts
        self._sessions: OrderedDict[_SessionKey, _Session] = OrderedDict()

    def session_for(self, request: A2ARequest) -> _Session:
        """Return the conversation's session, creating it with the factory when it is new."""
        key = _session_key(request)
        session = self._sessions.get(key)
        if session is None:
            session = _Session(agent=self._factory(request), lock=asyncio.Lock())
            self._sessions[key] = session
            self._evict_idle(keep=key)
        self._sessions.move_to_end(key)
        return session

    def discard(self, request: A2ARequest) -> None:
        """Drop the conversation's session, so that its next message starts a new agent."""
        self._sessions.pop(_session_key(request), None)

    def _evict_idle(self, keep: _SessionKey) -> None:
        """Evict least recently used idle sessions until the limit holds.

        A session whose lock is held has a message in flight, so it is kept.
        """
        while len(self._sessions) > self._max_contexts:
            victim = next(
                (
                    key
                    for key, session in self._sessions.items()
                    if key != keep and not session.lock.locked()
                ),
                None,
            )
            if victim is None:
                return
            del self._sessions[victim]


class _CommonsExecutor(AgentExecutor):
    """Answers each A2A message with one agent message, or one failed task."""

    def __init__(self, sessions: _Sessions) -> None:
        self._sessions = sessions

    async def execute(self, context: RequestContext, event_queue: EventQueue) -> None:
        # The SDK sets the context ID of every SendMessage request, generating one if needed.
        assert context.context_id is not None
        context_id = context.context_id
        request = _a2a_request(context, context_id)
        try:
            raw = await self._answer(context, request)
            reply = _reply(_parse_answer(raw), context_id)
        except Exception:
            logger.exception("The agent failed in A2A context %r.", context_id)
            self._sessions.discard(request)
            await event_queue.enqueue_event(_failed_task(context, context_id))
            return
        await event_queue.enqueue_event(reply)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:  # noqa: ARG002
        raise UnsupportedOperationError()

    async def _answer(self, context: RequestContext, request: A2ARequest) -> str:
        with _request_scope(request):
            session = self._sessions.session_for(request)
            async with session.lock:
                stream = await session.agent.stream_async(context.get_user_input(), content="text")
                chunks = [chunk async for chunk in stream]
        return "".join(chunk for chunk in chunks if isinstance(chunk, str))


def _a2a_request(context: RequestContext, context_id: str) -> A2ARequest:
    state_headers = context.call_context.state.get("headers", {})
    headers = {name: value for name, value in state_headers.items() if name in _ALLOWED_HEADERS}
    token = headers.get(_SESSION_TOKEN_HEADER)
    return A2ARequest(
        context_id=context_id,
        user_session_token=token,
        visitor_guid=visitor_guid_from_token(token),
        headers=headers,
    )


class _Answer(NamedTuple):
    """An answer split into the parts that its reply carries."""

    text: str
    provenance: str | None
    badge: str | None


def _reply(answer: _Answer, context_id: str) -> Message:
    message = new_text_message(answer.text, context_id=context_id)
    message.metadata.update({"commons": {"provenance": answer.provenance}})
    if answer.badge is not None:
        badge_part = Part(text=answer.badge, media_type="text/html")
        badge_part.metadata.update({"commons": {"kind": "provenance-badge"}})
        message.parts.append(badge_part)
    return message


def _failed_task(context: RequestContext, context_id: str) -> Task:
    status_message = new_text_message(
        _FAILURE_TEXT, context_id=context_id, task_id=context.task_id
    )
    return Task(
        id=context.task_id,
        context_id=context_id,
        status=TaskStatus(state=TaskState.TASK_STATE_FAILED, message=status_message),
    )


def _parse_answer(raw: str) -> _Answer:
    """Split a raw answer into its plain text, its provenance label, and its badge HTML.

    The asides are removed from the text. The Commons tags that appear outside an aside are removed
    too. Other text, including angle brackets, is kept as written. The label and badge come from
    ``_provenance_and_badge``. The badge is None when there is none, or when its HTML is longer than
    ``_BADGE_MAX_CHARS``.
    """
    text, asides = _split_asides(raw)
    text = _COMMONS_TAGS.sub("", text.replace(_ASIDE_CLOSE, ""))
    provenance, html = _provenance_and_badge(asides)
    return _Answer(
        text=_BLANK_LINE.sub("\n\n", text).strip(),
        provenance=provenance,
        badge=html if html and len(html) <= _BADGE_MAX_CHARS else None,
    )


def _provenance_and_badge(asides: list[tuple[str | None, str]]) -> tuple[str, str]:
    """Return the answer's label, and the HTML of its badge (an empty string for no badge).

    An explicit Commons label wins. Otherwise a verified citation makes the answer Cited. Otherwise
    the answer is Untrusted. Commons derives no tag when no successful data tool ran, for example for
    a clarifying question, so such an answer has no calculation or citation behind it.
    """
    label = _least_trusted([label for label, html in asides if not _is_citation(html)])
    if label is not None:
        return label, "\n".join(html for _, html in asides if _is_provenance_badge(html))
    if any(_is_citation(html) for _, html in asides):
        return _CITED, _BUILT_BADGES[_CITED]
    return _UNTRUSTED, _BUILT_BADGES[_UNTRUSTED]


def _is_citation(aside: str) -> bool:
    """Return whether an aside is a verified citation exactly as Commons writes it.

    Commons writes the citation's title row first, then its quote, and closes the aside.
    """
    match = _OPEN_TAG.match(aside)
    return (
        match is not None
        and aside.startswith(_CITATION_TITLE, match.end())
        and aside.endswith(_ASIDE_CLOSE)
    )


def _is_provenance_badge(aside: str) -> bool:
    """Return whether an aside's HTML is a provenance badge exactly as Commons writes it."""
    match = _OPEN_TAG.match(aside)
    if match is None:
        return False
    badge = _BADGES.get(match.group("label"))
    if badge is None or not _icon_matches(match.group("icon"), badge.icon_file):
        return False
    return aside[match.end() :] == f"{badge.body} {_BADGE_INFO}{_ASIDE_CLOSE}"


def _icon_matches(icon: str | None, icon_file: str | None) -> bool:
    """Return whether a badge's icon attribute is absent or is the icon that Commons serves.

    Commons omits the attribute when it serves no asset bundle. Otherwise the value is the bundle's
    base, then ``/figs/``, then the badge's icon file.
    """
    if icon is None:
        return True
    if icon_file is None:
        return False
    suffix = f"/figs/{icon_file}"
    return icon.endswith(suffix) and _ICON_BASE.fullmatch(icon[: -len(suffix)]) is not None


def _split_asides(raw: str) -> tuple[str, list[tuple[str | None, str]]]:
    """Return the text outside the asides, and each aside's label and HTML, in order."""
    kept: list[str] = []
    asides: list[tuple[str | None, str]] = []
    position = 0
    while (start := raw.find(_ASIDE_OPEN, position)) != -1:
        kept.append(raw[position:start])
        label, position = _scan_aside(raw, start)
        asides.append((label, raw[start:position]))
    kept.append(raw[position:])
    return "".join(kept), asides


def _scan_aside(raw: str, start: int) -> tuple[str | None, int]:
    """Return the label of the aside that opens at ``start``, and the position after it.

    An aside ends at its closing tag, or at the next opening tag, or at the end of the text. The
    searches stop at the next opening tag, so each character is scanned once.
    """
    boundary = raw.find(_ASIDE_OPEN, start + len(_ASIDE_OPEN))
    limit = len(raw) if boundary == -1 else boundary
    tag_end = raw.find(">", start, limit)
    if tag_end == -1:
        return _label_between(raw, start, limit), limit
    label = _label_between(raw, start, tag_end)
    close = raw.find(_ASIDE_CLOSE, tag_end + 1, limit)
    if close == -1:
        return label, limit
    return label, close + len(_ASIDE_CLOSE)


def _label_between(raw: str, start: int, end: int) -> str | None:
    match = _LABEL.search(raw, start, end)
    return None if match is None else match.group("label")


def _least_trusted(labels: list[str | None]) -> str | None:
    known = [label for label in labels if label is not None and label in _PROVENANCE_RANK]
    return max(known, key=_PROVENANCE_RANK.__getitem__, default=None)
