from __future__ import annotations

import os

from packaging.version import parse

from posit.workbench import admin

client = admin.Client()
version = client.version
assert version
WORKBENCH_VERSION = parse(f"{version['major']}.{version['minor']}.{version.get('patch', '0')}")

# The user the API token was minted for (with-workbench's --user, default "testuser").
WORKBENCH_USER = os.environ.get("WORKBENCH_USER", "testuser")

CLUSTER = "Local"

# Tags every job launched by these tests, so teardown can find and stop leftovers.
TAG = "posit-sdk-integration"


def _resource_profile() -> str | None:
    # The stock image's Local cluster defines resource profiles and rejects jobs that don't
    # name one ("Invalid resource profile for user").
    for cluster in client.compute_envs.list().get("clusters") or []:
        if cluster.get("name") == CLUSTER:
            profiles = cluster.get("resourceProfiles") or []
            return profiles[0]["name"] if profiles else None
    return None


RESOURCE_PROFILE = _resource_profile()
