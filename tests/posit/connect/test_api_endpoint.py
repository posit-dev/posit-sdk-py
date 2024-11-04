import pytest
import requests

from posit.connect._api import ApiDictEndpoint, ReadOnlyDict
from posit.connect.context import Context
from posit.connect.urls import Url


class TestApiEndpoint:
    def test_read_only(self):
        obj = ReadOnlyDict({})

        assert len(obj) == 0

        assert obj.get("foo", "bar") == "bar"

        with pytest.raises(AttributeError):
            obj["foo"] = "baz"

        obj._set_attrs(foo="qux", a="b")
        assert len(obj) == 2
        assert obj["foo"] == "qux"
        assert obj["a"] == "b"

    def test_api_dict_endpoint(self):
        session = requests.Session()
        ctx = Context(session, Url("http://connect.example"))

        end = ApiDictEndpoint(ctx=ctx, path="/some/sub/path", attrs={"uid_key": "guid"})
