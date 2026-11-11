"""Commons feedback tool.

Give a Commons agent a tool that it calls when the asker cannot get the answer they need. The tool
builds a feedback report from the conversation and hands it to a transport, which delivers it to a
curator.

The default transport, `MockFeedbackTransport`, keeps reports in memory and logs them. It does not
deliver reports to a curator, and its receipt says so.

Notes
-----
The APIs in this module are provided as a convenience and are subject to breaking changes.
"""

from __future__ import annotations

import logging
import os
import re
import uuid
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone

from typing_extensions import Any, Protocol

from ._a2a_request import current_a2a_request

try:
    import chatlas
except ImportError as e:
    raise ImportError(
        "The 'chatlas' package is required to use this module. "
        "Install it with: pip install 'posit-sdk[commons]'"
    ) from e

logger = logging.getLogger(__name__)

TOOL_NAME = "send_curation_feedback"
TOOL_DESCRIPTION = (
    "Notify a curator that the asker needs an answer that you could not provide. Call this only "
    "after you have tried to answer with the available tools and cannot. The result says whether "
    "the request was sent. Tell the asker what the result says."
)
MAX_TRANSCRIPT_TURNS = 20
"""The number of most recent user and assistant turns that a report keeps."""
MAX_TURN_CHARACTERS = 2000
"""The longest text that a transcript entry, question, or reason keeps.

Longer text ends with ``...``.
"""
MAX_MOCK_REPORTS = 100
"""The number of reports that `MockFeedbackTransport` keeps. Older reports are dropped."""
_TRANSCRIPT_ROLES = ("user", "assistant")
_NOT_SENT_TEXT = (
    "The feedback request was not sent because of a server error. Tell the asker that the "
    "request failed and that they can try again later."
)
_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")


@dataclass(frozen=True)
class FeedbackReport:
    """A feedback request for a curator.

    Attributes
    ----------
    question
        The question that the agent could not answer. The model supplies it, and it is at most
        `MAX_TURN_CHARACTERS` characters long.
    reason
        Why the agent could not answer. The model supplies it, and it is at most
        `MAX_TURN_CHARACTERS` characters long.
    requested_by
        The visitor's username or GUID, if known.
    content_guid
        The value of the ``CONNECT_CONTENT_GUID`` environment variable, if set.
    transcript
        The most recent turns of the conversation. Each entry has a ``role`` (``"user"`` or
        ``"assistant"``) and a ``text``. A report keeps at most `MAX_TRANSCRIPT_TURNS` turns, and
        each text is at most `MAX_TURN_CHARACTERS` characters long.
    created_at
        The time that the agent created the report, in ISO-8601 format with UTC offset.
    """

    question: str
    reason: str
    requested_by: str | None
    content_guid: str | None
    transcript: list[dict[str, str]]
    created_at: str


@dataclass(frozen=True)
class FeedbackReceipt:
    """The acknowledgement that a transport returns for a report.

    Attributes
    ----------
    id
        The identifier of the request.
    status
        The state of the request, such as ``"queued"``.
    message
        The text that the agent shows the asker. It states what the transport did with the report.
    """

    id: str
    status: str
    message: str


class FeedbackTransport(Protocol):
    """Delivers feedback reports to a curator."""

    def send(self, report: FeedbackReport) -> FeedbackReceipt:
        """Deliver a report and return its receipt."""
        ...


class MockFeedbackTransport:
    """Keep feedback reports in memory and log them. It does not deliver them to a curator.

    Attributes
    ----------
    reports
        The most recent `MAX_MOCK_REPORTS` reports, in the order sent.
    """

    def __init__(self) -> None:
        self.reports: deque[FeedbackReport] = deque(maxlen=MAX_MOCK_REPORTS)

    def send(self, report: FeedbackReport) -> FeedbackReceipt:
        """Record a report, log it, and return a queued receipt with a new UUID."""
        self.reports.append(report)
        receipt_id = str(uuid.uuid4())
        logger.info("Feedback request %s recorded: %s", receipt_id, _log_safe(report.question))
        return FeedbackReceipt(
            id=receipt_id,
            status="queued",
            message=(
                f"Feedback recorded as {receipt_id} (demo transport: logged on the server only, "
                "not delivered to a curator)."
            ),
        )


