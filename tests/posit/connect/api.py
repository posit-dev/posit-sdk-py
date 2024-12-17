from pathlib import Path

import pyjson5 as json


def load_mock(path: str):
    """
    Load mock data from a file.

    Reads a JSON or JSONC (JSON with Comments) file and returns the parsed data.

    It's primarily used for loading mock data for tests.

    The file names for mock data should match the query path that they represent.

    Parameters
    ----------
    path : str
        The relative path to the JSONC file.

    Returns
    -------
    dict | list
        The parsed data from the JSONC file.

    Examples
    --------
    >>> data = load_mock("v1/example.json")
    >>> data = load_mock("v1/example.jsonc")
    """
    return json.loads((Path(__file__).parent / "__api__" / path).read_text())


def load_mock_dict(path: str) -> dict:
    result = load_mock(path)
    assert isinstance(result, dict)
    return result


def load_mock_list(path: str) -> list:
    result = load_mock(path)
    assert isinstance(result, list)
    return result


def get_path(path: str) -> Path:
    return Path(__file__).parent / "__api__" / path
