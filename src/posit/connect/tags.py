from typing import TYPE_CHECKING, List, overload

from .resources import Resource, ResourceParameters, Resources

if TYPE_CHECKING:
    from .content import Content


class Tag(Resource):
    def __init__(self, params: ResourceParameters, content_guid = None, **kwargs):
        super().__init__(params, **kwargs)
        self["content_guid"] = content_guid

    @property
    def id(self):
        return self["id"]

    @property
    def content_guid(self):
        return self["content_guid"]

    @property
    def name(self):
        return self["name"]

    @property
    def parent_id(self):
        return self["parent_id"]

    @property
    def content(self) -> "Content":
        from .content import Content

        return Content(self.params, tag_id=self.id)

    @property
    def parent(self) -> "Tag":
        return Tags(self.params).get(self.parent_id)

    @property
    def children(self) -> List["Tag"]:
        return Tags(self.params).find(parent_id=self.id)

    def create_child(self, **kwargs) -> "Tag":
        return Tags(self.params).create(parent_id=self.id, **kwargs)

    def delete(self) -> None:
        path = f"/v1/tags/{self.id}"
        if self.content_guid:
            path = f"v1/content/{self.content_guid}/tags/{self.id}"
        url = self.url + path
        self.session.delete(url)

    def update(self, *args, **kwargs) -> None:
        url = self.url + f"/v1/tags/{self.id}"
        response = self.session.patch(url, json=kwargs)
        super().update(**response.json())


class Tags(Resources):
    def __init__(
        self, params: ResourceParameters, *, content_guid=None
    ) -> None:
        super().__init__(params)
        self.content_guid = content_guid

    def count(self) -> int:
        return len(self.find())

    @overload
    def create(self, *, name: str, parent_id: str = ...) -> Tag: ...

    @overload
    def create(self, **kwargs) -> Tag: ...

    def create(self, **kwargs) -> Tag:
        path = "v1/tags"
        if self.content_guid:
            path = f"v1/content/{self.content_guid}/tags"
        url = self.url + path
        response = self.session.post(url, json=kwargs)
        return Tag(self.params, **response.json())

    def find(self, **kwargs) -> List[Tag]:
        path = "v1/tags"
        if self.content_guid:
            path = f"v1/content/{self.content_guid}/tags"
        url = self.url + path
        response = self.session.get(url, params=kwargs)
        return [
            Tag(self.params, content_guid=self.content_guid, **result)
            for result in response.json()
        ]

    def find_one(self, **kwargs) -> Tag | None:
        path = "v1/tags"
        if self.content_guid:
            path = f"v1/content/{self.content_guid}/tags"
        url = self.url + path
        response = self.session.get(url, params=kwargs)
        return next(
            (
                Tag(self.params, content_guid=self.content_guid, **result)
                for result in response.json()
            ),
            None,
        )

    def get(self, uid: str) -> Tag:
        url = self.url + f"/v1/tags/{uid}"
        response = self.session.get(url)
        return Tag(self.params, **response.json())
