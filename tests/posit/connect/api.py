import json

from pathlib import Path


def load_mock(path: str) -> dict:
    """
    Read a JSON object from `path`
    """
    return json.loads((Path(__file__).parent / "__api__" / path).read_text())
