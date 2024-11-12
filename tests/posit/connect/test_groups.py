from unittest import mock
from unittest.mock import Mock

from posit.connect.groups import Group

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
