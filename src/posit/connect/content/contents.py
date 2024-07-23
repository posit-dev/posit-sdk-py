from __future__ import annotations

from typing import List, Optional, overload

from requests import Session

from .. import urls
from ..config import Config
from ..resources import Resources
from .content import Content


class Contents(Resources):
    """Contents resource.

    Parameters
    ----------
    config : Config
        Configuration object.
    session : Session
        Requests session object.
    owner_guid : str, optional
        Content item owner identifier. Filters results to those owned by a specific user (the default is None, which implies not filtering results on owner identifier).
    """

    def __init__(
        self,
        config: Config,
        session: Session,
        *,
        owner_guid: str | None = None,
    ) -> None:
        self.url = urls.append(config.url, "v1/content")
        self.config = config
        self.session = session
        self.owner_guid = owner_guid

    def _get_default_params(self) -> dict:
        """Build default parameters for GET requests.

        Returns
        -------
        dict
        """
        params = {}
        if self.owner_guid:
            params["owner_guid"] = self.owner_guid
        return params

    def count(self) -> int:
        """Count the number of content items.

        Returns
        -------
        int
        """
        return len(self.find())

    @overload
    def create(
        self,
        name: str = ...,
        title: Optional[str] = ...,
        description: str = ...,
        access_type: str = ...,
        connection_timeout: Optional[int] = ...,
        read_timeout: Optional[int] = ...,
        init_timeout: Optional[int] = ...,
        idle_timeout: Optional[int] = ...,
        max_processes: Optional[int] = ...,
        min_processes: Optional[int] = ...,
        max_conns_per_process: Optional[int] = ...,
        load_factor: Optional[float] = ...,
        cpu_request: Optional[float] = ...,
        cpu_limit: Optional[float] = ...,
        memory_request: Optional[int] = ...,
        memory_limit: Optional[int] = ...,
        amd_gpu_limit: Optional[int] = ...,
        nvidia_gpu_limit: Optional[int] = ...,
        run_as: Optional[str] = ...,
        run_as_current_user: Optional[bool] = ...,
        default_image_name: Optional[str] = ...,
        default_r_environment_management: Optional[bool] = ...,
        default_py_environment_management: Optional[bool] = ...,
        service_account_name: Optional[str] = ...,
    ) -> Content:
        """Create a content item.

        Parameters
        ----------
        name : str, optional
        title : Optional[str], optional
        description : str, optional
        access_type : str, optional
        connection_timeout : Optional[int], optional
        read_timeout : Optional[int], optional
        init_timeout : Optional[int], optional
        idle_timeout : Optional[int], optional
        max_processes : Optional[int], optional
        min_processes : Optional[int], optional
        max_conns_per_process : Optional[int], optional
        load_factor : Optional[float], optional
        cpu_request : Optional[float], optional
        cpu_limit : Optional[float], optional
        memory_request : Optional[int], optional
        memory_limit : Optional[int], optional
        amd_gpu_limit : Optional[int], optional
        nvidia_gpu_limit : Optional[int], optional
        run_as : Optional[str], optional
        run_as_current_user : Optional[bool], optional
        default_image_name : Optional[str], optional
        default_r_environment_management : Optional[bool], optional
        default_py_environment_management : Optional[bool], optional
        service_account_name : Optional[str], optional

        Returns
        -------
        ContentItem
        """
        ...

    @overload
    def create(self, *args, **kwargs) -> Content:
        """Create a content item.

        Returns
        -------
        ContentItem
        """
        ...

    def create(self, *args, **kwargs) -> Content:
        """Create a content item.

        Returns
        -------
        ContentItem
        """
        body = dict(*args, **kwargs)
        path = "v1/content"
        url = urls.append(self.config.url, path)
        response = self.session.post(url, json=body)
        return Content(self.config, self.session, **response.json())

    @overload
    def find(
        self,
        owner_guid: str = ...,
        name: str = ...,
        include: Optional[str] = "owner,tags",
    ) -> List[Content]:
        """Find content items.

        Parameters
        ----------
        owner_guid : str, optional
            The owner's unique identifier, by default ...
        name : str, optional
            The simple URL friendly name, by default ...
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        List[ContentItem]
        """
        ...

    @overload
    def find(
        self, *args, include: Optional[str] = "owner,tags", **kwargs
    ) -> List[Content]:
        """Find content items.

        Parameters
        ----------
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        List[ContentItem]
        """
        ...

    def find(
        self, *args, include: Optional[str] = "owner,tags", **kwargs
    ) -> List[Content]:
        """Find content items.

        Parameters
        ----------
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        List[ContentItem]
        """
        params = self._get_default_params()
        params.update(args)
        params.update(kwargs)
        params["include"] = include
        response = self.session.get(self.url, params=params)
        return [
            Content(
                config=self.config,
                session=self.session,
                **result,
            )
            for result in response.json()
        ]

    @overload
    def find_one(
        self,
        owner_guid: str = ...,
        name: str = ...,
        include: Optional[str] = "owner,tags",
    ) -> Content | None:
        """Find content items.

        Parameters
        ----------
        owner_guid : str, optional
            The owner's unique identifier, by default ...
        name : str, optional
            The simple URL friendly name, by default ...
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        ContentItem | None
        """
        ...

    @overload
    def find_one(
        self, *args, include: Optional[str] = "owner,tags", **kwargs
    ) -> Content | None:
        """Find content items.

        Parameters
        ----------
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        ContentItem | None
        """
        ...

    def find_one(
        self, *args, include: Optional[str] = "owner,tags", **kwargs
    ) -> Content | None:
        """Find content items.

        Parameters
        ----------
        include : Optional[str], optional
            Comma separated list of details to include in the response, allows 'owner' and 'tags', by default 'owner,tags'

        Returns
        -------
        ContentItem | None
        """
        items = self.find(*args, include=include, **kwargs)
        return next(iter(items), None)

    def get(self, guid: str) -> Content:
        """Get a content item.

        Parameters
        ----------
        guid : str

        Returns
        -------
        ContentItem
        """
        url = urls.append(self.url, guid)
        response = self.session.get(url)
        return Content(self.config, self.session, **response.json())