class _Agent(Protocol):
    """The part of a Commons agent that the feedback tool uses."""

    def get_turns(self) -> Any: ...

    def register_tool(self, tool: chatlas.Tool, /) -> Any: ...


def feedback_tool(
    agent: _Agent,
    transport: FeedbackTransport | None = None,
    *,
    requested_by: str | None = None,
) -> chatlas.Tool:
    """Return a tool that sends a feedback report when the agent calls it.

    The tool is synchronous, so it runs under both ``chat()`` and ``stream_async()``. Its result is
    the receipt's message. If the transport raises, the result says that the request was not sent,
    and the exception is logged.

    Parameters
    ----------
    agent
        The agent that calls the tool. The report's transcript comes from its turns.
    transport
        Where reports go. Defaults to a new `MockFeedbackTransport`.
    requested_by
        The visitor's username or GUID. When it is None, each call records the visitor of the
        current A2A request, read through `current_a2a_request`, or None outside an A2A turn.

    Returns
    -------
    chatlas.Tool
        The tool, named ``send_curation_feedback``. It takes ``question`` and ``reason``.
    """
    sender: FeedbackTransport = MockFeedbackTransport() if transport is None else transport

    def send_curation_feedback(question: str, reason: str) -> str:
        visitor = requested_by if requested_by is not None else _current_visitor()
        report = _build_report(agent, _truncate(question), _truncate(reason), visitor)
        try:
            receipt = sender.send(report)
        except Exception:
            logger.exception("The feedback request could not be sent.")
            return _NOT_SENT_TEXT
        return receipt.message

    return chatlas.Tool(
        func=send_curation_feedback,
        name=TOOL_NAME,
        description=TOOL_DESCRIPTION,
        parameters=_parameters(),
    )


def attach_feedback_tool(
    agent: _Agent,
    transport: FeedbackTransport | None = None,
    *,
    requested_by: str | None = None,
) -> chatlas.Tool:
    """Build a feedback tool with `feedback_tool` and register it on the agent.

    Returns
    -------
    chatlas.Tool
        The registered tool.
    """
    tool = feedback_tool(agent, transport, requested_by=requested_by)
    agent.register_tool(tool)
    return tool


def _build_report(
    agent: _Agent,
    question: str,
    reason: str,
    requested_by: str | None,
) -> FeedbackReport:
    """Build a report from the agent's current conversation."""
    return FeedbackReport(
        question=question,
        reason=reason,
        requested_by=requested_by,
        content_guid=os.environ.get("CONNECT_CONTENT_GUID") or None,
        transcript=_transcript(agent.get_turns()),
        created_at=datetime.now(timezone.utc).isoformat(),
    )


def _current_visitor() -> str | None:
    request = current_a2a_request()
    return None if request is None else request.visitor_guid


def _transcript(turns: Any) -> list[dict[str, str]]:
    """Return the most recent user and assistant turns that contain text.

    Turns with other roles, and turns without text, are skipped. The result keeps at most
    `MAX_TRANSCRIPT_TURNS` entries, and each text is at most `MAX_TURN_CHARACTERS` characters.
    """
    entries: list[dict[str, str]] = []
    for turn in turns:
        text = turn.text.strip()
        if turn.role not in _TRANSCRIPT_ROLES or not text:
            continue
        entries.append({"role": turn.role, "text": _truncate(text)})
    return entries[-MAX_TRANSCRIPT_TURNS:]


def _truncate(text: str) -> str:
    if len(text) <= MAX_TURN_CHARACTERS:
        return text
    return text[: MAX_TURN_CHARACTERS - 3] + "..."


def _log_safe(text: str) -> str:
    """Return ``text`` with control characters written as escapes, so a log line stays one line."""
    return _CONTROL_CHARACTERS.sub(lambda match: f"\\x{ord(match.group()):02x}", text)


def _parameters() -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that you could not answer.",
            },
            "reason": {
                "type": "string",
                "description": "Why you could not answer the question.",
            },
        },
        "required": ["question", "reason"],
        "additionalProperties": False,
    }
