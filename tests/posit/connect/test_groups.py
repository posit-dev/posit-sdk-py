from unittest.mock import Mock

import pytest
import requests
import responses


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
