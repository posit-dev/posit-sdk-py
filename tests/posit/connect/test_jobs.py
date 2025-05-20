import pytest
import responses
from requests.exceptions import HTTPError
from typing_extensions import TYPE_CHECKING

from posit.connect.client import Client

from .api import load_mock

if TYPE_CHECKING:
    from posit.connect.jobs import Job, Jobs


class TestJobsMixin:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs.json"),
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")
        jobs: Jobs = content.jobs
        assert len(jobs) == 1


class TestJobsFind:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/tHawGvHZTosJA2Dx",
            json=load_mock(
                "v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/tHawGvHZTosJA2Dx.json",
            ),
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        job: Job = content.jobs.find("tHawGvHZTosJA2Dx")
        assert job["key"] == "tHawGvHZTosJA2Dx"

    @responses.activate
    def test_miss(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/not-found",
            status=404,
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        with pytest.raises(HTTPError):
            content.jobs.find("not-found")


class TestJobsFindBy:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs.json"),
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        job = content.jobs.find_by(key="tHawGvHZTosJA2Dx")
        assert job
        assert job["key"] == "tHawGvHZTosJA2Dx"

    @responses.activate
    def test_with_content_id(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs.json"),
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        # Test with content_id (new field)
        job = content.jobs.find_by(content_id="54")
        assert job
        assert job["content_id"] == "54"
        assert job["app_id"] == "54"  # Should have both fields

        # Test with app_id (deprecated field)
        job = content.jobs.find_by(app_id="54")
        assert job
        assert job["app_id"] == "54"
        assert job["content_id"] == "54"  # Should have both fields


class TestJobDestory:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/tHawGvHZTosJA2Dx",
            json=load_mock(
                "v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/tHawGvHZTosJA2Dx.json",
            ),
        )

        responses.delete(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/tHawGvHZTosJA2Dx",
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        job = content.jobs.find("tHawGvHZTosJA2Dx")
        job.destroy()
