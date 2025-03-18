from __future__ import annotations

import pytest

from posit.workbench.external.databricks import (
    POSIT_WORKBENCH_AUTH_TYPE,
    WorkbenchStrategy,
)

try:
    from databricks.sdk.core import Config
except ImportError:
    pytestmark = pytest.mark.skipif(True, reason="requires the Databricks SDK")


class TestPositCredentialsHelpers:
    def test_workbench_strategy(self):
        # default will attempt to load the workbench profile
        with pytest.raises(ValueError, match="profile=workbench"):
            WorkbenchStrategy()

        # providing a Config is allowed
        cs = WorkbenchStrategy(
            config=Config(host="https://databricks.com/workspace", token="token")  # pyright: ignore[reportPossiblyUnboundVariable]
        )
        assert cs.auth_type() == POSIT_WORKBENCH_AUTH_TYPE
        cp = cs()

        # token from the Config is passed through to the auth header
        assert cp() == {"Authorization": "Bearer token"}
