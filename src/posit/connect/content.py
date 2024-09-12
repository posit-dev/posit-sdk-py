"""Content resources."""

from __future__ import annotations

import posixpath
import time
from posixpath import dirname
from typing import Any, List, Optional, overload

from posit.connect.oauth.associations import ContentItemAssociations

from . import tasks
from .bundles import Bundles
from .env import EnvVars
from .permissions import Permissions
from .resources import Resource, ResourceParameters, Resources
from .tasks import Task
from .variants import Variants


class ContentItemOAuth(Resource):
    def __init__(self, params: ResourceParameters, content_guid: str) -> None:
        super().__init__(params)
        self.content_guid = content_guid

    @property
    def associations(self) -> ContentItemAssociations:
        return ContentItemAssociations(
            self.params, content_guid=self.content_guid
        )


class ContentItemOwner(Resource):
    pass


class ContentItem(Resource):
    def __getitem__(self, key: Any) -> Any:
        v = super().__getitem__(key)
        if key == "owner" and isinstance(v, dict):
            return ContentItemOwner(params=self.params, **v)
        return v

    @property
    def oauth(self) -> ContentItemOAuth:
        if "guid" not in self:
            raise ValueError("ContentItemOAuth requires content guid")
        return ContentItemOAuth(self.params, content_guid=self["guid"])

    def delete(self) -> None:
        """Delete the content item."""
        path = f"v1/content/{self.guid}"
        url = self.params.url + path
        self.params.session.delete(url)

    def deploy(self) -> tasks.Task:
        """Deploy the content.

        Spawns an asynchronous task, which activates the latest bundle.

        Returns
        -------
        tasks.Task
            The task for the deployment.

        Examples
        --------
        >>> task = content.deploy()
        >>> task.wait_for()
        None
        """
        path = f"v1/content/{self.guid}/deploy"
        url = self.params.url + path
        response = self.params.session.post(url, json={"bundle_id": None})
        result = response.json()
        ts = tasks.Tasks(self.params)
        return ts.get(result["task_id"])

    def render(self) -> Task:
        """Render the content.

        Submit a render request to the server for the content. After submission, the server executes an asynchronous process to render the content. This is useful when content is dependent on external information, such as a dataset.

        See Also
        --------
        restart

        Examples
        --------
        >>> render()
        """
        self.update()

        if self.is_rendered:
            variants = self._variants.find()
            variants = [variant for variant in variants if variant.is_default]
            if len(variants) != 1:
                raise RuntimeError(
                    f"Found {len(variants)} default variants. Expected 1. Without a single default variant, the content cannot be refreshed. This is indicative of a corrupted state."
                )
            variant = variants[0]
            return variant.render()
        else:
            raise ValueError(
                f"Render not supported for this application mode: {self.app_mode}. Did you need to use the 'restart()' method instead? Note that some application modes do not support 'render()' or 'restart()'."
            )

    def restart(self) -> None:
        """Mark for restart.

        Sends a restart request to the server for the content. Once submitted, the server performs an asynchronous process to restart the content. This is particularly useful when the content relies on external information loaded into application memory, such as datasets. Additionally, restarting can help clear memory leaks or reduce excessive memory usage that might build up over time.

        See Also
        --------
        render

        Examples
        --------
        >>> restart()
        """
        self.update()

        if self.is_interactive:
            unix_epoch_in_seconds = str(int(time.time()))
            key = f"_CONNECT_RESTART_TMP_{unix_epoch_in_seconds}"
            self.environment_variables.create(key, unix_epoch_in_seconds)
            self.environment_variables.delete(key)
            # GET via the base Connect URL to force create a new worker thread.
            url = posixpath.join(
                dirname(self.params.url), f"content/{self.guid}"
            )
            self.params.session.get(url)
            return None
        else:
            raise ValueError(
                f"Restart not supported for this application mode: {self.app_mode}. Did you need to use the 'render()' method instead? Note that some application modes do not support 'render()' or 'restart()'."
            )

    @overload
    def update(
        self,
        *args,
        name: str = ...,
        title: Optional[str] = ...,
        description: str = ...,
        access_type: str = ...,
        owner_guid: Optional[str] = ...,
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
        **kwargs,
    ) -> None:
        """Update the content item.

        Parameters
        ----------
        name : str, optional
        title : Optional[str], optional
        description : str, optional
        access_type : str, optional
        owner_guid : Optional[str], optional
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
        """
        ...

    @overload
    def update(self, *args, **kwargs) -> None:
        """Update the content item."""
        ...

    def update(self, *args, **kwargs) -> None:
        """Update the content item."""
        body = dict(*args, **kwargs)
        url = self.params.url + f"v1/content/{self.guid}"
        response = self.params.session.patch(url, json=body)
        super().update(**response.json())

    # Relationships

    @property
    def bundles(self) -> Bundles:
        return Bundles(self.params, self.guid)

    @property
    def environment_variables(self) -> EnvVars:
        return EnvVars(self.params, self.guid)

    @property
    def permissions(self) -> Permissions:
        return Permissions(self.params, self.guid)

    @property
    def owner(self) -> dict:
        if "owner" not in self:
            # It is possible to get a content item that does not contain owner.
            # "owner" is an optional additional request param.
            # If it's not included, we can retrieve the information by `owner_guid`
            from .users import Users

            self["owner"] = Users(self.params).get(self.owner_guid)
        return self["owner"]

    @property
    def _variants(self) -> Variants:
        return Variants(self.params, self.guid)

    @property
    def is_interactive(self) -> bool:
        return self.app_mode in {
            "api",
            "jupyter-voila",
            "python-api",
            "python-bokeh",
            "python-dash",
            "python-fastapi",
            "python-shiny",
            "python-streamlit",
            "quarto-shiny",
            "rmd-shiny",
            "shiny",
            "tensorflow-saved-model",
        }

    @property
    def is_rendered(self) -> bool:
        return self.app_mode in {
            "rmd-static",
            "jupyter-static",
            "quarto-static",
        }


class Content(Resources):
    """Content resource.

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
        params: ResourceParameters,
        *,
        owner_guid: str | None = None,
    ) -> None:
        super().__init__(params)
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
        *,
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
    ) -> ContentItem:
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
    def create(self, **kwargs) -> ContentItem:
        """Create a content item.

        Returns
        -------
        ContentItem
        """
        ...

    def create(self, **kwargs) -> ContentItem:
        """Create a content item.

        Returns
        -------
        ContentItem
        """
        path = "v1/content"
        url = self.params.url + path
        response = self.params.session.post(url, json=kwargs)
        return ContentItem(self.params, **response.json())

    @overload
    def find(
        self,
        owner_guid: str = ...,
        name: str = ...,
        include: Optional[str] = "owner,tags",
    ) -> List[ContentItem]:
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
    ) -> List[ContentItem]:
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
    ) -> List[ContentItem]:
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
        path = "v1/content"
        url = self.params.url + path
        response = self.params.session.get(url, params=params)
        return [
            ContentItem(
                self.params,
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
    ) -> ContentItem | None:
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
    ) -> ContentItem | None:
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
    ) -> ContentItem | None:
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

    def get(self, guid: str) -> ContentItem:
        """Get a content item.

        Parameters
        ----------
        guid : str

        Returns
        -------
        ContentItem
        """
        path = f"v1/content/{guid}"
        url = self.params.url + path
        response = self.params.session.get(url)
        return ContentItem(self.params, **response.json())
