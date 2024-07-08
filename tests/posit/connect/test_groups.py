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
    def test_name_arg(self):
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        name = "test"

        # behavior
        mock_groups_create = responses.post(
            f"https://connect.example.com/__api__/v1/groups",
            json=load_mock(f"v1/groups/{guid}.json"),
            match=[matchers.json_params_matcher({"name": name})],
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.create(name)

        # assert
        assert group.guid == guid
        assert mock_groups_create.call_count == 1

    @responses.activate
    def test_name_kwarg(self):
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        name = "test"

        # behavior
        mock_groups_create = responses.post(
            f"https://connect.example.com/__api__/v1/groups",
            json=load_mock(f"v1/groups/{guid}.json"),
            match=[matchers.json_params_matcher({"name": name})],
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.create(name=name)

        # assert
        assert group.guid == guid
        assert mock_groups_create.call_count == 1
        assert mock_groups_create.calls[0].request

    @responses.activate
    def test_temp_ticket(self):
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        ticket = "test"

        # behavior
        mock_groups_create = responses.post(
            f"https://connect.example.com/__api__/v1/groups",
            json=load_mock(f"v1/groups/{guid}.json"),
            match=[matchers.json_params_matcher({"temp_ticket": ticket})],
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.create(temp_ticket=ticket)

        # assert
        assert group.guid == guid
        assert mock_groups_create.call_count == 1


class TestGroupsFind:
    @responses.activate
    def test(self):
        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        groups = c.groups.find()

        # assert
        assert len(groups) == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_prefix_arg(self):
        prefix = "test"

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1, "prefix": prefix}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        groups = c.groups.find(prefix)

        # assert
        assert len(groups) == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_prefix_kwarg(self):
        prefix = "test"

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1, "prefix": prefix}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        groups = c.groups.find(prefix=prefix)

        # assert
        assert len(groups) == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote_kwarg_as_true(self):
        remote = True

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups/remote",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups/remote.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        groups = c.groups.find(remote=remote)

        # assert
        assert len(groups) == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote_kwarg_as_false(self):
        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        groups = c.groups.find(remote=False)

        # assert
        assert len(groups) == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_kwargs(self):
        future = "future"

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1, "future": future}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        groups = c.groups.find(future=future)

        # assert
        assert len(groups) == 1
        assert mock_groups_get.call_count == 1


class TestGroupsFindOne:
    @responses.activate
    def test(self):
        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.find_one()

        # assert
        assert group
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_prefix_arg(self):
        prefix = "test"

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1, "prefix": prefix}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.find_one(prefix)

        # assert
        assert group
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_prefix_kwarg(self):
        prefix = "test"

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1, "prefix": prefix}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.find_one(prefix=prefix)

        # assert
        assert group
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote_kwarg_as_true(self):
        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups/remote",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups/remote.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.find_one(remote=True)

        # assert
        assert group
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote_kwarg_as_false(self):
        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.find_one(remote=False)

        # assert
        assert group
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_kwargs(self):
        future = "future"

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 500, "page_number": 1, "future": future}
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.find_one(future=future)

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
        c = Client("12345", "https://connect.example.com")

        # invoke
        group = c.groups.get(guid)

        # assert
        assert group.guid == guid
        assert mock_groups_create.call_count == 1


class TestGroupsCount:
    @responses.activate
    def test(self):
        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[responses.matchers.query_param_matcher({"page_size": 1})],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        count = c.groups.count()

        # assert
        assert count == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_prefix_arg(self):
        prefix = "example"

        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 1, "prefix": prefix},
                )
            ],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        count = c.groups.count(prefix)

        # assert
        assert count == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote_kwarg_as_true(self):
        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups/remote",
            match=[responses.matchers.query_param_matcher({"page_size": 1})],
            json=load_mock("v1/groups/remote.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        count = c.groups.count(remote=True)

        # assert
        assert count == 1
        assert mock_groups_get.call_count == 1

    @responses.activate
    def test_remote_kwarg_as_false(self):
        # behavior
        mock_groups_get = responses.get(
            "https://connect.example.com/__api__/v1/groups",
            match=[responses.matchers.query_param_matcher({"page_size": 1})],
            json=load_mock("v1/groups.json"),
        )

        # setup
        c = Client("12345", "https://connect.example.com")

        # invoke
        count = c.groups.count(remote=False)

        # assert
        assert count == 1
        assert mock_groups_get.call_count == 1
