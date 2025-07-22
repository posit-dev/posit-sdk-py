"""Task resources."""

from __future__ import annotations

from typing_extensions import overload

from . import resources


class Task(resources.BaseResource):
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
    def update(self, *args, first: int, wait: int, **kwargs) -> None:
        """Update the task.

        Parameters
        ----------
        first : int, default 0
            Line to start output on.
        wait : int, default 0
            Maximum number of seconds to wait for the task to complete.
        """

    @overload
    def update(self, *args, **kwargs) -> None:
        """Update the task."""

    def update(self, *args, **kwargs) -> None:
        """Update the task.

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
        >>> task.update()
        >>> task.output
        [
            "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.",
            "Pretium aenean pharetra magna ac placerat vestibulum lectus mauris."
        ]
        """
        params = dict(*args, **kwargs)
        path = f"v1/tasks/{self['id']}"
        response = self._ctx.client.get(path, params=params)
        result = response.json()
        super().update(**result)

    def wait_for(self, *, wait: int = 1, max_attempts: int | None = None) -> None:
        """Wait for the task to finish.

        Parameters
        ----------
        wait : int, default 1
            Maximum wait time in seconds between polling requests.
        max_attempts : int | None, default None
            Maximum number of polling attempts. If None, polling will continue indefinitely.

        Raises
        ------
        TimeoutError
            If the task does not finish within the maximum attempts.

        Notes
        -----
        If the task finishes before the wait time or maximum attempts are reached, the function will return immediately. For example, if the wait time is set to 5 seconds and the task finishes in 2 seconds, the function will return after 2 seconds.

        If the task does not finished after the maximum attempts, a TimeoutError will be raised. By default, the maximum attempts is None, which means the function will wait indefinitely until the task finishes.

        Examples
        --------
        >>> task.wait_for()
        None

        Waiting for a task to finish with a custom wait time.

        >>> task.wait_for(wait=5)
        None

        Waiting for a task with a maximum number of attempts.

        >>> task.wait_for(max_attempts=3)
        None
        """
        attempts = 0
        while not self.is_finished:
            if max_attempts is not None and attempts >= max_attempts:
                break
            self.update(wait=wait)
            attempts += 1

        if not self.is_finished:
            raise TimeoutError(
                f"Task {self['id']} did not finish within the specified wait time or maximum attempts."
            )


class Tasks(resources.Resources):
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
        path = f"v1/tasks/{uid}"
        response = self._ctx.client.get(path, params=kwargs)
        result = response.json()
        return Task(self._ctx, **result)
