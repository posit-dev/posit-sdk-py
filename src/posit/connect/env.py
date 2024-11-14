from __future__ import annotations

from typing import Any, Iterator, List, Mapping, MutableMapping, Optional

from posit.connect._api_call import ApiCallMixin
from posit.connect._types_content_item import ContentItemContext
from posit.connect._types_context import ContextP


class EnvVars(ApiCallMixin, ContextP[ContentItemContext], MutableMapping[str, Optional[str]]):
    def __init__(self, ctx: ContentItemContext) -> None:
        super().__init__()
        self._ctx = ctx
        self._path = f"v1/content/{self._ctx.content_guid}/environment"

    def __delitem__(self, key: str, /) -> None:
        """Delete the environment variable.

        Parameters
        ----------
        key : str
            The name of the environment variable to delete.

        Examples
        --------
        >>> vars = EnvVars(params, content_guid)
        >>> del vars["DATABASE_URL"]
        """
        self.update({key: None})

    def __getitem__(self, key: Any) -> Any:
        raise NotImplementedError(
            "Since environment variables may contain sensitive information, the values are not accessible outside of Connect.",
        )

    def __iter__(self) -> Iterator:
        return iter(self.find())

    def __len__(self):
        return len(self.find())

    def __setitem__(self, key: str, value: Optional[str], /) -> None:
        """Set environment variable.

        Set the environment variable for content.

        Parameters
        ----------
        key : str
            The name of the environment variable to set.
        value : str
            The value assigned to the environment variable.

        Examples
        --------
        >>> vars = EnvVars(params, content_guid)
        >>> vars["DATABASE_URL"] = "postgres://user:password@localhost:5432/database"
        """
        self.update({key: value})

    def clear(self) -> None:
        """Remove all environment variables.

        Examples
        --------
        >>> clear()
        """
        self._put_api(json=[])

    def create(self, key: str, value: str, /) -> None:
        """Create an environment variable.

        Set an environment variable with the provided key and value. If the key already exists, its value is overwritten without warning to the provided value.

        Parameters
        ----------
        key : str
            The name of the environment variable to create.
        value : str
            The value assigned to the environment variable.

        Examples
        --------
        >>> create(
        ...     "DATABASE_URL",
        ...     "postgres://user:password@localhost:5432/database",
        ... )
        """
        self.update({key: value})

    def delete(self, key: str, /) -> None:
        """Delete the environment variable.

        Parameters
        ----------
        key : str
            The name of the environment variable to delete.

        Examples
        --------
        >>> delete("DATABASE_URL")
        """
        self.update({key: None})

    def find(self) -> List[str]:
        """Find environment variables.

        List the names of the defined environment variables.

        Returns
        -------
        List[str]
            Environment variable names.

        Notes
        -----
        The Connect environment variables API does support retrieving the environment variable's value.

        Examples
        --------
        >>> find()
        ['DATABASE_URL']
        """
        result = self._get_api()
        return result

    def items(self):
        raise NotImplementedError(
            "Since environment variables may contain sensitive information, the values are not accessible outside of Connect.",
        )

    def update(self, other=(), /, **kwargs: Optional[str]):
        """
        Update environment variables.

        Updates environment variables with the provided key-value pairs. Accepts a dictionary, an iterable of key-value pairs, or keyword arguments to update the environment variables. All keys and values must be str types.

        Parameters
        ----------
        other : dict, iterable of tuples, optional
            A dictionary or an iterable of key-value pairs to update the environment variables. By default, it is None.
        **kwargs : str
            Additional key-value pairs to update the environment variables.

        Raises
        ------
        TypeError
            If the type of 'other' is not a dictionary or an iterable of key-value pairs.

        Examples
        --------
        Update using keyword arguments:
        >>> update(DATABASE_URL="postgres://user:password@localhost:5432/database")

        Update using multiple keyword arguments:
        >>> update(
        ...     DATABASE_URL="postgres://localhost:5432/database",
        ...     DATABASE_USERNAME="user",
        ...     DATABASE_PASSWORD="password",
        ... )

        Update using a dictionary:
        >>> update(
        ...     {
        ...         "DATABASE_URL": "postgres://localhost:5432/database",
        ...         "DATABASE_USERNAME": "user",
        ...         "DATABASE_PASSWORD": "password",
        ...     }
        ... )

        Update using an iterable of key-value pairs:
        >>> update(
        ...     [
        ...         ("DATABASE_URL", "postgres://localhost:5432/database"),
        ...         ("DATABASE_USERNAME", "user"),
        ...         ("DATABASE_PASSWORD", "password"),
        ...     ]
        ... )
        """
        d = {}
        if isinstance(other, Mapping):
            for key in other:
                d[key] = other[key]
        elif hasattr(other, "keys"):
            for key in other.keys():  # noqa: SIM118
                d[key] = other[key]
        else:
            for key, value in other:
                d[key] = value

        for key, value in kwargs.items():
            d[key] = value

        body = [{"name": key, "value": value} for key, value in d.items()]
        self._patch_api(json=body)
