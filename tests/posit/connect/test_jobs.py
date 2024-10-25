import pytest
import responses

from posit.connect.client import Client

from .api import load_mock  # type: ignore


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

        assert len(content.jobs) == 1


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
                "v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/tHawGvHZTosJA2Dx.json"
            ),
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        job = content.jobs.find("tHawGvHZTosJA2Dx")
        assert job["key"] == "tHawGvHZTosJA2Dx"

    @responses.activate
    def test_cached(self):
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

        assert content.jobs
        job = content.jobs.find("tHawGvHZTosJA2Dx")
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

        with pytest.raises(Exception):
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


class TestJobsReload:
    @responses.activate
    def test(self):
        responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066.json"),
        )

        mock_get = responses.get(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs",
            json=load_mock("v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs.json"),
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        assert len(content.jobs) == 1
        assert mock_get.call_count == 1

        content.jobs.reload()

        assert len(content.jobs) == 1
        assert mock_get.call_count == 2


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
                "v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/tHawGvHZTosJA2Dx.json"
            ),
        )

        responses.delete(
            "https://connect.example/__api__/v1/content/f2f37341-e21d-3d80-c698-a935ad614066/jobs/tHawGvHZTosJA2Dx",
        )

        c = Client("https://connect.example", "12345")
        content = c.content.get("f2f37341-e21d-3d80-c698-a935ad614066")

        job = content.jobs.find("tHawGvHZTosJA2Dx")
        job.destroy()