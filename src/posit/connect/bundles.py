from __future__ import annotations

from typing import List

from requests.sessions import Session as Session

from posit.connect.config import Config

from . import urls

from .resources import Resources, Resource


class BundleMetadata(Resource):
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


class Bundle(Resource):
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
        return BundleMetadata(self.config, self.session, **self.get("metadata", {}))

    # Accessor Methods

    def delete(self) -> None:
        path = f"v1/content/{self.content_guid}/bundles/{self.id}"
        url = urls.append_path(self.config.url, path)
        self.session.delete(url)


class Bundles(Resources):
    def __init__(self, config: Config, session: Session, content_guid: str) -> None:
        super().__init__(config, session)
        self.content_guid = content_guid

    def find(self) -> List[Bundle]:
        path = f"v1/content/{self.content_guid}/bundles"
        url = urls.append_path(self.config.url, path)
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
        url = urls.append_path(self.config.url, path)
        response = self.session.get(url)
        result = response.json()
        return Bundle(self.config, self.session, **result)
