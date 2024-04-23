from __future__ import annotations

from typing import BinaryIO, List

from requests.sessions import Session as Session


from . import config, resources, urls


class BundleMetadata(resources.Resource):
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

    # CRUD Methods

    def delete(self) -> None:
        path = f"v1/content/{self.content_guid}/bundles/{self.id}"
        url = urls.append(self.config.url, path)
        self.session.delete(url)

    def download(self) -> bytes:
        """Download a bundle.

        Returns
        -------
        bytes
            Archive contents in bytes representation.

        Examples
        --------
        >>> with open('archive.tar.gz', 'wb') as file:
        >>>     data = bundle.download()
        >>>     file.write(data)
        """
        path = f"v1/content/{self.content_guid}/bundles/{self.id}/download"
        url = urls.append(self.config.url, path)
        response = self.session.get(url, stream=True)
        return response.content


class Bundles(resources.Resources):
    def __init__(
        self, config: config.Config, session: Session, content_guid: str
    ) -> None:
        super().__init__(config, session)
        self.content_guid = content_guid

    def create(self, data: BinaryIO | bytes) -> Bundle:
        """Create a bundle.

        Create a bundle by upload via archive format.

        Parameters
        ----------
        data : BinaryIO | bytes
            Archive contents in BinaryIO or bytes representation.

        Returns
        -------
        Bundle

        Examples
        --------
        Create a bundle using a file object.

        >>> with open('bundle.tar.gz', 'rb') as file:
        >>>     bundle.create(file)

        Create a bundle using bytes.

        >>> with open('bundle.tar.gz', 'rb') as file:
        >>>     data = file.read()
        >>>     bundle.create(data)
        """
        path = f"v1/content/{self.content_guid}/bundles"
        url = urls.append(self.config.url, path)
        response = self.session.post(url, data=data)
        result = response.json()
        return Bundle(self.config, self.session, **result)

    def find(self) -> List[Bundle]:
        path = f"v1/content/{self.content_guid}/bundles"
        url = urls.append(self.config.url, path)
        response = self.session.get(url)
        results = response.json()
        return [
            Bundle(
                self.config,
                self.session,
                **result,
            )
            for result in results
        ]

    def find_one(self) -> Bundle | None:
        bundles = self.find()
        return next(iter(bundles), None)

    def get(self, id: str) -> Bundle:
        path = f"v1/content/{self.content_guid}/bundles/{id}"
        url = urls.append(self.config.url, path)
        response = self.session.get(url)
        result = response.json()
        return Bundle(self.config, self.session, **result)
