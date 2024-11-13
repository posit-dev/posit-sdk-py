from email.contentmanager import ContentManager
from unittest.mock import MagicMock, Mock

import pytest
import requests
import responses

from posit.connect.context import Context, requires
from posit.connect.urls import Url


class TestRequires:
    def test_version_unsupported(self):
        class Stub(ContentManager):
            def __init__(self, ctx):
                self._ctx = ctx

            @requires("1.0.0")
            def fail(self):
                pass

        ctx = MagicMock()
        ctx.version = "0.0.0"
        instance = Stub(ctx)

        with pytest.raises(RuntimeError):
            instance.fail()

    def test_version_supported(self):
        class Stub(ContentManager):
            def __init__(self, ctx):
                self._ctx = ctx

            @requires("1.0.0")
            def success(self):
                pass

        ctx = MagicMock()
        ctx.version = "1.0.0"
        instance = Stub(ctx)

        instance.success()

    def test_version_missing(self):
        class Stub(ContentManager):
            def __init__(self, ctx):
                self._ctx = ctx

            @requires("1.0.0")
            def success(self):
                pass

        ctx = MagicMock()
        ctx.version = None
        instance = Stub(ctx)

        instance.success()


class TestContextVersion:
    @responses.activate
    def test_unknown(self):
        responses.get(
            "http://connect.example/__api__/server_settings",
            json={},
        )

        session = requests.Session()
        url = Url("http://connect.example")
        ctx = Context(session, url)

        assert ctx.version is None

    @responses.activate
    def test_known(self):
        responses.get(
            "http://connect.example/__api__/server_settings",
            json={"version": "2024.09.24"},
        )

        session = requests.Session()
        url = Url("http://connect.example")
        ctx = Context(session, url)

        assert ctx.version == "2024.09.24"

    def test_setter(self):
        ctx = Context(Mock(), Mock())
        ctx.version = "2024.09.24"
        assert ctx.version == "2024.09.24"
