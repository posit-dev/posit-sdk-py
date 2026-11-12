# The SDK's response TypedDicts are total=False; these tests index keys a live server returns.
# pyright: reportTypedDictNotRequiredAccess=false

from posit.workbench import admin

from . import CLUSTER, WORKBENCH_USER, WORKBENCH_VERSION


class TestServer:
    @classmethod
    def setup_class(cls):
        cls.client = admin.Client()

    def test_version(self):
        # `version` returns its payload bare, not wrapped in {"result": ...}.
        info = self.client.server.version()
        assert info["version"]["major"] == str(WORKBENCH_VERSION.major)
        assert isinstance(info["features"], list)

    def test_client_version(self):
        assert self.client.version["major"] == str(WORKBENCH_VERSION.major)
        assert self.client._ctx.version == str(WORKBENCH_VERSION)


class TestUsers:
    @classmethod
    def setup_class(cls):
        cls.client = admin.Client()

    def test_list_includes_token_user_as_admin(self):
        users = {user["username"]: user for user in self.client.users.list()}
        assert WORKBENCH_USER in users
        assert users[WORKBENCH_USER]["isAdmin"] is True


class TestComputeEnvs:
    @classmethod
    def setup_class(cls):
        cls.client = admin.Client()

    def test_list_includes_local_cluster(self):
        envs = self.client.compute_envs.list()
        clusters = {cluster["name"]: cluster for cluster in envs["clusters"]}
        assert CLUSTER in clusters
        assert clusters[CLUSTER]["type"] == "Local"

    def test_list_includes_workbenches(self):
        envs = self.client.compute_envs.list()
        assert "RStudio" in envs["workbenches"]
