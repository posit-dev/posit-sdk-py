from __future__ import annotations

from typing import Any, List, Iterable, MutableMapping, Optional, overload

from requests import Session

from . import urls
from .config import Config
from .resources import Resources


class EnvVars(Resources):
    def __init__(
        self, config: Config, session: Session, content_guid: str
    ) -> None:
        super().__init__(config, session)
        self.content_guid = content_guid

    def __setitem__(self, key: str, value: str, /) -> None:
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
        >>> vars = EnvVars(config, session, content_guid)
        >>> vars["DATABASE_URL"] = (
        ...     "postgres://user:password@localhost:5432/database"
        ... )
        """
        self.update({key: value})

    def __delitem__(self, key: str, /) -> None:
        """Delete the environment variable.

        Parameters
        ----------
        key : str
            The name of the environment variable to delete.

        Examples
        --------
        >>> vars = EnvVars(config, session, content_guid)
        >>> del vars["DATABASE_URL"]
        """
        self.update({key: None})

    def clear(self) -> None:
        """Remove all environment variables.

        Examples
        --------
        >>> clear()
        """
        path = f"v1/content/{self.content_guid}/environment"
        url = urls.append(self.config.url, path)
        self.session.put(url, json=[])

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
        path = f"v1/content/{self.content_guid}/environment"
        url = urls.append(self.config.url, path)
        response = self.session.get(url)
        return response.json()

    @overload
    def update(
        self, other: MutableMapping[str, Optional[str]], /, **kwargs: str
    ) -> None: ...

    @overload
    def update(
        self, other: Iterable[tuple[str, Optional[str]]], /, **kwargs: str
    ) -> None: ...

    @overload
    def update(self, /, **kwargs: str) -> None: ...

    def update(self, other=None, /, **kwargs: str) -> None:
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
        >>> update(
        ...     DATABASE_URL="postgres://user:password@localhost:5432/database"
        ... )

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
        d = dict[str, str]()
        if other is not None:
            if isinstance(other, MutableMapping):
                d.update(other)
            elif isinstance(other, Iterable) and not isinstance(
                other, (str, bytes)
            ):
                try:
                    d.update(other)
                except (TypeError, ValueError):
                    raise TypeError(
                        f"update expected a {MutableMapping.__name__} or {Iterable.__name__}, got {type(other).__name__}"
                    )
            else:
                raise TypeError(
                    f"update expected a {MutableMapping.__name__} or {Iterable.__name__}, got {type(other).__name__}"
                )

        if kwargs:
            d.update(kwargs)

        body = [{"name": key, "value": value} for key, value in d.items()]
        path = f"v1/content/{self.content_guid}/environment"
        url = urls.append(self.config.url, path)
        self.session.patch(url, json=body)
