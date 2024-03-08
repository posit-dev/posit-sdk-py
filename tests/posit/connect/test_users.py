import pandas as pd
import responses

from posit.connect.client import Client

from .api import load_mock


class TestUsers:
    @responses.activate
    def test_get_users(self):
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
        assert df.shape == (3, 11)
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
        ]
        assert df["username"].to_list() == ["al", "robert", "carlos12"]

        # Test find_one()
        bob = con.users.find_one(lambda u: u["first_name"] == "Bob", page_size=2)
        # Can't isinstance(bob, User) bc inherits TypedDict (cf. #23)
        assert bob["username"] == "robert"

        # Test where find_one() doesn't find any
        assert (
            con.users.find_one(lambda u: u["first_name"] == "Ringo", page_size=2)
            is None
        )

    @responses.activate
    def test_users_get(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json=load_mock("v1/users/20a79ce3-6e87-4522-9faf-be24228800a4.json"),
        )

        con = Client(api_key="12345", url="https://connect.example/")
        assert (
            con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")["username"]
            == "carlos12"
        )
