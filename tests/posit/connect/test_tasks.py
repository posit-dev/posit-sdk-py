from unittest import mock

import responses
from responses import BaseResponse, matchers

from posit import connect
from posit.connect import tasks

from .api import load_mock_dict


class TestTaskAttributes:
    @classmethod
    def setup_class(cls):
        cls.task = tasks.Task(  # pyright: ignore[reportCallIssue]
            mock.Mock(),
            **load_mock_dict("v1/tasks/jXhOhdm5OOSkGhJw-finished.json"),  # pyright: ignore[reportArgumentType]
        )

    def test_id(self):
        assert self.task["id"] == "jXhOhdm5OOSkGhJw"

    def test_is_finished(self):
        assert self.task.is_finished

    def test_output(self):
        assert self.task["output"] == [
            "Building static content...",
            "Launching static content...",
        ]

    def test_error_code(self):
        assert self.task.error_code == 1

    def test_error_message(self):
        assert (
            self.task.error_message
            == "Unable to render: Rendering exited abnormally: exit status 1"
        )

    def test_result(self):
        assert self.task["result"] is None


class TestTaskUpdate:
    @responses.activate
    def test(self):
        uid = "jXhOhdm5OOSkGhJw"

        # behavior
        mock_tasks_get = [
            responses.get(
                f"https://connect.example/__api__/v1/tasks/{uid}",
                json=load_mock_dict(f"v1/tasks/{uid}-unfinished.json"),
            ),
            responses.get(
                f"https://connect.example/__api__/v1/tasks/{uid}",
                json=load_mock_dict(f"v1/tasks/{uid}-finished.json"),
            ),
        ]

        # setup
        c = connect.Client("https://connect.example", "12345")
        task = c.tasks.get(uid)
        assert not task.is_finished

        # invoke
        finished_task = task.update()

        # assert
        assert not task.is_finished
        assert finished_task.is_finished
        assert mock_tasks_get[0].call_count == 1
        assert mock_tasks_get[1].call_count == 1

    @responses.activate
    def test_with_params(self):
        uid = "jXhOhdm5OOSkGhJw"
        params = {"first": 10, "wait": 10}

        # behavior
        mock_tasks_get = [
            responses.get(
                f"https://connect.example/__api__/v1/tasks/{uid}",
                json=load_mock_dict(f"v1/tasks/{uid}-unfinished.json"),
            ),
            responses.get(
                f"https://connect.example/__api__/v1/tasks/{uid}",
                json=load_mock_dict(f"v1/tasks/{uid}-finished.json"),
                match=[matchers.query_param_matcher(params)],
            ),
        ]

        # setup
        c = connect.Client("https://connect.example", "12345")
        task = c.tasks.get(uid)
        assert not task.is_finished

        # invoke
        finished_task = task.update(**params)

        # assert
        assert not task.is_finished
        assert finished_task.is_finished
        assert mock_tasks_get[0].call_count == 1
        assert mock_tasks_get[1].call_count == 1


class TestTaskWaitFor:
    @responses.activate
    def test(self):
        uid = "jXhOhdm5OOSkGhJw"

        # behavior
        mock_tasks_get = [
            responses.get(
                f"https://connect.example/__api__/v1/tasks/{uid}",
                json=load_mock_dict(f"v1/tasks/{uid}-unfinished.json"),
            ),
            responses.get(
                f"https://connect.example/__api__/v1/tasks/{uid}",
                json=load_mock_dict(f"v1/tasks/{uid}-finished.json"),
            ),
        ]

        # setup
        c = connect.Client("https://connect.example", "12345")
        task = c.tasks.get(uid)
        assert not task.is_finished

        # invoke
        finished_task = task.wait_for()

        # assert
        assert finished_task.is_finished
        assert mock_tasks_get[0].call_count == 1
        assert mock_tasks_get[1].call_count == 1


class TestTasksGet:
    @responses.activate
    def test(self):
        uid = "jXhOhdm5OOSkGhJw"

        # behavior
        mock_tasks_get: BaseResponse = responses.get(
            f"https://connect.example/__api__/v1/tasks/{uid}",
            json=load_mock_dict(f"v1/tasks/{uid}-finished.json"),
        )

        # setup
        c = connect.Client("https://connect.example", "12345")

        # invoke
        task = c.tasks.get(uid)

        # assert
        assert task["id"] == uid
        assert mock_tasks_get.call_count == 1
