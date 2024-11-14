"""Bundle resources."""

from __future__ import annotations

import io
from typing import List

from posit.connect._types_context import ContextP

from ._active import ActiveDict, ReadOnlyDict
from ._api_call import ApiCallMixin, get_api_stream, post_api
from ._types_content_item import ContentItemContext
from .tasks import Task, Tasks


class BundleMetadata(ReadOnlyDict):
    pass


class BundleContext(ContentItemContext):
    bundle_id: str

    def __init__(
        self,
        ctx: ContentItemContext,
        /,
        *,
        bundle_id: str,
    ) -> None:
        super().__init__(ctx, content_guid=ctx.content_guid)
        self.bundle_id = bundle_id


class Bundle(ActiveDict[BundleContext]):
    def __init__(self, ctx: ContentItemContext, /, **kwargs) -> None:
        bundle_id = kwargs.get("id")
        assert isinstance(bundle_id, str), f"Bundle 'id' must be a string. Got: {id}"
        assert bundle_id, "Bundle 'id' must not be an empty string."

        bundle_ctx = BundleContext(ctx, bundle_id=bundle_id)
        path = f"v1/content/{ctx.content_guid}/bundles/{bundle_id}"
        get_data = len(kwargs) == 1  # `id` is required
        super().__init__(bundle_ctx, path, get_data, **kwargs)

    @property
    def metadata(self) -> BundleMetadata:
        return BundleMetadata(**self.get("metadata", {}))

    def delete(self) -> None:
        """Delete the bundle."""
        self._delete_api()

    def deploy(self) -> Task:
        """Deploy the bundle.

        Spawns an asynchronous task, which activates the bundle.

        Returns
        -------
        Task
            The task for the deployment.

        Examples
        --------
        >>> task = bundle.deploy()
        >>> task.wait_for()
        """
        result = post_api(
            self._ctx,
            self._ctx.content_path,
            "deploy",
            json={"bundle_id": self["id"]},
        )
        assert isinstance(result, dict), f"Deploy response must be a dict. Got: {result}"
        assert "task_id" in result, f"Task ID not found in response: {result}"
        ts = Tasks(self._ctx)
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

        response = get_api_stream(
            self._ctx, self._ctx.content_path, "bundles", self._ctx.bundle_id, "download"
        )
        if isinstance(output, io.BufferedWriter):
            for chunk in response.iter_content():
                output.write(chunk)
        elif isinstance(output, str):
            with open(output, "wb") as file:
                for chunk in response.iter_content():
                    file.write(chunk)


class Bundles(ApiCallMixin, ContextP[ContentItemContext]):
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
        ctx: ContentItemContext,
    ) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = f"v1/content/{ctx.content_guid}/bundles"

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

        result = self._post_api(data=data)
        assert result is not None, "Bundle creation failed"

        return Bundle(self._ctx, **result)

    def find(self) -> List[Bundle]:
        """Find all bundles.

        Returns
        -------
        list of Bundle
            List of all found bundles.
        """
        results = self._get_api()
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
        result = self._get_api(uid)
        return Bundle(self._ctx, **result)
