"""Tag resources."""

from __future__ import annotations

from abc import ABC, abstractmethod

from typing_extensions import TYPE_CHECKING, NotRequired, Optional, TypedDict, Unpack, overload

from ._utils import update_dict_values
from .context import Context, ContextManager
from .resources import Active

if TYPE_CHECKING:
    from .content import ContentItem


class _RelatedTagsBase(ContextManager, ABC):
    @abstractmethod
    def find(self) -> list[Tag]:
        pass


def _update_parent_kwargs(kwargs: dict) -> dict:
    """
    Sets the `parent_id` key in the kwargs if `parent` is provided.

    Asserts that the `parent=` and `parent_id=` keys are not both provided.
    """
    parent = kwargs.get("parent", None)
    parent_id = kwargs.get("parent_id", None)
    if parent is None:
        # No parent to upgrade, return the kwargs as is
        return kwargs
    if parent and parent_id:
        raise ValueError("Cannot provide both `parent=` and `parent_id=`")
    if not isinstance(parent, Tag):
        raise TypeError(
            "`parent=` must be a Tag instance. If using a string, please use `parent_id=`"
        )

    # Remove `parent` from a copy of `kwargs` and replace it with `parent_id`
    ret_kwargs = {**kwargs}
    del ret_kwargs["parent"]
    ret_kwargs["parent_id"] = parent["id"]

    return ret_kwargs


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

        parent = self._ctx.client.tags.get(self["parent_id"])
        return parent

    @property
    def child_tags(self) -> ChildTags:
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

        client = posit.connect.Client()
        mytag = client.tags.find(id="TAG_ID_HERE")

        children = mytag.child_tags.find()
        ```
        """
        return ChildTags(self._ctx, self._path, parent_tag=self)

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

        client = posit.connect.Client()
        mytag = client.tags.find(id="TAG_ID_HERE")

        descendant_tags = mytag.descendant_tags.find()
        ```
        """
        return DescendantTags(self._ctx, parent_tag=self)

    @property
    def content_items(self) -> TagContentItems:
        """
        Find all content items that are tagged with this tag.

        Returns
        -------
        TagContentItems
            Helper class that can `.find()` all content items.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()
        first_tag = client.tags.find()[0]

        first_tag_content_items = first_tag.content_items.find()
        ```
        """
        path = f"{self._path}/content"
        return TagContentItems(self._ctx, path)

    def destroy(self) -> None:
        """
        Removes the tag.

        Deletes a tag, including all descendants in its own tag hierarchy.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()
        first_tag = client.tags.find()[0]

        # Remove the tag
        first_tag.destroy()
        ```
        """
        self._ctx.client.delete(self._path)

    # Allow for every combination of `name` and (`parent` or `parent_id`)
    @overload
    def update(self, /, *, name: str = ..., parent: Tag | None = ...) -> None: ...
    @overload
    def update(self, /, *, name: str = ..., parent_id: str | None = ...) -> None: ...

    def update(
        self,
        **kwargs,
    ) -> None:
        """
        Update the tag.

        Parameters
        ----------
        name : str
            The name of the tag.
        parent : Tag | None, optional
            The parent `Tag` object. If there is no parent, the tag is a top-level tag. To remove
            the parent tag, set the value to `None`. Only one of `parent` or `parent_id` can be
            provided.
        parent_id : str | None, optional
            The identifier for the parent tag. If there is no parent, the tag is a top-level tag.
            To remove the parent tag, set the value to `None`.

        Returns
        -------
        Tag
            Updated tag object.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()
        last_tag = client.tags.find()[-1]

        # Update the tag's name
        updated_tag = last_tag.update(name="new_name")

        # Remove the tag's parent
        updated_tag = last_tag.update(parent=None)
        updated_tag = last_tag.update(parent_id=None)

        # Update the tag's parent
        parent_tag = client.tags.find()[0]
        updated_tag = last_tag.update(parent=parent_tag)
        updated_tag = last_tag.update(parent_id=parent_tag["id"])
        ```
        """
        updated_kwargs = _update_parent_kwargs(kwargs)
        response = self._ctx.client.patch(self._path, json=updated_kwargs)
        result = response.json()
        update_dict_values(self, **result)


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

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()
        first_tag = client.tags.find()[0]

        first_tag_content_items = first_tag.content_items.find()
        ```
        """
        from .content import ContentItem

        response = self._ctx.client.get(self._path)
        results = response.json()
        return [ContentItem(self._ctx, **result) for result in results]


class ChildTags(_RelatedTagsBase):
    def __init__(self, ctx: Context, path: str, /, *, parent_tag: Tag) -> None:
        super().__init__()
        self._ctx: Context = ctx
        self._path: str = path

        self._parent_tag = parent_tag

    def find(self) -> list[Tag]:
        """
        Find all child tags that are direct children of a single tag.

        Returns
        -------
        list[Tag]
            List of child tags. (Does not include the parent tag.)

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()
        mytag = client.tags.get("TAG_ID_HERE")

        child_tags = mytag.child_tags.find()
        ```
        """
        child_tags = self._ctx.client.tags.find(parent=self._parent_tag)
        return child_tags


class DescendantTags(_RelatedTagsBase):
    def __init__(self, ctx: Context, /, *, parent_tag: Tag) -> None:
        super().__init__()
        self._ctx = ctx
        self._parent_tag = parent_tag

    def find(self) -> list[Tag]:
        """
        Find all child tags that descend from a single tag.

        Returns
        -------
        list[Tag]
            List of tags that descend from the parent tag.
        """
        # This method could be done using `tags.find(parent=self._root_id)` but it would require
        # a request for every child tag recursively. (O(n) requests)
        # By using the `/v1/tags` endpoint, we can get all tags in a single request
        # and filter them in Python. (1 request)

        all_tags = self._ctx.client.tags.find()

        # O(n^2) algorithm to find all child tags. O(n) in practice.
        #
        # This could be optimized by using a dictionary to store the tags by their parent_id and
        # then recursively traverse the dictionary to find all child tags. O(2 * n) = O(n) but the
        # code is more complex
        #
        # If the tags are always ordered (which they seem to be ordered by creation date - parents are first),
        # this algo be performed in a two passes (one to add all tags, one to confirm no more additions)
        child_tags = []
        parent_ids = {self._parent_tag["id"]}
        tag_found: bool = True
        while tag_found:
            tag_found = False
            for tag in [*all_tags]:
                parent_id = tag.get("parent_id")
                if not parent_id:
                    # Skip tags with no parent
                    all_tags.remove(tag)
                    continue
                if parent_id in parent_ids:
                    # Child found, remove from search list
                    child_tags.append(tag)
                    parent_ids.add(tag["id"])
                    # Remove from search list
                    all_tags.remove(tag)
                    tag_found = True

        return child_tags


class Tags(ContextManager):
    """Content item tags resource."""

    def __init__(self, ctx: Context, path: str) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = path

    def _tag_path(self, tag_id: str) -> str:
        if not isinstance(tag_id, str):
            raise TypeError('Tag `"id"` must be a string')
        if tag_id == "":
            raise ValueError('Tag `"id"` cannot be an empty string')

        return f"{self._path}/{tag_id}"

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

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()
        mytag = client.tags.get("TAG_ID_HERE")
        ```
        """
        if not isinstance(tag_id, str):
            raise TypeError("`tag_id` must be a string")

        if tag_id == "":
            raise ValueError("`tag_id` cannot be an empty string")
        path = self._tag_path(tag_id)
        response = self._ctx.client.get(path)
        return Tag(self._ctx, path, **response.json())

    # Allow for every combination of `name` and (`parent` or `parent_id`)
    @overload
    def find(self, /, *, name: str = ..., parent: Tag = ...) -> list[Tag]: ...
    @overload
    def find(self, /, *, name: str = ..., parent_id: str = ...) -> list[Tag]: ...

    def find(self, /, **kwargs) -> list[Tag]:
        """
        Find tags by name and/or parent.

        Note: tag names are only unique within the scope of a parent, which means that it is
        possible to have multiple results when querying by name; However, querying by both `name`
        and `parent` ensures a single result.

        Parameters
        ----------
        name : str, optional
            The name of the tag.
        parent : Tag, optional
            The parent `Tag` object. If there is no parent, the tag is a top-level tag. Only one of
            `parent` or `parent_id` can be provided.
        parent_id : str, optional
            The identifier for the parent tag. If there is no parent, the tag is a top-level tag.

        Returns
        -------
        list[Tag]
            List of tags that match the query. Defaults to all Tags.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()

        # Find all tags
        all_tags = client.tags.find()

        # Find all tags with the name
        mytag = client.tags.find(name="tag_name")

        # Find all tags with the name and parent
        subtags = client.tags.find(name="sub_name", parent=mytag)
        subtags = client.tags.find(name="sub_name", parent=mytag["id"])
        ```
        """
        updated_kwargs = _update_parent_kwargs(
            kwargs,  # pyright: ignore[reportArgumentType]
        )
        response = self._ctx.client.get(self._path, params=updated_kwargs)
        results = response.json()
        return [Tag(self._ctx, self._tag_path(result["id"]), **result) for result in results]

    @overload
    def create(self, /, *, name: str) -> Tag: ...
    @overload
    def create(self, /, *, name: str, parent: Tag) -> Tag: ...
    @overload
    def create(self, /, *, name: str, parent_id: str) -> Tag: ...

    def create(self, /, **kwargs) -> Tag:
        """
        Create a tag.

        Parameters
        ----------
        name : str
            The name of the tag.
        parent : Tag, optional
            The parent `Tag` object. If there is no parent, the tag is a top-level tag. Only one of
            `parent` or `parent_id` can be provided.
        parent_id : str, optional
            The identifier for the parent tag. If there is no parent, the tag is a top-level tag.

        Returns
        -------
        Tag
            Newly created tag object.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()

        category_tag = client.tags.create(name="category_name")
        tag = client.tags.create(name="tag_name", parent=category_tag)
        ```
        """
        updated_kwargs = _update_parent_kwargs(
            kwargs,  # pyright: ignore[reportArgumentType]
        )

        response = self._ctx.client.post(self._path, json=updated_kwargs)
        result = response.json()
        return Tag(self._ctx, self._tag_path(result["id"]), **result)


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

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()
        content_item = client.content.find_one()

        # Find all tags associated with the content item
        content_item_tags = content_item.tags.find()
        ```
        """
        response = self._ctx.client.get(self._path)
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

    def _to_tag_id(self, tag: str | Tag) -> str:
        if isinstance(tag, Tag):
            tag_id = tag["id"]
            if not isinstance(tag_id, str):
                raise TypeError(f'Expected `tag=` `"id"` to be a string. Received: {tag}')

        elif isinstance(tag, str):
            tag_id = tag
        else:
            raise TypeError(f"Expected `tag=` to be a string or Tag object. Received: {tag}")

        if tag_id == "":
            raise ValueError(f"Expected 'tag=' ID to be non-empty. Received: {tag_id}")

        return tag_id

    def add(self, tag: str | Tag) -> None:
        """
        Add the specified tag to an individual content item.

        When adding a tag, all tags above the specified tag in the tag tree are also added to the
        content item.

        Parameters
        ----------
        tag : str | Tag
            The tag id or tag object to add to the content item.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()

        content_item = client.content.find_one()
        tag = client.tags.find()[0]

        # Add a tag
        content_item.tags.add(tag)
        ```
        """
        tag_id = self._to_tag_id(tag)

        self._ctx.client.post(self._path, json={"tag_id": tag_id})

    def delete(self, tag: str | Tag) -> None:
        """
        Remove the specified tag from an individual content item.

        When removing a tag, all tags above the specified tag in the tag tree are also removed from
        the content item.

        Parameters
        ----------
        tag : str | Tag
            The tag id or tag object to remove from the content item.

        Examples
        --------
        ```python
        import posit

        client = posit.connect.Client()

        content_item = client.content.find_one()
        content_item_first_tag = content_item.tags.find()[0]

        # Remove a tag
        content_item.tags.delete(content_item_first_tag)
        ```
        """
        tag_id = self._to_tag_id(tag)

        self._ctx.client.delete(f"{self._path}/{tag_id}")
