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
from collections.abc import (
    AsyncIterable,
    AsyncIterator,
    Awaitable,
    Callable,
    Iterator,
    Sequence,
)
from contextlib import asynccontextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from urllib.parse import urlsplit

from typing_extensions import TYPE_CHECKING, Any, Literal, NamedTuple, Protocol

from ._a2a_request import A2ARequest, _request_scope, current_a2a_request, visitor_guid_from_token

try:
    from fastapi import FastAPI, Request
    from fastapi.responses import JSONResponse
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
_CARD_PATH = "/.well-known/agent-card.json"
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
_TOKEN_REQUIRED_TEXT = (
    "A Posit-Connect-User-Session-Token header that names a visitor is required."
)
_CARD_API_KEY_SCHEME = "connectApiKey"
_CURRENT_REQUEST: ContextVar[Request | None] = ContextVar(
    "commons_a2a_current_request", default=None
)

# Commons writes each tool result's trust tag under this key of the result's ``extra`` mapping, with
# the values "A" and "B". This relies on Commons internals (``commons._provenance``), which are not
# public API. A renamed key or value labels every answer Untrusted, so the failure is closed.
_TAG_EXTRA_KEY = "commons_tag"
_TRUSTED_TAG = "A"
# Commons labels an answer with this tag Cited only when its citation verifies. Commons keeps the
# verdict inside its citation scanner, so this server checks each citation itself. See
# `_cites_retrieved_context`.
_CITATION_TAG = "B"
# Only the output of this tool counts as retrieved context. A quote from any other tool, such as
# code output that the model wrote, cannot verify a citation.
_RETRIEVAL_TOOL = "search_context"
_CITATION_TITLE = '<span class="commons-citation-title">'
_CITATION_QUOTE = re.compile(r"^> ?")
_EMPHASIS = re.compile(r"[*_`]")
_WHITESPACE = re.compile(r"\s+")
# The folds that Commons applies to a quote and its source before it compares them.
_FOLDS = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"', "–": "-", "—": "-"})
_MIN_QUOTE_LENGTH = 10

_TRUSTED = "Trusted"
_CITED = "Cited"
_UNTRUSTED = "Untrusted"
# The body text of each badge, as Commons writes it. The server builds every badge from this table,
# so no badge in the answer text is ever forwarded.
_BADGES = {
    _TRUSTED: "This answer comes from a trusted calculation.",
    _CITED: "This answer cites context from a trusted source that supports its approach.",
    _UNTRUSTED: (
        "This answer was not produced by a trusted calculation and does not cite trusted context."
    ),
}
_BADGE_INFO = '<commons-provenance-info class="commons-provenance-info"></commons-provenance-info>'
# Matched without regard to case, so that an upper-case tag cannot pass through as answer text.
_ASIDE_OPEN = re.compile(r"<shiny-aside", re.IGNORECASE)
_ASIDE_CLOSE = re.compile(r"</shiny-aside>", re.IGNORECASE)
# The tags that Commons writes. Each one appears only inside an aside, so a stray one is removed.
_COMMONS_TAGS = re.compile(
    r"</?(?:span|blockquote|commons-provenance-info)\b[^<>]*>", re.IGNORECASE
)
_BLANK_LINE = re.compile(r"\n\s*\n")


