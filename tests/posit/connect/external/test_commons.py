from __future__ import annotations

import logging
import re
import subprocess
import sys
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import chatlas
import pytest
from typing_extensions import Any

from posit.connect.external import commons
from posit.connect.external._a2a_request import A2ARequest, _request_scope

ROOT = Path(__file__).resolve().parents[4]
LOGGER_NAME = "posit.connect.external.commons"
NOT_SENT_TEXT = (
    "The feedback request was not sent because of a server error. Tell the asker that the "
    "request failed and that they can try again later."
)
DEMO_MESSAGE = (
    r"Feedback recorded as ([0-9a-f-]{36}) "
    r"\(demo transport: logged on the server only, not delivered to a curator\)\."
)


class RecordingAgent:
    """Stands in for a Commons agent. It holds fixed turns and records each tool it registers."""

    def __init__(self, turns: list[Any] | None = None) -> None:
        self.turns = list(turns or [])
        self.tools: list[Any] = []

    def get_turns(self) -> list[Any]:
        return list(self.turns)

    def register_tool(self, tool: Any) -> None:
        self.tools.append(tool)


class FixedTransport:
    """Returns a fixed receipt and records each report."""

    def __init__(self, receipt: commons.FeedbackReceipt) -> None:
        self.receipt = receipt
        self.reports: list[commons.FeedbackReport] = []

    def send(self, report: commons.FeedbackReport) -> commons.FeedbackReceipt:
        self.reports.append(report)
        return self.receipt


class FailingTransport:
    """Raises on every send, as a network transport does when the server is unreachable."""

    def send(self, report: commons.FeedbackReport) -> commons.FeedbackReceipt:
        raise RuntimeError("socket down")


def _user(text: str) -> Any:
    return chatlas.UserTurn(text)


def _assistant(text: str) -> Any:
    return chatlas.AssistantTurn(text)


def _receipt(message: str = "Recorded.") -> commons.FeedbackReceipt:
    return commons.FeedbackReceipt(id="rec-1", status="queued", message=message)


def _turn_request(visitor_guid: str) -> A2ARequest:
    return A2ARequest(
        context_id="ctx",
        user_session_token=None,
        visitor_guid=visitor_guid,
        headers={},
    )


def test_tool_has_name_and_json_schema():
    tool = commons.feedback_tool(RecordingAgent(), commons.MockFeedbackTransport())

    assert tool.name == "send_curation_feedback"
    schema: Any = tool.schema
    parameters = schema["function"]["parameters"]
    assert parameters["required"] == ["question", "reason"]
    assert set(parameters["properties"]) == {"question", "reason"}
    assert parameters["additionalProperties"] is False


