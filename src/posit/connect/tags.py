from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from typing_extensions import NotRequired, TypedDict, Unpack

from .context import Context, ContextManager
from .resources import Active, ResourceParameters

if TYPE_CHECKING:
    from .content import ContentItem


class Tag(Active):
    """Tag resource."""

    class _Attrs(TypedDict, total=False):
        id: str
        """The identifier for the tag."""
        name: str
        """The name of the tag."""
        parent_id: NotRequired[Optional[str]]
        """The identifier for the parent tag. If there is no parent_id, the tag is a top-level tag."""
        created_time: str
        """The timestamp (RFC3339) indicating when the tag was created. Ex. '2006-01-02T15:04:05Z'"""
        updated_time: str
        """The timestamp (RFC3339) indicating when the tag was created. Ex. '2006-01-02T15:04:05Z'"""

    def __init__(self, ctx: Context, path: str, /, **kwargs: Unpack[Tag._Attrs]):
        super().__init__(ctx, path, **kwargs)

    @property
    def parent_tag(self) -> Tag | None:
        if self.get("parent_id", None) is None:
            return None

        # TODO-barret-future: Replace with `self._ctx.client.tags.get(self["parent_id"])`
        path = "v1/tags/" + self["parent_id"]
        url = self._ctx.url + path
        response = self._ctx.session.get(url)
        return Tag(self._ctx, path, **response.json())

    @property
    def children_tags(self) -> ChildrenTags:
        """
        Find all child tags that are direct children of this tag.

        Returns
        -------
        ChildrenTags
            Helper class that can `.find()` the child tags.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client(...)

        mytag = client.tags.find(id="TAG_ID_HERE")
        children = mytag.children_tags().find()
        ```
        """
        return ChildrenTags(self._ctx, self._path, parent_tag=self)

    # TODO-barret-Q: Should this be `.descendant_tags` or `.descendants`?
    # TODO-barret-Q: Should this be `.find_descendants() -> list[Tag]`?
    @property
    def descendant_tags(self) -> DescendantTags:
        """
        Find all tags that descend from this tag.

        Returns
        -------
        DescendantTags
            Helper class that can `.find()` all descendant tags.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client(...)

        mytag = client.tags.find(id="TAG_ID_HERE")
        descendant_tags = mytag.descendant_tags().find()
        ```
        """
        return DescendantTags(self._ctx, parent_tag=self)

    @property
    def content_items(self) -> TagContentItems:
        """
        Find all content items using this tag.

        Returns
        -------
        TagContentItems
            Helper class that can `.find()` all content items.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client(...)
        first_tag = client.tags.find()[0]
        first_tag_content_items = first_tag.content_items.find()
        ```
        """
        path = self._path + "/content"
        return TagContentItems(self._ctx, path)

    def destroy(self) -> None:
        """
        Removes the tag.

        Deletes a tag, including all descendants in its own tag hierarchy.
        """
        url = self._ctx.url + self._path
        self._ctx.session.delete(url)


class TagContentItems(ContextManager):
    def __init__(self, ctx: Context, path: str) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = path

    def find(self) -> list[ContentItem]:
        """
        Find all content items that are tagged with this tag.

        Returns
        -------
        list[ContentItem]
            List of content items that are tagged with this tag.
        """
        from .content import ContentItem

        url = self._ctx.url + self._path
        response = self._ctx.session.get(url)
        results = response.json()
        params = ResourceParameters(self._ctx.session, self._ctx.url)
        print(results)
        return [ContentItem(params, **result) for result in results]


class ChildrenTags(ContextManager):
    def __init__(self, ctx: Context, path: str, /, *, parent_tag: Tag) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = path
        self._parent_tag = parent_tag

    def find(self) -> list[Tag]:
        """
        Find all child tags that are direct children of a single tag.

        Returns
        -------
        list[Tag]
            List of child tags. (Does not include the parent tag.)
        """
        # TODO-future-barret;
        # This method could be done with `self._ctx.client.tags.find(parent=self)`
        # For now, use DescendantTags and filter the results
        descendant_tags = DescendantTags(self._ctx, parent_tag=self._parent_tag).find()

        # Filter out tags that are not direct children
        child_tags: list[Tag] = []
        for tag in descendant_tags:
            if tag.get("parent_id") == self._parent_tag["id"]:
                child_tags.append(tag)

        return child_tags


