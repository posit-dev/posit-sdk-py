import pytest
import responses

from pandas import DataFrame
from unittest.mock import patch

from .client import Client
from .users import Users


@pytest.fixture
def mock_config():
    with patch("posit.connect.users.Config") as mock:
        yield mock.return_value


@pytest.fixture
def mock_session():
    with patch("posit.connect.users.Session") as mock:
        yield mock.return_value


class TestUsers:
    def test_init(self, mock_config, mock_session):
        with pytest.raises(ValueError):
            Users(mock_config, mock_session, page_size=9999)

    @responses.activate
    def test_get_users(self):
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 2, "page_number": 1}
                )
            ],
            json={
                "results": [
                    {
                        "email": "alice@connect.example",
                        "username": "al",
                        "first_name": "Alice",
                        "last_name": "User",
                        "user_role": "publisher",
                        "created_time": "2017-08-08T15:24:32Z",
                        "updated_time": "2023-03-02T20:25:06Z",
                        "active_time": "2018-05-09T16:58:45Z",
                        "confirmed": True,
                        "locked": False,
                        "guid": "a01792e3-2e67-402e-99af-be04a48da074",
                    },
                    {
                        "email": "bob@connect.example",
                        "username": "robert",
                        "first_name": "Bob",
                        "last_name": "Loblaw",
                        "user_role": "publisher",
                        "created_time": "2023-01-06T19:47:29Z",
                        "updated_time": "2023-05-05T19:08:45Z",
                        "active_time": "2023-05-05T20:29:11Z",
                        "confirmed": True,
                        "locked": False,
                        "guid": "87c12c08-11cd-4de1-8da3-12a7579c4998",
                    },
                ],
                "current_page": 1,
                "total": 3,
            },
        )
        responses.get(
            "https://connect.example/__api__/v1/users",
            match=[
                responses.matchers.query_param_matcher(
                    {"page_size": 2, "page_number": 2}
                )
            ],
            json={
                "results": [
                    {
                        "email": "carlos@connect.example",
                        "username": "carlos12",
                        "first_name": "Carlos",
                        "last_name": "User",
                        "user_role": "publisher",
                        "created_time": "2019-09-09T15:24:32Z",
                        "updated_time": "2022-03-02T20:25:06Z",
                        "active_time": "2020-05-11T16:58:45Z",
                        "confirmed": True,
                        "locked": False,
                        "guid": "20a79ce3-6e87-4522-9faf-be24228800a4",
                    },
                ],
                "current_page": 2,
                "total": 3,
            },
        )

        con = Client(api_key="12345", url="https://connect.example/")
        # TODO(#48): page_size should go with find(), can't pass it to client.users
        u = con.users
        u.page_size = 2
        # TODO(#47): Add __len__ method to Users
        assert len(u.find().data) == 3

        # Test to_pandas()
        df = u.to_pandas()
        assert isinstance(df, DataFrame)
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
        bob = u.find_one(lambda u: u["first_name"] == "Bob")
        # Can't isinstance(bob, User) bc inherits TypedDict (cf. #23)
        assert bob["username"] == "robert"

    @responses.activate
    def test_users_get(self):
        responses.get(
            "https://connect.example/__api__/v1/users/20a79ce3-6e87-4522-9faf-be24228800a4",
            json={
                "email": "carlos@connect.example",
                "username": "carlos12",
                "first_name": "Carlos",
                "last_name": "User",
                "user_role": "publisher",
                "created_time": "2019-09-09T15:24:32Z",
                "updated_time": "2022-03-02T20:25:06Z",
                "active_time": "2020-05-11T16:58:45Z",
                "confirmed": True,
                "locked": False,
                "guid": "20a79ce3-6e87-4522-9faf-be24228800a4",
            },
        )

        con = Client(api_key="12345", url="https://connect.example/")
        assert (
            con.users.get("20a79ce3-6e87-4522-9faf-be24228800a4")["username"]
            == "carlos12"
        )
