"""Bundle resources."""

from __future__ import annotations

import io
import requests
from typing import List
from . import config, resources, tasks, urls


class BundleMetadata(resources.Resource):
    """Bundle metadata resource.

    Attributes
    ----------
    source : str | None
        Source of the bundle.
    source_repo : str | None
        Source repository of the bundle.
    source_branch : str | None
        Source branch of the bundle.
    source_commit : str | None
        Source commit of the bundle.
    archive_md5 : str | None
        MD5 checksum of the bundle archive.
    archive_sha1 : str | None
        SHA-1 checksum of the bundle archive.
    """

    @property
    def source(self) -> str | None:
        return self.get("source")

    @property
    def source_repo(self) -> str | None:
        return self.get("source_repo")

    @property
    def source_branch(self) -> str | None:
        return self.get("source_branch")

    @property
    def source_commit(self) -> str | None:
        return self.get("source_commit")

    @property
    def archive_md5(self) -> str | None:
        return self.get("archive_md5")

    @property
    def archive_sha1(self) -> str | None:
        return self.get("archive_sha1")


class Bundle(resources.Resource):
    """Bundle resource.

    Attributes
    ----------
    id : str
        Identifier of the bundle.
    content_guid : str
        Content GUID of the bundle.
    created_time : str
        Creation time of the bundle.
    cluster_name : str | None
        Cluster name associated with the bundle.
    image_name : str | None
        Image name of the bundle.
    r_version : str | None
        R version used in the bundle.
    r_environment_management : bool | None
        Indicates if R environment management is enabled.
    py_version : str | None
        Python version used in the bundle.
    py_environment_management : bool | None
        Indicates if Python environment management is enabled.
    quarto_version : str | None
        Quarto version used in the bundle.
    active : bool | None
        Indicates if the bundle is active.
    size : int | None
        Size of the bundle.
    metadata : BundleMetadata
        Metadata of the bundle.
    """

    @property
    def id(self) -> str:
        return self["id"]

    @property
    def content_guid(self) -> str:
        return self["content_guid"]

    @property
    def created_time(self) -> str:
        return self["created_time"]

    @property
    def cluster_name(self) -> str | None:
        return self.get("cluster_name")

    @property
    def image_name(self) -> str | None:
        return self.get("image_name")

    @property
    def r_version(self) -> str | None:
        return self.get("r_version")

    @property
    def r_environment_management(self) -> bool | None:
        return self.get("r_environment_management")

    @property
    def py_version(self) -> str | None:
        return self.get("py_version")

    @property
    def py_environment_management(self) -> bool | None:
        return self.get("py_environment_management")

    @property
    def quarto_version(self) -> str | None:
        return self.get("quarto_version")

    @property
    def active(self) -> bool | None:
        return self["active"]

    @property
    def size(self) -> int | None:
        return self["size"]

    @property
    def metadata(self) -> BundleMetadata:
        return BundleMetadata(
            self.config, self.session, **self.get("metadata", {})
        )

    def delete(self) -> None:
        """Delete the bundle."""
        path = f"v1/content/{self.content_guid}/bundles/{self.id}"
        url = urls.append(self.config.url, path)
        self.session.delete(url)

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
        path = f"v1/content/{self.content_guid}/deploy"
        url = urls.append(self.config.url, path)
        response = self.session.post(url, json={"bundle_id": self.id})
        result = response.json()
        ts = tasks.Tasks(self.config, self.session)
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
                f"download() expected argument type 'io.BufferedWriter` or 'str', but got '{type(output).__name__}'"
            )

        path = f"v1/content/{self.content_guid}/bundles/{self.id}/download"
        url = urls.append(self.config.url, path)
        response = self.session.get(url, stream=True)
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
        config: config.Config,
        session: requests.Session,
        content_guid: str,
    ) -> None:
        super().__init__(config, session)
        self.content_guid = content_guid

    def create(self, input: io.BufferedReader | bytes | str) -> Bundle:
        """
        Create a bundle.

        Create a bundle from a file or memory.

        Parameters
        ----------
        input : io.BufferedReader, bytes, or str
            Input archive for bundle creation. A 'str' type assumes a relative or absolute filepath.

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
        if isinstance(input, (io.BufferedReader, bytes)):
            data = input
        elif isinstance(input, str):
            with open(input, "rb") as file:
                data = file.read()
        else:
            raise TypeError(
                f"create() expected argument type 'io.BufferedReader', 'bytes', or 'str', but got '{type(input).__name__}'"
            )

        path = f"v1/content/{self.content_guid}/bundles"
        url = urls.append(self.config.url, path)
        response = self.session.post(url, data=data)
        result = response.json()
        return Bundle(self.config, self.session, **result)

    def find(self) -> List[Bundle]:
        """Find all bundles.

        Returns
        -------
        list of Bundle
            List of all found bundles.
        """
        path = f"v1/content/{self.content_guid}/bundles"
        url = urls.append(self.config.url, path)
        response = self.session.get(url)
        results = response.json()
        return [
            Bundle(self.config, self.session, **result) for result in results
        ]

    def find_one(self) -> Bundle | None:
        """Find a bundle.

        Returns
        -------
        Bundle | None
            The first found bundle | None if no bundles are found.
        """
        bundles = self.find()
        return next(iter(bundles), None)

    def get(self, id: str) -> Bundle:
        """Get a bundle.

        Parameters
        ----------
        id : str
            Identifier of the bundle to retrieve.

        Returns
        -------
        Bundle
            The bundle with the specified ID.
        """
        path = f"v1/content/{self.content_guid}/bundles/{id}"
        url = urls.append(self.config.url, path)
        response = self.session.get(url)
        result = response.json()
        return Bundle(self.config, self.session, **result)
