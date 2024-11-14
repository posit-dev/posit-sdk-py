"""Task resources."""

from __future__ import annotations

from typing import overload

from typing_extensions import TypedDict, Unpack

from ._active import ActiveDict
from ._types_context import ContextP
from .context import Context


class TaskContext(Context):
    task_id: str

    def __init__(self, ctx: Context, *, task_id: str) -> None:
        super().__init__(ctx.session, ctx.url)
        self.task_id = task_id


class Task(ActiveDict[TaskContext]):
    @classmethod
    def _api_path(cls, task_uid: str) -> str:
        return f"v1/tasks/{task_uid}"

    class _AttrResult(TypedDict):
        type: str
        data: object

    class _Attrs(TypedDict, total=False):
        id: str
        """The identifier for this task."""
        output: list[str]
        """An array containing lines of output produced by the task."""
        finished: bool
        """Indicates that a task has completed."""
        code: int
        """Numeric indication as to the cause of an error. Non-zero when an error has occured."""
        error: str
        """Description of the error. An empty string when no error has occurred."""
        last: int
        """
        The total number of output lines produced so far. Use as the value
        to `first` in the next request to only fetch output lines beyond
        what you have already received.
        """
        result: "Task._AttrResult"
        """A value representing the result of the operation, if any. For deployment tasks, this
        value is `null`."""

    @overload
    def __init__(self, ctx: Context, /, *, id: str) -> None:
        """Task resource.

        Since the task attributes are not supplied, the attributes will be retrieved from the API upon initialization.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        id : str
            The identifier for this task.
        """

    @overload
    def __init__(self, ctx: Context, /, **kwargs: Unpack[_Attrs]) -> None:
        """Task resource.

        Parameters
        ----------
        ctx : Context
            The context object containing the session and URL for API interactions.
        **kwargs : Task._Attrs
            Attributes for the task. If not supplied, the attributes will be retrieved from the API upon initialization.
        """

    def __init__(self, ctx: Context, /, **kwargs: Unpack[_Attrs]) -> None:
        task_id = kwargs.get("id")
        assert isinstance(task_id, str), "Task `id` must be a string."
        assert task_id, "Task `id` must not be empty."

        task_ctx = TaskContext(ctx, task_id=task_id)
        path = self._api_path(task_id)
        get_data = len(kwargs) == 1
        super().__init__(task_ctx, path, get_data, **kwargs)

    @property
    def is_finished(self) -> bool:
        """The task state.

        If True, the task has completed. The task may have exited successfully
        or have failed. Inspect the error_code to determine if the task finished
        successfully or not.

        Returns
        -------
        bool
        """
        return self.get("finished", False)

    @property
    def error_code(self) -> int | None:
        """The error code.

        The error code produced by the task. A non-zero value represent an
        error. A zero value represents no error.

        Returns
        -------
        int | None
            Non-zero value indicates an error.
        """
        return self["code"] if self.is_finished else None

    @property
    def error_message(self) -> str | None:
        """The error message.

        Returns
        -------
        str | None
            Human readable error message, or None on success or not finished.
        """
        return self.get("error") if self.is_finished else None

    # CRUD Methods

    @overload
    def update(self, /, *, first: int, wait: int, **kwargs) -> Task: ...

    @overload
    def update(self, /, **kwargs) -> Task: ...

    def update(self, /, **kwargs) -> Task:
        """Update the task.

        Parameters
        ----------
        first : int, default 0
            Line to start output on.
        wait : int, default 0
            Maximum number of seconds to wait for the task to complete.
        **kwargs
            Additional query parameters to pass to the API.

        See Also
        --------
        task.wait_for : Wait for the task to complete.

        Notes
        -----
        When waiting for a task to complete, one should consider utilizing `task.wait_for`.

        Examples
        --------
        >>> task.output
        [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
        ]
        >>> updated_task = task.update()
        >>> updated_task.output
        [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Pretium aenean pharetra magna ac placerat vestibulum lectus mauris."
        ]
        """
        result = self._get_api(params=kwargs)
        new_task = Task(
            self._ctx,
            **result,
        )
        return new_task

    def wait_for(self) -> Task:
        """Wait for the task to finish.

        Examples
        --------
        >>> task.wait_for()
        """
        cur_task = self

        while not cur_task.is_finished:
            cur_task = self.update()

        return cur_task


# No special class for Tasks, just a placeholder for the get method
class Tasks(ContextP[Context]):
    def __init__(self, ctx: Context) -> None:
        super().__init__()
        self._ctx = ctx

    @overload
    def get(self, *, uid: str, first: int, wait: int) -> Task:
        """Get a task.

        Parameters
        ----------
        uid : str
            Task identifier.
        first : int, default 0
            Line to start output on.
        wait : int, default 0
            Maximum number of seconds to wait for the task to complete.

        Returns
        -------
        Task
        """

    @overload
    def get(self, uid: str, **kwargs) -> Task:
        """Get a task.

        Parameters
        ----------
        uid : str
            Task identifier.

        Returns
        -------
        Task
        """

    def get(self, uid: str, **kwargs) -> Task:
        """Get a task.

        Parameters
        ----------
        uid : str
            Task identifier.

        Returns
        -------
        Task
        """
        # TODO-barret-future; Find better way to pass through query params to the API calls on init
        task = Task(
            self._ctx,
            id=uid,
            _placeholder=True,  # pyright: ignore[reportCallIssue]
        )
        ret_task = task.update(**kwargs)
        return ret_task
