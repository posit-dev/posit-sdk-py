import requests
import responses

from posit.connect.packages import PackagesMixin
from posit.connect.resources import ResourceParameters
from posit.connect.urls import Url


class TestPackagesMixin:
    def setup_method(self):
        self.url = Url("http://connect.example/__api__")
        self.endpoint = self.url + "v1/content/1/packages"
        self.session = requests.Session()
        self.params = ResourceParameters(self.session, self.url)
        self.mixin = PackagesMixin(self.params, guid="1")

    @responses.activate
    def test_packages(self):
        # mock
        mock_get = responses.get(
            self.endpoint,
            json=[
                {
                    "language": "python",
                    "name": "posit-sdk",
                    "version": "0.5.1.dev3+gd4bba40.d20241016",
                }
            ],
        )

        # call
        packages = self.mixin.packages

        # assert
        assert mock_get.call_count == 1
        assert packages[0] == {
            "language": "python",
            "name": "posit-sdk",
            "version": "0.5.1.dev3+gd4bba40.d20241016",
        }

    @responses.activate
    def test_packages_are_cached(self):
        # mock
        mock_get = responses.get(
            self.endpoint,
            json=[
                {
                    "language": "python",
                    "name": "posit-sdk",
                    "version": "0.5.1.dev3+gd4bba40.d20241016",
                }
            ],
        )

        # call attribute twice, the second call should be cached
        self.mixin.packages
        self.mixin.packages

        # assert called once
        assert mock_get.call_count == 1

    @responses.activate
    def test_packages_count(self):
        responses.get(
            self.endpoint,
            json=[
                {
                    "language": "python",
                    "name": "posit-sdk",
                    "version": "0.5.1.dev3+gd4bba40.d20241016",
                }
            ],
        )

        packages = self.mixin.packages
        count = packages.count(
            {
                "language": "python",
                "name": "posit-sdk",
                "version": "0.5.1.dev3+gd4bba40.d20241016",
            }
        )

        assert count == 1

    @responses.activate
    def test_packages_index(self):
        responses.get(
            self.endpoint,
            json=[
                {
                    "language": "python",
                    "name": "posit-sdk",
                    "version": "0.5.1.dev3+gd4bba40.d20241016",
                }
            ],
        )

        packages = self.mixin.packages
        index = packages.index(
            {
                "language": "python",
                "name": "posit-sdk",
                "version": "0.5.1.dev3+gd4bba40.d20241016",
            }
        )

        assert index == 0

    @responses.activate
    def test_packages_repr(self):
        responses.get(
            self.endpoint,
            json=[
                {
                    "language": "python",
                    "name": "posit-sdk",
                    "version": "0.5.1.dev3+gd4bba40.d20241016",
                }
            ],
        )

        packages = self.mixin.packages
        assert (
            repr(packages)
            == "Packages({'language': 'python', 'name': 'posit-sdk', 'version': '0.5.1.dev3+gd4bba40.d20241016'})"
        )
