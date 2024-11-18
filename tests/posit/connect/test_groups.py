from unittest import mock
from unittest.mock import Mock

import responses

from posit.connect.client import Client
from posit.connect.context import Context
from posit.connect.groups import Group
from posit.connect.users import User

from .api import load_mock_dict

session = Mock()
url = Mock()


class TestGroupAttributes:
    @classmethod
    def setup_class(cls):
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        fake_item = load_mock_dict(f"v1/groups/{guid}.json")
        cls.item = Group(mock.Mock(), **fake_item)

    def test_guid(self):
        assert self.item["guid"] == "6f300623-1e0c-48e6-a473-ddf630c0c0c3"

    def test_name(self):
        assert self.item["name"] == "Friends"

    def test_owner_guid(self):
        assert self.item["owner_guid"] == "20a79ce3-6e87-4522-9faf-be24228800a4"


class TestGroupMembers:
    @classmethod
    def setup_class(cls):
        cls.client = Client("https://connect.example", "12345")
        guid = "6f300623-1e0c-48e6-a473-ddf630c0c0c3"
        fake_item = load_mock_dict(f"v1/groups/{guid}.json")
        ctx = Context(cls.client)
        cls.group = Group(ctx, **fake_item)

    @responses.activate
    def test_members_count(self):
        responses.get(
            "https://connect.example/__api__/v1/groups/6f300623-1e0c-48e6-a473-ddf630c0c0c3/members",
            json=load_mock_dict(f"v1/groups/{self.group['guid']}/members.json"),
        )
        group_members = self.group.members

        assert group_members.count() == 2

    @responses.activate
    def test_members_find(self):
        responses.get(
            "https://connect.example/__api__/v1/groups/6f300623-1e0c-48e6-a473-ddf630c0c0c3/members",
            json=load_mock_dict(f"v1/groups/{self.group['guid']}/members.json"),
        )

        group_users = self.group.members.find()
        assert len(group_users) == 2
        for user in group_users:
            assert isinstance(user, User)
