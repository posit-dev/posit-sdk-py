"""Task resources."""

from __future__ import annotations

from typing import List, overload

from . import resources, urls


class Task(resources.Resource):
    @property
    def id(self) -> str:
        """The task identifier.

        Returns
        -------
        str
        """
        return self["id"]

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
    def output(self) -> List[str]:
        """Process output.

        The process output produced by the task.

        Returns
        -------
        List[str]
        """
        return self["output"]

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

    @property
    def result(self) -> dict | None:
        """The task result.

        Returns
        -------
        dict | None
        """
        return self.get("result")

    # CRUD Methods

    @overload
    def update(self, first: int, wait: int, **kwargs) -> None:
        """Update the task.

        Parameters
        ----------
        first : int, default 0
            Line to start output on.
        wait : int, default 0
            Maximum number of seconds to wait for the task to complete.
        """
        ...

    @overload
    def update(self, *args, **kwargs) -> None:
        """Update the task."""
        ...

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
        path = f"v1/tasks/{self.id}"
        url = urls.append(self.config.url, path)
        response = self.session.get(url, params=params)
        result = response.json()
        super().update(**result)

    def wait_for(self) -> None:
        """Wait for the task to finish.

        Examples
        --------
        >>> task.wait_for()
        None
        """
        while not self.is_finished:
            self.update()


class Tasks(resources.Resources):
    @overload
    def get(self, id: str, first: int, wait: int) -> Task:
        """Get a task.

        Parameters
        ----------
        id : str
            Task identifier.
        first : int, default 0
            Line to start output on.
        wait : int, default 0
            Maximum number of seconds to wait for the task to complete.

        Returns
        -------
        Task
        """
        ...

    @overload
    def get(self, id: str, *args, **kwargs) -> Task:
        """Get a task.

        Parameters
        ----------
        id : str
            Task identifier.

        Returns
        -------
        Task
        """
        ...

    def get(self, id: str, *args, **kwargs) -> Task:
        """Get a task.

        Parameters
        ----------
        id : str
            Task identifier.

        Returns
        -------
        Task
        """
        params = dict(*args, **kwargs)
        path = f"v1/tasks/{id}"
        url = urls.append(self.config.url, path)
        response = self.session.get(url, params=params)
        result = response.json()
        return Task(self.config, self.session, **result)