class Agent(Protocol):
    """The part of a Commons agent that the A2A server uses.

    ``stream_async`` returns an async iterable of chunks. Only ``str`` chunks are kept. Other
    chunks are skipped. ``get_turns`` returns the conversation's turns, including the tool results
    of each turn. The server reads each answer's label from the turns that its message added.
    """

    async def stream_async(self, text: str, *, content: Literal["text"]) -> AsyncIterable[Any]:
        """Answer a question and return the answer as a stream of chunks."""
        ...

    def get_turns(self) -> Sequence[Any]:
        """Return the conversation's turns, in order."""
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

    Every request except the agent card must send a ``Posit-Connect-User-Session-Token`` header
    that names a visitor. A request without the header, or with a token that names no visitor, gets
    HTTP 401 before any agent runs. A request that carries more than one such header also gets HTTP
    401. The agent card is served without the header, for ``GET`` and ``HEAD`` requests. Agents and
    tasks are keyed by visitor, so without this check a client could share a conversation with
    another client by choosing its A2A context ID.

    A message with several text parts is one prompt. The parts are joined with newlines.

    The label of an answer comes from the tool results of its turn, never from its text.

    - A turn whose data tool ran and tagged its result as trusted is labelled Trusted.
    - A turn whose tool tagged its result as citing context is labelled Cited when every citation
      in the answer quotes a document that a ``search_context`` call returned in the same turn.
      Otherwise it is labelled Untrusted. A citation in an answer whose turn has no such tag does
      not make it Cited. Cited needs a ``search_context`` match. A quote of a measure definition or
      a dictionary is labelled Untrusted, because the server checks only ``search_context`` results.
    - Any other turn is labelled Untrusted. This includes a clarifying question and a turn whose
      tool failed.

    Citation asides in the answer are checked against the retrieved documents. Other asides never
    set the label. The server removes every aside from the text, so the text part has none.

    The reply has a second part after its text. The part is the badge for the reply's label: HTML
    with media type ``text/html``, and metadata that sets ``commons.kind`` to
    ``provenance-badge``. The server builds the badge from its own table, so the badge has no icon
    and no external URL.

    A turn that fails is stored as a failed task. The task is visible only to the visitor who sent
    the message. The store keeps the most recent 1000 saved tasks and deletes older ones.

    Parameters
    ----------
    agent_factory
        Builds the agent for a conversation. A conversation is one visitor and one A2A context. The
        factory runs on the first message of each conversation. The server keeps that agent for
        later messages, so the factory does not see later messages' session tokens. A tool that
        needs the visitor's credentials calls `current_a2a_request` at call time. The factory must
        return quickly, because it runs on the event loop. The agent must implement
        ``stream_async`` and ``get_turns``.
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
        slot, the least recently used conversation with no message in flight loses its agent, and
        its next message starts a new conversation. A conversation with a message in flight or
        queued is not evicted, so the limit can be exceeded while every other conversation is busy.
        A conversation whose turn fails also loses its agent.

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
    app.add_middleware(_RequireSessionToken)
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
    # Connect appends its own value of this header after any value the client sent, so the last
    # value is Connect's. A client can send earlier values, so only the last one is used. Unlike
    # the session token, which Connect overwrites, this header keeps client values.
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


