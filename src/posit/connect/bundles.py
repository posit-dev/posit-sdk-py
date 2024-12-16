"""Bundle resources."""

from __future__ import annotations

import io

from typing_extensions import TYPE_CHECKING, List

from . import resources, tasks

if TYPE_CHECKING:
    from .context import Context


class BundleMetadata(resources.BaseResource):
    pass


class Bundle(resources.BaseResource):
    @property
    def metadata(self) -> BundleMetadata:
        return BundleMetadata(self._ctx, **self.get("metadata", {}))

    def delete(self) -> None:
        """Delete the bundle."""
        path = f"v1/content/{self['content_guid']}/bundles/{self['id']}"
        self._ctx.client.delete(path)

    def deploy(self) -> tasks.Task:
        """Deploy the bundle.

        Spawns an asynchronous task, which activates the bundle.

        Returns
        -------
        tasks.Task
            The task for the deployment.

        Examples
        --------
        >>> task = bundle.deploy()
        >>> task.wait_for()
        None
        """
        path = f"v1/content/{self['content_guid']}/deploy"
        response = self._ctx.client.post(path, json={"bundle_id": self["id"]})
        result = response.json()
        ts = tasks.Tasks(self._ctx)
        return ts.get(result["task_id"])

    def download(self, output: io.BufferedWriter | str) -> None:
        """Download a bundle.

        Download a bundle to a file or memory.

        Parameters
        ----------
        output : io.BufferedWriter or str
            An io.BufferedWriter instance or a str representing a relative or absolute path.

        Raises
        ------
        TypeError
            If the output is not of type `io.BufferedWriter` or `str`.

        Examples
        --------
        Write to a file.
        >>> bundle.download("bundle.tar.gz")
        None

        Write to an io.BufferedWriter.
        >>> with open('bundle.tar.gz', 'wb') as file:
        >>>     bundle.download(file)
        None
        """
        if not isinstance(output, (io.BufferedWriter, str)):
            raise TypeError(
                f"download() expected argument type 'io.BufferedWriter` or 'str', but got '{type(output).__name__}'",
            )

        path = f"v1/content/{self['content_guid']}/bundles/{self['id']}/download"
        response = self._ctx.client.get(path, stream=True)
        if isinstance(output, io.BufferedWriter):
            for chunk in response.iter_content():
                output.write(chunk)
        elif isinstance(output, str):
            with open(output, "wb") as file:
                for chunk in response.iter_content():
                    file.write(chunk)


class Bundles(resources.Resources):
    """Bundles resource.

    Parameters
    ----------
    config : config.Config
        Configuration object.
    session : requests.Session
        HTTP session object.
    content_guid : str
        Content GUID associated with the bundles.

    Attributes
    ----------
    content_guid: str
        Content GUID associated with the bundles.
    """

    def __init__(
        self,
        ctx: Context,
        content_guid: str,
    ) -> None:
        super().__init__(ctx)
        self.content_guid = content_guid

    def create(self, archive: io.BufferedReader | bytes | str) -> Bundle:
        """
        Create a bundle.

        Create a bundle from a file or memory.

        Parameters
        ----------
        archive : io.BufferedReader, bytes, or str
            Archive for bundle creation. A 'str' type assumes a relative or absolute filepath.

        Returns
        -------
        Bundle
            The created bundle.

        Raises
        ------
        TypeError
            If the input is not of type `io.BufferedReader`, `bytes`, or `str`.

        Examples
        --------
        Create a bundle from io.BufferedReader
        >>> with open('bundle.tar.gz', 'rb') as file:
        >>>     bundle.create(file)
        None

        Create a bundle from bytes.
        >>> with open('bundle.tar.gz', 'rb') as file:
        >>>     data: bytes = file.read()
        >>>     bundle.create(data)
        None

        Create a bundle from pathname.
        >>> bundle.create("bundle.tar.gz")
        None
        """
        if isinstance(archive, (io.BufferedReader, bytes)):
            data = archive
        elif isinstance(archive, str):
            with open(archive, "rb") as file:
                data = file.read()
        else:
            raise TypeError(
                f"create() expected argument type 'io.BufferedReader', 'bytes', or 'str', but got '{type(archive).__name__}'",
            )

        path = f"v1/content/{self.content_guid}/bundles"
        response = self._ctx.client.post(path, data=data)
        result = response.json()
        return Bundle(self._ctx, **result)

    def find(self) -> List[Bundle]:
        """Find all bundles.

        Returns
        -------
        list of Bundle
            List of all found bundles.
        """
        path = f"v1/content/{self.content_guid}/bundles"
        response = self._ctx.client.get(path)
        results = response.json()
        return [Bundle(self._ctx, **result) for result in results]

    def find_one(self) -> Bundle | None:
        """Find a bundle.

        Returns
        -------
        Bundle | None
            The first found bundle | None if no bundles are found.
        """
        bundles = self.find()
        return next(iter(bundles), None)

    def get(self, uid: str) -> Bundle:
        """Get a bundle.

        Parameters
        ----------
        uid : str
            Identifier of the bundle to retrieve.

        Returns
        -------
        Bundle
            The bundle with the specified ID.
        """
        path = f"v1/content/{self.content_guid}/bundles/{uid}"
        response = self._ctx.client.get(path)
        result = response.json()
        return Bundle(self._ctx, **result)