class DescendantTags(ContextManager):
    def __init__(self, ctx: Context, /, *, parent_tag: Tag) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = "v1/tags"
        self._parent_tag = parent_tag

    def find(self) -> list[Tag]:
        """
        Find all child tags that descend from a single tag.

        Returns
        -------
        list[Tag]
            List of tags that desc
        """
        # This method could be done with `tags.find(parent=self._root_id)` but it would require
        # a request for every child tag recursively.
        # By using the `/v1/tags` endpoint, we can get all tags in a single request
        # and filter them in Python.

        # TODO-barret-future: Replace with `self._ctx.client.tags.find(parent=self._root_id)`
        url = self._ctx.url + self._path
        response = self._ctx.session.get(url)
        results = response.json()
        all_tags = []
        for result in results:
            tag = Tag(
                self._ctx,
                # TODO-barret-future: Replace with `self._ctx.client.tags._path`?
                f"{self._path}/{result['id']}",
                **result,
            )
            all_tags.append(tag)

        # O(n^2) algorithm to find all child tags
        # This could be optimized by using a dictionary to store the tags by their parent_id and
        # then recursively traverse the dictionary to find all child tags. O(2 * n) = O(n) but the
        # code is more complex
        #
        # If the tags are always ordered, it could be performed in a single pass (O(n)) as parents
        # always appear before any children
        child_tags = []
        parent_ids = {self._parent_tag["id"]}
        child_tag_found: bool = True
        while child_tag_found:
            child_tag_found = False

            for tag in [*all_tags]:
                if tag.get("parent_id") in parent_ids:
                    child_tags.append(tag)
                    parent_ids.add(tag["id"])
                    all_tags.remove(tag)
                    child_tag_found = True

        return child_tags


class Tags(ContextManager):
    """Content item tags resource."""

    def __init__(self, ctx: Context, path: str) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = path

    def get(self, tag_id: str) -> Tag:
        """
        Get a single tag by its identifier.

        Parameters
        ----------
        tag_id : str
            The identifier for the tag.

        Returns
        -------
        Tag
            The tag object.
        """
        # TODO-barret-future: Replace with `self._ctx.client.tags.find(id=tag_id)`
        if not isinstance(tag_id, str):
            raise TypeError("`tag_id` must be a string")
        if tag_id == "":
            raise ValueError("`tag_id` cannot be an empty string")
        path = f"{self._path}/{tag_id}"
        url = self._ctx.url + path
        response = self._ctx.session.get(url)
        return Tag(self._ctx, path, **response.json())

    class _NameParentAttrs(TypedDict, total=False):
        name: str
        """
        The name of the tag.

        Note: tag names are only unique within the scope of a parent, which
        means that it is possible to have multiple results when querying by
        name; however, querying by both `name` and `parent` ensures a single
        result.
        """
        parent: NotRequired[str | Tag | None]
        """The identifier for the parent tag. If there is no parent, the tag is a top-level tag."""

    def _update_parent_kwargs(self, kwargs: dict) -> dict:
        parent = kwargs.get("parent", None)
        if parent is None:
            return kwargs

        ret_kwargs = {**kwargs}

        # Remove `parent` from ret_kwargs
        # and store the `parent_id` in the ret_kwargs below
        del ret_kwargs["parent"]

        if isinstance(parent, Tag):
            parent: str = parent["id"]

        if isinstance(parent, str):
            if parent == "":
                raise ValueError("Tag `parent` cannot be an empty string")
            ret_kwargs["parent_id"] = parent
            return ret_kwargs

        raise TypeError("`parent=` must be a string or Tag instance")

    def find(self, /, **kwargs: Unpack[Tags._NameParentAttrs]) -> list[Tag]:
        """
        Find tags by name and/or parent.

        Note: tag names are only unique within the scope of a parent, which means that it is
        possible to have multiple results when querying by name; However, querying by both `name`
        and `parent` ensures a single result.

        Parameters
        ----------
        name : str, optional
            The name of the tag.
        parent : str, Tag, optional
            The identifier for the parent tag. If there is no parent, the tag is a top-level tag.

        Returns
        -------
        list[Tag]
            List of tags that match the query. Defaults to all Tags.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client(...)

        # Find all tags
        all_tags = client.tags.find()

        # Find all tags with the name
        mytag = client.tags.find(name="tag_name")

        # Find all tags with the name and parent
        subtags = client.tags.find(name="sub_name", parent=mytag)
        subtags = client.tags.find(name="sub_name", parent=mytag["id"])
        ```
        """
        updated_kwargs = self._update_parent_kwargs(
            kwargs,  # pyright: ignore[reportArgumentType]
        )
        url = self._ctx.url + self._path

        response = self._ctx.session.get(url, params=updated_kwargs)
        results = response.json()
        return [Tag(self._ctx, f"{self._path}/{result['id']}", **result) for result in results]

    def create(self, /, **kwargs: Unpack[Tags._NameParentAttrs]) -> Tag:
        """
        Create a tag.

        Parameters
        ----------
        name : str
            The name of the tag.
        parent : str, Tag, optional
            The identifier for the parent tag. If there is no parent, the tag is a top-level tag.

        Returns
        -------
        Tag
            Newly created tag object.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client(...)

        mytag = client.tags.create(name="tag_name")
        subtag = client.tags.create(name="subtag_name", parent=mytag)
        ```
        """
        updated_kwargs = self._update_parent_kwargs(
            kwargs,  # pyright: ignore[reportArgumentType]
        )

        url = self._ctx.url + self._path
        response = self._ctx.session.post(url, json=updated_kwargs)
        result = response.json()
        return Tag(self._ctx, f"{self._path}/{result['id']}", **result)


