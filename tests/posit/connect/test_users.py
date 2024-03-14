import pandas as pd
import pytest
import responses

from requests import HTTPError

from posit.connect.client import Client
from posit.connect.users import User

from .api import load_mock  # type: ignore


class TestUsers:
    @responses.activate
    def test_users_find(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 2, "page_number": 1}
                )
            ],
            json=load_mock("v1/users?page_number=1&page_size=2.json"),
        )
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 2, "page_number": 2}
                )
            ],
            json=load_mock("v1/users?page_number=2&page_size=2.json"),
        )

        con = Client(api_key="12345", url="https://connect.example/")
        all_users = con.users.find(page_size=2)
        assert len(all_users) == 3

        df = pd.DataFrame(all_users)
        assert isinstance(df, pd.DataFrame)
        assert df.shape == (3, 12)
        assert df.columns.to_list() == [
            "guid",
            "email",
            "username",
            "first_name",
            "last_name",
            "user_role",
            "created_time",
            "updated_time",
            "active_time",
            "confirmed",
            "locked",
            "is_locked",
        ]
        assert df.username.to_list() == ["al", "robert", "carlos12"]

    @responses.activate
    def test_users_find_one(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 2, "page_number": 1}
                )
            ],
            json=load_mock("v1/users?page_number=1&page_size=2.json"),
        )
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 2, "page_number": 2}
                )
            ],
            json=load_mock("v1/users?page_number=2&page_size=2.json"),
        )

        con = Client(api_key="12345", url="https://connect.example/")
        c = con.users.find_one(lambda u: u.first_name == "Carlos", page_size=2)
        assert isinstance(c, User)
        assert c.username == "carlos12"

        # Now test that if not found, it returns None
        assert (
            con.users.find_one(lambda u: u.first_name == "Ringo", page_size=2) is None
        )

    @responses.activate
    def test_users_find_one_only_gets_necessary_pages(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 2, "page_number": 1}
                )
            ],
            json=load_mock("v1/users?page_number=1&page_size=2.json"),
        )
        # Make page 2 return an error so we can prove that we're quitting
        # when we find the user
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 2, "page_number": 2}
                )
            ],
            status=500,
        )

        con = Client(api_key="12345", url="https://connect.example/")
        bob = con.users.find_one(lambda u: u.first_name == "Bob", page_size=2)
        assert bob.username == "robert"
        # This errors because we have to go past the first page
        with pytest.raises(HTTPError, match="500 Server Error"):
            con.users.find_one(lambda u: u.first_name == "Carlos", page_size=2)

    @responses.activate
    def test_users_get(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )

        con = Client(api_key="12345", url="https://connect.example/")
        assert (
            con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4").username == "carlos12"
        )
