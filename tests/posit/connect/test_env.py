import pytest
import responses

from responses import matchers

from posit.connect import Client

from .api import load_mock  # type: ignore


@responses.activate
def test__delitem__():
    # data
    guid = "f2f37341-e21d-3d80-c698-a935ad614066"

    # behavior
    mock_get = responses.get(
        f"https://connect.example.com/__api__/v1/content/{guid}",
        json=load_mock(f"v1/content/{guid}.json"),
    )

    mock_patch = responses.patch(
        f"https://connect.example.com/__api__/v1/content/{guid}/environment",
        json=[],
        match=[
            matchers.json_params_matcher(
                [
                    {
                        "name": "TEST",
                        "value": None,
                    }
                ]
            )
        ],
    )

    # setup
    c = Client("https://connect.example.com", "12345")
    content = c.content.get(guid)

    # invoke
    del content.environment_variables["TEST"]

    # assert
    assert mock_get.call_count == 1
    assert mock_patch.call_count == 1


@responses.activate
def test__setitem__():
    # data
    guid = "f2f37341-e21d-3d80-c698-a935ad614066"

    # behavior
    mock_get = responses.get(
        f"https://connect.example.com/__api__/v1/content/{guid}",
        json=load_mock(f"v1/content/{guid}.json"),
    )

    mock_patch = responses.patch(
        f"https://connect.example.com/__api__/v1/content/{guid}/environment",
        json=["TEST"],
        match=[
            matchers.json_params_matcher(
                [
                    {
                        "name": "TEST",
                        "value": "TEST",
                    }
                ]
            )
        ],
    )

    # setup
    c = Client("https://connect.example.com", "12345")
    content = c.content.get(guid)

    # invoke
    content.environment_variables["TEST"] = "TEST"

    # assert
    assert mock_get.call_count == 1
    assert mock_patch.call_count == 1


@responses.activate
def test_clear():
    # data
    guid = "f2f37341-e21d-3d80-c698-a935ad614066"

    # behavior
    mock_get = responses.get(
        f"https://connect.example.com/__api__/v1/content/{guid}",
        json=load_mock(f"v1/content/{guid}.json"),
    )

    mock_put = responses.put(
        f"https://connect.example.com/__api__/v1/content/{guid}/environment",
        json=[],
        match=[matchers.json_params_matcher([])],
    )

    # setup
    c = Client("https://connect.example.com", "12345")
    content = c.content.get(guid)

    # invoke
    content.environment_variables.clear()

    # assert
    assert mock_get.call_count == 1
    assert mock_put.call_count == 1


@responses.activate
def test_create():
    # data
    guid = "f2f37341-e21d-3d80-c698-a935ad614066"

    # behavior
    mock_get = responses.get(
        f"https://connect.example.com/__api__/v1/content/{guid}",
        json=load_mock(f"v1/content/{guid}.json"),
    )

    mock_patch = responses.patch(
        f"https://connect.example.com/__api__/v1/content/{guid}/environment",
        json=["TEST"],
        match=[
            matchers.json_params_matcher(
                [
                    {
                        "name": "TEST",
                        "value": "TEST",
                    }
                ]
            )
        ],
    )

    # setup
    c = Client("https://connect.example.com", "12345")
    content = c.content.get(guid)

    # invoke
    content.environment_variables.create("TEST", "TEST")

    # assert
    assert mock_get.call_count == 1
    assert mock_patch.call_count == 1


@responses.activate
def test_delete():
    # data
    guid = "f2f37341-e21d-3d80-c698-a935ad614066"

    # behavior
    mock_get = responses.get(
        f"https://connect.example.com/__api__/v1/content/{guid}",
        json=load_mock(f"v1/content/{guid}.json"),
    )

    mock_patch = responses.patch(
        f"https://connect.example.com/__api__/v1/content/{guid}/environment",
        json=[],
        match=[
            matchers.json_params_matcher(
                [
                    {
                        "name": "TEST",
                        "value": None,
                    }
                ]
            )
        ],
    )

    # setup
    c = Client("https://connect.example.com", "12345")
    content = c.content.get(guid)

    # invoke
    content.environment_variables.delete("TEST")

    # assert
    assert mock_get.call_count == 1
    assert mock_patch.call_count == 1


@responses.activate
def test_find():
    # data
    guid = "f2f37341-e21d-3d80-c698-a935ad614066"

    # behavior
    mock_get_content = responses.get(
        f"https://connect.example.com/__api__/v1/content/{guid}",
        json=load_mock(f"v1/content/{guid}.json"),
    )

    mock_get_environment = responses.get(
        f"https://connect.example.com/__api__/v1/content/{guid}/environment",
        json=["TEST"],
    )

    # setup
    c = Client("https://connect.example.com", "12345")
    content = c.content.get(guid)

    # invoke
    vars = content.environment_variables.find()

    # assert
    assert vars == ["TEST"]
    assert mock_get_content.call_count == 1
    assert mock_get_environment.call_count == 1


class TestUpdate:
    @responses.activate
    def test(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        mock_patch = responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}/environment",
            json=load_mock(f"v1/content/{guid}.json"),
            match=[
                matchers.json_params_matcher(
                    [
                        {
                            "name": "TEST",
                            "value": "TEST",
                        }
                    ]
                )
            ],
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        content.environment_variables.update(TEST="TEST")

        # assert
        assert mock_get.call_count == 1
        assert mock_patch.call_count == 1

    @responses.activate
    def test_other_is_mutable_mapping(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        mock_patch = responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}/environment",
            json=load_mock(f"v1/content/{guid}.json"),
            match=[
                matchers.json_params_matcher(
                    [
                        {
                            "name": "TEST",
                            "value": "TEST",
                        }
                    ]
                )
            ],
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        content.environment_variables.update({"TEST": "TEST"})

        # assert
        assert mock_get.call_count == 1
        assert mock_patch.call_count == 1

    @responses.activate
    def test_other_is_iterable(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        mock_patch = responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}/environment",
            json=load_mock(f"v1/content/{guid}.json"),
            match=[
                matchers.json_params_matcher(
                    [
                        {
                            "name": "TEST",
                            "value": "TEST",
                        }
                    ]
                )
            ],
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        content.environment_variables.update([("TEST", "TEST")])

        # assert
        assert mock_get.call_count == 1
        assert mock_patch.call_count == 1

    @responses.activate
    def test_other_is_iterable_of_something_else(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        mock_patch = responses.patch(
            f"https://connect.example.com/__api__/v1/content/{guid}/environment",
            json=load_mock(f"v1/content/{guid}.json"),
            match=[
                matchers.json_params_matcher(
                    [
                        {
                            "name": "TEST",
                            "value": "TEST",
                        }
                    ]
                )
            ],
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        with pytest.raises(TypeError):
            content.environment_variables.update([0, 1, 2, 3, 4, 5])

    @responses.activate
    def test_other_is_str(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        with pytest.raises(TypeError):
            content.environment_variables.update("TEST")

    @responses.activate
    def test_other_is_bytes(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        with pytest.raises(TypeError):
            content.environment_variables.update(b"TEST")

    @responses.activate
    def test_other_is_something_else(self):
        # data
        guid = "f2f37341-e21d-3d80-c698-a935ad614066"

        # behavior
        mock_get = responses.get(
            f"https://connect.example.com/__api__/v1/content/{guid}",
            json=load_mock(f"v1/content/{guid}.json"),
        )

        # setup
        c = Client("https://connect.example.com", "12345")
        content = c.content.get(guid)

        # invoke
        with pytest.raises(TypeError):
            content.environment_variables.update(0)