class ContentItemTags(ContextManager):
    """Content item tags resource."""

    def __init__(self, ctx: Context, path: str, /, *, tags_path: str, content_guid: str) -> None:
        super().__init__()
        self._ctx = ctx

        # v1/content/{guid}/tags
        self._path = path
        self._tags_path = tags_path

        self._content_guid = content_guid

    def find(self) -> list[Tag]:
        """
        Find all tags that are associated with a single content item.

        Returns
        -------
        list[Tag]
            List of tags associated with the content item.
        """
        url = self._ctx.url + self._path
        response = self._ctx.session.get(url)
        results = response.json()

        tags: list[Tag] = []
        for result in results:
            tags.append(
                Tag(
                    self._ctx,
                    f"{self._tags_path}/{result['id']}",
                    **result,
                )
            )

        return tags

    def _to_tag_ids(self, tags: tuple[str | Tag, ...]) -> list[str]:
        tag_ids: list[str] = []
        for i, tag in enumerate(tags):
            tag_id = tag["id"] if isinstance(tag, Tag) else tag
            if not isinstance(tag_id, str):
                raise TypeError(f"Expected 'tags[{i}]' to be a string. Received: {tag_id}")
            if tag_id == "":
                raise ValueError(f"Expected 'tags[{i}]' to be non-empty. Received: {tag_id}")

            tag_ids.append(tag_id)

        return tag_ids

    def add(self, *tags: str | Tag) -> None:
        """
        Add the specified tags to an individual content item.

        When adding a tag, all tags above the specified tag in the tag tree are also added to the
        content item.

        Parameters
        ----------
        tags : str | Tag
            The tags id or tag object to add to the content item.

        Returns
        -------
        None
        """
        tag_ids = self._to_tag_ids(tags)

        url = self._ctx.url + self._path
        for tag_id in tag_ids:
            _ = self._ctx.session.post(url, json={"tag_id": tag_id})
        return

    def delete(self, *tags: str | Tag) -> None:
        """
        Remove the specified tags from an individual content item.

        When removing a tag, all tags above the specified tag in the tag tree are also removed from
        the content item.

        Parameters
        ----------
        tags : str | Tag
            The tags id or tag object to remove from the content item.

        Returns
        -------
        None
        """
        tag_ids = self._to_tag_ids(tags)

        url = self._ctx.url + self._path
        for tag_id in tag_ids:
            tag_url = f"{url}/{tag_id}"
            self._ctx.session.delete(tag_url)
        return
