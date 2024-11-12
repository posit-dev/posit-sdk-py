import pytest

from posit.connect._api import ReadOnlyDict


class TestApiEndpoint:
    def test_read_only(self):
        obj = ReadOnlyDict({})

        assert len(obj) == 0

        assert obj.get("foo", "bar") == "bar"

        with pytest.raises(NotImplementedError):
            obj["foo"] = "baz"

        eq_obj = ReadOnlyDict({"foo": "bar", "a": 1})
        assert eq_obj == {"foo": "bar", "a": 1}
