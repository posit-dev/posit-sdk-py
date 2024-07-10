from unittest.mock import Mock

import pytest
import requests
import responses

from responses import matchers

from posit.connect.client import Client
from posit.connect.config import Config
from posit.connect.groups import Group

from .api import load_mock  # type: ignore

session = Mock()
url = Mock()


class TestGroupAttributes:
    @classmethod
    def setup_class(cls):
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        config = Config(api_key="12345", url="https://connect.example.com/")
        session = requests.Session()
        fake_item = load_mock(f"v1/groups/{guid}.json")
        cls.item = Group(config, session, **fake_item)

    def test_guid(self):
        assert self.item.guid == "6f300623-1e0c-48e6-a473-ddf630c0c0c3"

    def test_name(self):
        assert self.item.name == "Friends"

    def test_owner_guid(self):
        assert self.item.owner_guid == "20a79ce3-6e87-4522-9faf-be24228800a4"


class TestGroupsCreate:
    @responses.activate
    def test(self):
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        kwargs = {
            "name": "name",
        }

        # behavior
        # note: POST for local calls
        mock_groups_create = responses.post(
            f"https://connect.example.com/__api__/v1/groups",
            json=load_mock(f"v1/groups/{guid}.json"),
            match=[matchers.json_params_matcher(kwargs)],
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        group = c.groups.create(**kwargs)

        # assert
        assert group.guid == guid
        assert mock_groups_create.call_count == 1
        assert mock_groups_create.calls[0].request

    @responses.activate
    def test_remote(self):
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        kwargs = {"temp_ticket": "temp_ticket"}

        # behavior
        # note: PUT for remote calls
        mock_groups_create = responses.put(
            f"https://connect.example.com/__api__/v1/groups",
            json=load_mock(f"v1/groups/{guid}.json"),
            match=[matchers.json_params_matcher(kwargs)],
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        group = c.groups.create(**kwargs)

        # assert
        assert group.guid == guid
        assert mock_groups_create.call_count == 1
        assert mock_groups_create.calls[0].request


class TestGroupsFind:
    @responses.activate
    def test(self):
        kwargs = {"prefix": "friends"}

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {**kwargs, "page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        groups = c.groups.find(**kwargs, remote=False)

        # assert
        assert len(groups) == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote(self):
        kwargs = {"prefix": "friends"}

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups/remote",
            match=[
                responses.matchers.query_param_matcher(
                    {**kwargs, "page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        groups = c.groups.find(**kwargs, remote=True)

        # assert
        assert len(groups) == 1
        assert mock_groups_get.call_count == 1


class TestGroupsFindOne:
    @responses.activate
    def test(self):
        kwargs = {"prefix": "friends"}

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {**kwargs, "page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        group = c.groups.find_one(**kwargs, remote=False)

        # assert
        assert group
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote(self):
        kwargs = {"prefix": "friends"}

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups/remote",
            match=[
                responses.matchers.query_param_matcher(
                    {**kwargs, "page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        group = c.groups.find_one(**kwargs, remote=True)

        # assert
        assert group
        assert mock_groups_get.call_count == 1


class TestGroupsGet:
    @responses.activate
    def test_guid_arg(self):
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"

        # behavior
        mock_groups_create = responses.get(
            f"https://connect.example.com/__api__/v1/groups/{guid}",
            json=load_mock(f"v1/groups/{guid}.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        group = c.groups.get(guid)

        # assert
        assert group.guid == guid
        assert mock_groups_create.call_count == 1


class TestGroupsCount:
    @responses.activate
    def test(self):
        kwargs = {"prefix": "friends"}

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {**kwargs, "page_size": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        count = c.groups.count(**kwargs, remote=False)

        # assert
        assert count == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote(self):
        kwargs = {"prefix": "friends"}

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups/remote",
            match=[
                responses.matchers.query_param_matcher(
                    {**kwargs, "page_size": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")

        # invoke
        count = c.groups.count(**kwargs, remote=True)

        # assert
        assert count == 1
        assert mock_groups_get.call_count == 1
