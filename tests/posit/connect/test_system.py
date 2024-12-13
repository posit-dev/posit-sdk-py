import responses

from posit.connect.client import Client
from posit.connect.system import SystemRuntimeCache
from posit.connect.tasks import Task

from .api import load_mock_dict


class TestSystemCacheRuntime:
    @responses.activate
    def test_runtime_caches(self):
        # behavior
        mock_get_runtimes = responses.get(
            "https://connect.example/__api__/v1/system/caches/runtime",
            json=load_mock_dict("v1/system/caches/runtime.json"),
        )
        mock_delete = responses.delete(
            "https://connect.example/__api__/v1/system/caches/runtime",
            json={"task_id": "12345"},
        )
        mock_task = responses.get(
            "https://connect.example/__api__/v1/tasks/12345",
            json={"task_id": "12345"},
        )

        # setup
        client = Client(api_key="12345", url="https://connect.example")

        # invoke
        runtimes = client.system.caches.runtime.find()

        for runtime in runtimes:
            assert isinstance(runtime, SystemRuntimeCache)
            task = runtime.destroy()
            assert isinstance(task, Task)

        first_runtime = runtimes[0]
        task = first_runtime.destroy()
        assert isinstance(task, Task)
        task = client.system.caches.runtime.destroy(
            language=first_runtime["language"],
            version=first_runtime["version"],
            image_name=first_runtime["image_name"],
        )
        assert isinstance(task, Task)

        # assert
        assert mock_get_runtimes.call_count == 1
        assert mock_delete.call_count == 3
        assert mock_task.call_count == len(runtimes) + 2