def test_call_sends_report_with_all_fields(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("CONNECT_CONTENT_GUID", "guid-1")
    agent = RecordingAgent([_user("Why is revenue down?"), _assistant("I cannot tell.")])
    transport = FixedTransport(_receipt())
    tool = commons.feedback_tool(agent, transport, requested_by="alice")

    tool.func(question="Why is revenue down?", reason="No source covers it.")

    (report,) = transport.reports
    assert report.question == "Why is revenue down?"
    assert report.reason == "No source covers it."
    assert report.requested_by == "alice"
    assert report.content_guid == "guid-1"
    assert report.transcript == [
        {"role": "user", "text": "Why is revenue down?"},
        {"role": "assistant", "text": "I cannot tell."},
    ]


def test_created_at_is_iso_8601_in_utc():
    transport = FixedTransport(_receipt())
    commons.feedback_tool(RecordingAgent(), transport).func(question="q", reason="r")

    created_at = datetime.fromisoformat(transport.reports[0].created_at)
    assert created_at.utcoffset() == timedelta(0)


@pytest.mark.parametrize("value", [None, ""], ids=["unset", "empty"])
def test_content_guid_is_none_when_unset_or_empty(monkeypatch: pytest.MonkeyPatch, value: Any):
    if value is None:
        monkeypatch.delenv("CONNECT_CONTENT_GUID", raising=False)
    else:
        monkeypatch.setenv("CONNECT_CONTENT_GUID", value)
    transport = FixedTransport(_receipt())

    commons.feedback_tool(RecordingAgent(), transport).func(question="q", reason="r")

    assert transport.reports[0].content_guid is None


def test_requested_by_defaults_to_none_outside_an_a2a_turn():
    transport = FixedTransport(_receipt())

    commons.feedback_tool(RecordingAgent(), transport).func(question="q", reason="r")

    assert transport.reports[0].requested_by is None


def test_requested_by_defaults_to_the_visitor_of_the_current_turn():
    transport = FixedTransport(_receipt())
    tool = commons.feedback_tool(RecordingAgent(), transport)

    with _request_scope(_turn_request("user-9")):
        tool.func(question="q", reason="r")

    assert transport.reports[0].requested_by == "user-9"


def test_explicit_requested_by_overrides_the_current_turn_visitor():
    transport = FixedTransport(_receipt())
    tool = commons.feedback_tool(RecordingAgent(), transport, requested_by="alice")

    with _request_scope(_turn_request("user-9")):
        tool.func(question="q", reason="r")

    assert transport.reports[0].requested_by == "alice"


def test_tool_result_is_the_receipt_message():
    transport = FixedTransport(_receipt(message="Recorded as rec-42."))
    tool = commons.feedback_tool(RecordingAgent(), transport)

    assert tool.func(question="q", reason="r") == "Recorded as rec-42."


def test_default_transport_result_says_the_demo_transport_did_not_deliver():
    tool = commons.feedback_tool(RecordingAgent())

    func: Any = tool.func
    result = func(question="q", reason="r")

    match = re.fullmatch(DEMO_MESSAGE, result)
    assert match is not None
    assert uuid.UUID(match.group(1)).version == 4


def test_transport_failure_returns_fixed_text_and_logs_the_exception(
    caplog: pytest.LogCaptureFixture,
):
    tool = commons.feedback_tool(RecordingAgent(), FailingTransport())

    with caplog.at_level(logging.ERROR, logger=LOGGER_NAME):
        result = tool.func(question="q", reason="r")

    assert result == NOT_SENT_TEXT
    (record,) = [record for record in caplog.records if record.name == LOGGER_NAME]
    assert record.exc_info is not None


def test_question_and_reason_are_capped_at_the_turn_limit():
    transport = FixedTransport(_receipt())

    commons.feedback_tool(RecordingAgent(), transport).func(question="q" * 2500, reason="r" * 2500)

    report = transport.reports[0]
    assert len(report.question) == 2000
    assert report.question.endswith("...")
    assert len(report.reason) == 2000
    assert report.reason.endswith("...")


def test_mock_transport_returns_queued_receipt_with_demo_message():
    transport = commons.MockFeedbackTransport()
    report = commons.FeedbackReport(
        question="q",
        reason="r",
        requested_by=None,
        content_guid=None,
        transcript=[],
        created_at="2026-01-01T00:00:00+00:00",
    )

    first = transport.send(report)
    second = transport.send(report)

    assert first.status == "queued"
    assert uuid.UUID(first.id).version == 4
    assert first.id != second.id
    assert first.message == (
        f"Feedback recorded as {first.id} (demo transport: logged on the server only, "
        "not delivered to a curator)."
    )


def test_mock_transport_records_reports_and_logs_the_question(caplog: pytest.LogCaptureFixture):
    transport = commons.MockFeedbackTransport()
    report = commons.FeedbackReport(
        question="Which region leads sales?",
        reason="No source covers it.",
        requested_by=None,
        content_guid=None,
        transcript=[],
        created_at="2026-01-01T00:00:00+00:00",
    )

    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        receipt = transport.send(report)

    assert list(transport.reports) == [report]
    assert receipt.id in caplog.text
    assert "Which region leads sales?" in caplog.text


def test_mock_transport_keeps_only_the_latest_hundred_reports():
    transport = commons.MockFeedbackTransport()

    for index in range(101):
        transport.send(
            commons.FeedbackReport(
                question=f"question {index}",
                reason="r",
                requested_by=None,
                content_guid=None,
                transcript=[],
                created_at="2026-01-01T00:00:00+00:00",
            )
        )

    assert len(transport.reports) == 100
    assert transport.reports[0].question == "question 1"
    assert transport.reports[-1].question == "question 100"


def test_log_lines_escape_control_characters(caplog: pytest.LogCaptureFixture):
    transport = commons.MockFeedbackTransport()
    report = commons.FeedbackReport(
        question="line one\nline two\x00",
        reason="r",
        requested_by=None,
        content_guid=None,
        transcript=[],
        created_at="2026-01-01T00:00:00+00:00",
    )

    with caplog.at_level(logging.INFO, logger=LOGGER_NAME):
        transport.send(report)

    assert "line one\\x0aline two\\x00" in caplog.text
    assert "line one\nline two" not in caplog.text


def test_transcript_keeps_last_twenty_turns():
    turns = [_user(f"t{index}") for index in range(25)]

    entries = commons._transcript(turns)

    assert [entry["text"] for entry in entries] == [f"t{index}" for index in range(5, 25)]


def test_transcript_drops_turns_before_applying_the_limit():
    turns = [_user(f"t{index}") for index in range(21)]
    turns.append(chatlas.SystemTurn("system prompt"))

    entries = commons._transcript(turns)

    assert [entry["text"] for entry in entries] == [f"t{index}" for index in range(1, 21)]


def test_transcript_skips_other_roles_and_empty_text_and_strips_whitespace():
    turns = [
        chatlas.SystemTurn("system prompt"),
        chatlas.AssistantTurn([]),
        _user("  question  "),
        _assistant("answer"),
    ]

    assert commons._transcript(turns) == [
        {"role": "user", "text": "question"},
        {"role": "assistant", "text": "answer"},
    ]


def test_transcript_text_at_limit_is_kept_whole():
    text = "x" * 2000

    assert commons._transcript([_user(text)]) == [{"role": "user", "text": text}]


def test_transcript_text_over_limit_is_truncated_to_limit():
    entries = commons._transcript([_user("y" * 2001)])

    (entry,) = entries
    assert len(entry["text"]) == 2000
    assert entry["text"] == "y" * 1997 + "..."


def test_attach_registers_the_tool_and_returns_it():
    agent = RecordingAgent()

    tool = commons.attach_feedback_tool(agent, FixedTransport(_receipt()), requested_by="bob")

    assert agent.tools == [tool]
    assert tool.name == "send_curation_feedback"


def test_tool_registers_on_a_real_chatlas_chat():
    chat: Any = chatlas.ChatOpenAI(api_key="test-key", model="gpt-4o")

    tool = commons.attach_feedback_tool(chat, commons.MockFeedbackTransport())

    assert [registered.name for registered in chat.get_tools()] == [tool.name]


def test_import_without_chatlas_raises_guard_message():
    code = "import sys; sys.modules['chatlas'] = None; import posit.connect.external.commons"

    result = subprocess.run(
        [sys.executable, "-c", code],
        capture_output=True,
        text=True,
        cwd=ROOT,
        check=False,
    )

    assert result.returncode != 0
    assert (
        "ImportError: The 'chatlas' package is required to use this module. "
        "Install it with: pip install 'posit-sdk[commons]'"
    ) in result.stderr
