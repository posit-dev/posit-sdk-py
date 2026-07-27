from __future__ import annotations

import pytest

from posit import connect


@pytest.fixture(scope="class", autouse=True)
def clear_default_integration():
    """Delete Connect's auto-created default integration before each class.

    Automatic since Connect 2025.05.0:
    https://docs.posit.co/connect/news/#posit-connect-2025.05.0
    """
    client = connect.Client()
    for integration in client.oauth.integrations.find():
        integration.delete()
