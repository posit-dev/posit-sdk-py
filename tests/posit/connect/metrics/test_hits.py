"""Tests for the hits metrics module."""

import pytest
import responses
from responses import matchers

from posit import connect

from ..api import load_mock


class TestHitsFetch:
    @responses.activate
    def test_fetch(self):
        # Set up mock response
        mock_get = responses.get(
            "https://connect.example/__api__/v1/instrumentation/content/hits",
            json=load_mock("v1/instrumentation/content/hits.json"),
        )

        # Create client with required version for hits API
        c = connect.Client("https://connect.example", "12345")
        c._ctx.version = "2025.04.0"

        # Fetch hits
        hits = list(c.metrics.hits.fetch())

        # Verify request was made
        assert mock_get.call_count == 1

        # Verify results
        assert len(hits) == 2
        assert hits[0]["id"] == 1001
        assert hits[0]["content_guid"] == "bd1d2285-6c80-49af-8a83-a200effe3cb3"
        assert hits[0]["timestamp"] == "2025-05-01T10:00:00-05:00"
        assert hits[0]["data"]["path"] == "/dashboard"

    @responses.activate
    def test_fetch_with_params(self):
        # Set up mock response
        mock_get = responses.get(
            "https://connect.example/__api__/v1/instrumentation/content/hits",
            json=load_mock("v1/instrumentation/content/hits.json"),
            match=[
                matchers.query_param_matcher(
                    {
                        "from": "2025-05-01T00:00:00Z",
                        "to": "2025-05-02T00:00:00Z",
                    }
                ),
            ],
        )

        # Create client with required version for hits API
        c = connect.Client("https://connect.example", "12345")
        c._ctx.version = "2025.04.0"

        # Fetch hits with parameters
        hits = list(
            c.metrics.hits.fetch(**{"from": "2025-05-01T00:00:00Z", "to": "2025-05-02T00:00:00Z"})
        )

        # Verify request was made with proper parameters
        assert mock_get.call_count == 1

        # Verify results
        assert len(hits) == 2


class TestHitsFindBy:
    @responses.activate
    def test_find_by(self):
        # Set up mock response
        mock_get = responses.get(
            "https://connect.example/__api__/v1/instrumentation/content/hits",
            json=load_mock("v1/instrumentation/content/hits.json"),
        )

        # Create client with required version for hits API
        c = connect.Client("https://connect.example", "12345")
        c._ctx.version = "2025.04.0"

        # Find hits by content_guid
        hit = c.metrics.hits.find_by(content_guid="bd1d2285-6c80-49af-8a83-a200effe3cb3")

        # Verify request was made
        assert mock_get.call_count == 1

        # Verify results
        assert hit is not None
        assert hit["id"] == 1001
        assert hit["content_guid"] == "bd1d2285-6c80-49af-8a83-a200effe3cb3"

    @responses.activate
    def test_find_by_not_found(self):
        # Set up mock response
        mock_get = responses.get(
            "https://connect.example/__api__/v1/instrumentation/content/hits",
            json=load_mock("v1/instrumentation/content/hits.json"),
        )

        # Create client with required version for hits API
        c = connect.Client("https://connect.example", "12345")
        c._ctx.version = "2025.04.0"

        # Try to find hit with non-existent content_guid
        hit = c.metrics.hits.find_by(content_guid="non-existent-guid")

        # Verify request was made
        assert mock_get.call_count == 1

        # Verify no result was found
        assert hit is None


class TestHitsVersionRequirement:
    @responses.activate
    def test_version_requirement(self):
        # Create client with version that's too old
        c = connect.Client("https://connect.example", "12345")
        c._ctx.version = "2024.04.0"

        with pytest.raises(RuntimeError):
            h = c.metrics.hits
