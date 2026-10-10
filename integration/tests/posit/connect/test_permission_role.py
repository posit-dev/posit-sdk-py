from posit.connect.permissions import PermissionRole


class TestPermissionRole:
    def test_ordering(self):
        assert PermissionRole.viewer < PermissionRole.owner
        assert PermissionRole.owner > PermissionRole.viewer
        assert PermissionRole.viewer == PermissionRole.viewer
        assert PermissionRole.owner == PermissionRole.owner

    def test_from_string(self):
        assert PermissionRole("viewer") == PermissionRole.viewer
        assert PermissionRole("owner") == PermissionRole.owner

    def test_max_min(self):
        assert max(PermissionRole.viewer, PermissionRole.owner) == PermissionRole.owner
        assert min(PermissionRole.viewer, PermissionRole.owner) == PermissionRole.viewer

    def test_comparison_from_permission_data(self):
        """Simulate comparing roles from actual permission dicts."""
        source_role = PermissionRole("owner")
        target_role = PermissionRole("viewer")
        assert source_role > target_role
        stronger = max(source_role, target_role)
        assert stronger == PermissionRole.owner