class _RequireSessionToken:
    """Answer HTTP 401 to each request that does not name a visitor, except the agent card."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or _is_agent_card(scope):
            await self.app(scope, receive, send)
            return
        # Connect overwrites this header with its own value, so a request that carries two values
        # did not come through Connect as a whole. The request is refused, and no value is read.
        values = Request(scope).headers.getlist(_SESSION_TOKEN_HEADER)
        token = values[0] if len(values) == 1 else None
        if visitor_guid_from_token(token) is None:
            response = JSONResponse({"error": _TOKEN_REQUIRED_TEXT}, status_code=401)
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


def _is_agent_card(scope: Scope) -> bool:
    return scope["method"] in ("GET", "HEAD") and scope["path"].endswith(_CARD_PATH)


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
        # The middleware refuses a request with more than one token value, so the first is the only.
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
    # Messages that are queued on the lock or running. A session with a count above zero is kept.
    in_flight: int = 0
    # Set when a turn ends in an error or a cancellation. The agent is rebuilt before the next turn.
    stale: bool = False


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

    @asynccontextmanager
    async def turn(self, request: A2ARequest) -> AsyncIterator[Agent]:
        """Yield the conversation's agent after the messages before it in the conversation finish.

        A turn that ends in an error or a cancellation marks the session stale. The next turn that
        gets the lock builds a new agent before it runs, so one key never has two agents running.
        The session counts as in flight from the moment the message arrives until its turn ends.
        Eviction cannot remove a session with a message queued behind another message.
        """
        session = self.session_for(request)
        session.in_flight += 1
        try:
            async with session.lock:
                if session.stale:
                    session.agent = self._factory(request)
                    session.stale = False
                try:
                    yield session.agent
                except BaseException:
                    session.stale = True
                    raise
        finally:
            session.in_flight -= 1

    def _evict_idle(self, keep: _SessionKey) -> None:
        """Evict least recently used sessions with no message in flight until the limit holds."""
        while len(self._sessions) > self._max_contexts:
            victim = next(
                (
                    key
                    for key, session in self._sessions.items()
                    if key != keep and session.in_flight == 0
                ),
                None,
            )
            if victim is None:
                return
            del self._sessions[victim]


class _Answer(NamedTuple):
    """One agent answer: the model's text with its asides, and the label of its turn."""

    raw: str
    provenance: str


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
            answer = await self._answer(context, request)
            reply = _reply(answer, context_id)
        except Exception:
            logger.exception("The agent failed in A2A context %r.", context_id)
            await event_queue.enqueue_event(_failed_task(context, context_id))
            return
        await event_queue.enqueue_event(reply)

    async def cancel(self, context: RequestContext, event_queue: EventQueue) -> None:  # noqa: ARG002
        raise UnsupportedOperationError()

    async def _answer(self, context: RequestContext, request: A2ARequest) -> _Answer:
        with _request_scope(request):
            async with self._sessions.turn(request) as agent:
                before = len(agent.get_turns())
                stream = await agent.stream_async(context.get_user_input(), content="text")
                chunks = [chunk async for chunk in stream]
                exchange = agent.get_turns()[before:]
        raw = "".join(chunk for chunk in chunks if isinstance(chunk, str))
        return _Answer(raw=raw, provenance=_provenance_label(exchange, raw))


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


def _reply(answer: _Answer, context_id: str) -> Message:
    message = new_text_message(_visible_text(answer.raw), context_id=context_id)
    message.metadata.update({"commons": {"provenance": answer.provenance}})
    badge_part = Part(text=_badge_html(answer.provenance), media_type="text/html")
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


def _provenance_label(turns: Sequence[Any], raw: str) -> str:
    """Return the label of one exchange.

    The turns are the ones the exchange added, read after its stream ends. A B tag on a tool result
    makes the answer Cited when its citations verify, and Untrusted otherwise. An A tag alone makes
    the answer Trusted. The answer text matters only through its citations, and those are checked
    against the documents that the exchange retrieved.
    """
    tags = _tool_tags(turns)
    if _CITATION_TAG in tags:
        return _CITED if _cites_retrieved_context(turns, raw) else _UNTRUSTED
    return _TRUSTED if _TRUSTED_TAG in tags else _UNTRUSTED


def _cites_retrieved_context(turns: Sequence[Any], raw: str) -> bool:
    """Return whether the answer has citations and each one quotes a retrieved document.

    A citation is an aside whose body opens with Commons' title row. Its quote is the one run of
    blockquote lines. A malformed citation, or a quote that no retrieved document contains, fails
    the check, so one bad citation makes the answer not Cited.
    """
    quotes = _citation_quotes(raw)
    retrieved = _retrieved_texts(turns)
    return bool(quotes) and all(_is_retrieved(quote, retrieved) for quote in quotes)


def _citation_quotes(raw: str) -> list[str | None]:
    """Return the quote of each citation aside in the answer. None marks a malformed citation."""
    bodies = (_aside_body(raw[start:end]) for start, end in _asides(raw))
    return [_quote_of(body) for body in bodies if body.startswith(_CITATION_TITLE)]


