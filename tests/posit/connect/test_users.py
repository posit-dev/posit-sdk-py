import pandas as pd
import pytest
import responses

from requests import HTTPError

from posit.connect.client import Client

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
        assert df.shape == (3, 13)
        assert df.columns.to_list() == [
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
            "guid",
            "session",
            "url",
        ]
        assert df["username"].to_list() == ["al", "robert", "carlos12"]

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
        # Can't isinstance(c, User) bc inherits TypedDict (cf. #23)
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
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert carlos.username == "carlos12"
        assert carlos.first_name == "Carlos"
        assert carlos.created_time == "2019-09-09T15:24:32Z"

    @responses.activate
    def test_users_get_extra_fields(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json={
                "guid": "20a79ce3-6e87-4522-9faf-be24228800a4",
                "username": "carlos12",
                "some_new_field": "some_new_value",
            },
        )

        con = Client(api_key="12345", url="https://connect.example/")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")
        assert carlos.username == "carlos12"
        assert carlos["some_new_field"] == "some_new_value"

    @responses.activate
    def test_user_update(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )
        patch_request = responses.patch(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            match=[responses.matchers.json_params_matcher({"first_name": "Carlitos"})],
        )

        con = Client(api_key="12345", url="https://connect.example/")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")

        assert patch_request.call_count == 0
        assert carlos.first_name == "Carlos"

        carlos.update(first_name="Carlitos")

        assert patch_request.call_count == 1
        assert carlos.first_name == "Carlitos"
        # TODO: test setting the other fields
        # TODO: test invalid field

    @responses.activate
    def test_user_cant_setattr(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )

        con = Client(api_key="12345", url="https://connect.example/")
        carlos = con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")

        with pytest.raises(
            AttributeError,
            match=r"Cannot set attributes: use update\(\) instead",
        ):
            carlos.first_name = "Carlitos"
