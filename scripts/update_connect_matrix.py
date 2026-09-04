"""Update the integration-test Connect versions from Posit's support page."""

from __future__ import annotations

import argparse
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.request import Request, urlopen

SUPPORTED_VERSIONS_URL = "https://docs.posit.co/supported-versions/connect.html"
_VERSION_PATTERN = re.compile(r"\b(20\d{2}\.\d{2}\.\d+)\b")
_TRAIN_PATTERN = re.compile(r"20\d{2}\.\d{2}")
_VERSIONS_START = "# Versions\nCONNECT_VERSIONS := \\\n"


def _clean_text(value: str) -> str:
    return " ".join(value.split())


class _TableParser(HTMLParser):
    """Collect rows and visible text from HTML tables."""

    def __init__(self) -> None:
        super().__init__()
        self.rows: list[list[str]] = []
        self.text: list[str] = []
        self._table_depth = 0
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_data(self, data: str) -> None:
        self.text.append(data)
        if self._cell is not None:
            self._cell.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag in {"td", "th"} and self._cell is not None and self._row is not None:
            self._row.append(_clean_text("".join(self._cell)))
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None
        elif tag == "table" and self._table_depth:
            self._table_depth -= 1

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        if tag == "table":
            self._table_depth += 1
        elif tag == "tr" and self._table_depth:
            self._row = []
        elif tag in {"td", "th"} and self._row is not None:
            self._cell = []


def _version_key(version: str) -> tuple[int, int, int]:
    year, month, patch = (int(part) for part in version.split("."))
    return year, month, patch


def supported_versions_from_html(html: str) -> list[str]:
    """Return the newest listed patch release for each supported train."""
    parser = _TableParser()
    parser.feed(html)

    header = ["Supported Version", "Supported Until"]
    try:
        header_index = next(
            index for index, row in enumerate(parser.rows) if row[: len(header)] == header
        )
    except StopIteration as error:
        raise ValueError("Could not find the supported versions table") from error

    supported_trains: list[str] = []
    for row in parser.rows[header_index + 1 :]:
        if not row or not _TRAIN_PATTERN.fullmatch(row[0]):
            continue
        if row[0] not in supported_trains:
            supported_trains.append(row[0])

    if not supported_trains:
        raise ValueError("The supported versions table contains no release trains")

    releases = set(_VERSION_PATTERN.findall("".join(parser.text)))
    latest_by_train: dict[str, str] = {}
    for release in releases:
        train = ".".join(release.split(".")[:2])
        if train not in supported_trains:
            continue
        current = latest_by_train.get(train)
        if current is None or _version_key(release) > _version_key(current):
            latest_by_train[train] = release

    missing = [train for train in supported_trains if train not in latest_by_train]
    if missing:
        missing_versions = ", ".join(missing)
        raise ValueError(f"No release was found for supported trains: {missing_versions}")

    return [latest_by_train[train] for train in supported_trains]


def update_makefile(makefile: Path, versions: list[str]) -> bool:
    """Replace the Connect version block and return whether it changed."""
    content = makefile.read_text()
    start = content.find(_VERSIONS_START)
    end = content.find("\n.PHONY:", start)
    if start == -1 or end == -1:
        raise ValueError(f"Could not find the Connect version block in {makefile}")

    continuation = " " + "\\"
    version_lines = [
        f"\t{version}{continuation if index < len(versions) - 1 else ''}\n"
        for index, version in enumerate(versions)
    ]
    replacement = _VERSIONS_START + "".join(version_lines)
    updated = content[:start] + replacement + content[end:]
    if updated == content:
        return False

    makefile.write_text(updated)
    return True


def _fetch(url: str) -> str:
    request = Request(url, headers={"User-Agent": "posit-sdk-py-connect-matrix"})
    with urlopen(request, timeout=30) as response:
        return response.read().decode()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=SUPPORTED_VERSIONS_URL)
    parser.add_argument(
        "--makefile",
        type=Path,
        default=Path("integration/Makefile"),
    )
    args = parser.parse_args()

    versions = supported_versions_from_html(_fetch(args.url))
    changed = update_makefile(args.makefile, versions)
    state = "updated" if changed else "already current"
    print(f"{state}: {', '.join(versions)}")


if __name__ == "__main__":
    main()