def _aside_body(aside: str) -> str:
    """Return the text of an aside after its opening tag, without its closing tag."""
    return _ASIDE_CLOSE.sub("", aside[aside.find(">") + 1 :])


def _quote_of(body: str) -> str | None:
    """Return the quote in a citation body, or None unless it holds exactly one blockquote run."""
    lines = body.split("\n")
    quoted = [line.startswith(">") for line in lines]
    runs = sum(
        1 for index, flag in enumerate(quoted) if flag and (index == 0 or not quoted[index - 1])
    )
    if runs != 1:
        return None
    kept = [line for line, flag in zip(lines, quoted, strict=True) if flag]
    return "\n".join(_CITATION_QUOTE.sub("", line) for line in kept)


def _retrieved_texts(turns: Sequence[Any]) -> list[str]:
    """Return the normalized output of each successful retrieval call in the turns."""
    texts: list[str] = []
    for turn in turns:
        for content in turn.contents:
            if _is_retrieval_result(content):
                texts.append(_normalize(content.value))
    return texts


def _is_retrieval_result(content: Any) -> bool:
    """Return whether a content is a successful result of the retrieval tool."""
    request = getattr(content, "request", None)
    return (
        getattr(request, "name", None) == _RETRIEVAL_TOOL
        and getattr(content, "error", None) is None
        and isinstance(getattr(content, "value", None), str)
    )


def _is_retrieved(quote: str | None, retrieved: Sequence[str]) -> bool:
    """Return whether a quote, normalized as Commons normalizes it, appears in a retrieved text."""
    if quote is None:
        return False
    needle = _normalize(quote)
    return len(needle) >= _MIN_QUOTE_LENGTH and any(needle in text for text in retrieved)


def _normalize(text: str) -> str:
    """Fold a text the way Commons folds a quote and its source before they are compared."""
    text = _EMPHASIS.sub("", text).translate(_FOLDS)
    return _WHITESPACE.sub(" ", text).strip()


def _tool_tags(turns: Sequence[Any]) -> set[str]:
    """Return the string tags that the turns' contents carry in their ``extra`` mappings.

    Only tool results carry the key. A tag that is not a string is ignored.
    """
    tags: set[str] = set()
    for turn in turns:
        for content in turn.contents:
            extra = getattr(content, "extra", None) or {}
            value = extra.get(_TAG_EXTRA_KEY)
            if isinstance(value, str):
                tags.add(value)
    return tags


def _badge_html(label: str) -> str:
    return f'<shiny-aside label="{label}">{_BADGES[label]} {_BADGE_INFO}</shiny-aside>'


def _visible_text(raw: str) -> str:
    """Return the answer's text without its asides, its Commons tags, or its extra blank lines."""
    text = _COMMONS_TAGS.sub("", _ASIDE_CLOSE.sub("", _outside_asides(raw)))
    return _BLANK_LINE.sub("\n\n", text).strip()


def _outside_asides(raw: str) -> str:
    """Return the text that lies outside every aside."""
    kept: list[str] = []
    position = 0
    for start, end in _asides(raw):
        kept.append(raw[position:start])
        position = end
    kept.append(raw[position:])
    return "".join(kept)


def _asides(raw: str) -> Iterator[tuple[int, int]]:
    """Yield the start and end positions of each aside, in order."""
    position = 0
    while (opened := _ASIDE_OPEN.search(raw, position)) is not None:
        position = _aside_end(raw, opened.start())
        yield opened.start(), position


def _aside_end(raw: str, start: int) -> int:
    """Return the position after the aside that opens at ``start``.

    An aside ends at its closing tag, or at the next opening tag, or at the end of the text. The
    searches stop at the next opening tag, so each character is scanned once.
    """
    boundary = _ASIDE_OPEN.search(raw, start + 1)
    limit = len(raw) if boundary is None else boundary.start()
    close = _ASIDE_CLOSE.search(raw, start, limit)
    return limit if close is None else close.end()
