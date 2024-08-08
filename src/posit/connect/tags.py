from typing import List, overload

from .resources import Resource, Resources


class Tag(Resource):
    @property
    def id(self):
        return self['id']

    def delete(self) -> None:
        url = self.url + f"/v1/tags/{self.id}"
        self.session.delete(url)

    def update(self, *args, **kwargs) -> None:
        url = self.url + f"/v1/tags/{self.id}"
        response = self.session.patch(url, json=kwargs)
        super().update(**response.json())


class Tags(Resources):
    @overload
    def create(self, *, name: str, parent_id: str = ...) -> Tag: ...

    @overload
    def create(self, **kwargs) -> Tag: ...

    def create(self, **kwargs) -> Tag:
        dict().update()
        url = self.url + "/v1/tags"
        response = self.session.post(url, json=kwargs)
        return Tag(self.params, **response.json())

    def find(self, **kwargs) -> List[Tag]:
        url = self.url + "/v1/tags"
        response = self.session.get(url, params=kwargs)
        return [Tag(self.params, **result) for result in response.json()]

    def find_one(self, **kwargs) -> Tag | None:
        url = self.url + "/v1/tags"
        response = self.session.get(url, params=kwargs)
        return next(
            (Tag(self.params, **result) for result in response.json()), None
        )

    def get(self, uid: str) -> Tag:
        url = self.url + f"/v1/tags/{uid}"
        response = self.session.get(url)
        return Tag(self.params, **response.json())
