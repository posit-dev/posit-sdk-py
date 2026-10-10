import responses
from responses import matchers

from posit.connect.admin import MergeResult, merge_users
from posit.connect.client import Client
from posit.connect.users import User


class TestMergeUsersOwnership:
    @responses.activate
    def test_transfers_ownership(self):
        source_guid = "source-guid"
        target_guid = "target-guid"
        content_guid_1 = "content-guid-1"
        content_guid_2 = "content-guid-2"

        # Resolve users
        responses.get(
            f"https://connect.example/__api__/v1/users/{source_guid}",
            json={"guid": source_guid, "username": "source"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/users/{target_guid}",
            json={"guid": target_guid, "username": "target"},
        )

        # Source owns 2 content items
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[
                {"guid": content_guid_1, "name": "app-1", "owner_guid": source_guid},
                {"guid": content_guid_2, "name": "app-2", "owner_guid": source_guid},
            ],
            match=[matchers.query_param_matcher({"owner_guid": source_guid}, strict_match=False)],
        )

        # Ownership transfer patches
        mock_patch_1 = responses.patch(
            f"https://connect.example/__api__/v1/content/{content_guid_1}",
            json={"guid": content_guid_1, "name": "app-1", "owner_guid": target_guid},
            match=[matchers.json_params_matcher({"owner_guid": target_guid})],
        )
        mock_patch_2 = responses.patch(
            f"https://connect.example/__api__/v1/content/{content_guid_2}",
            json={"guid": content_guid_2, "name": "app-2", "owner_guid": target_guid},
            match=[matchers.json_params_matcher({"owner_guid": target_guid})],
        )

        # Source has no permissions (empty content listing for permission scan)
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[],
        )

        # Lock source
        responses.get(
            "https://connect.example/__api__/v1/user",
            json={"guid": "admin-guid"},
        )
        responses.post(
            f"https://connect.example/__api__/v1/users/{source_guid}/lock",
            match=[matchers.json_params_matcher({"locked": True})],
        )

        c = Client(api_key="12345", url="https://connect.example/")
        result = merge_users(c, source=source_guid, target=target_guid)

        assert mock_patch_1.call_count == 1
        assert mock_patch_2.call_count == 1
        assert set(result.ownership_transferred) == {content_guid_1, content_guid_2}
        assert result.source_locked is True


class TestMergeUsersPermissions:
    @responses.activate
    def test_add_permission(self):
        """Source has viewer permission, target has none — should add."""
        source_guid = "source-guid"
        target_guid = "target-guid"
        content_guid = "content-guid-1"

        responses.get(
            f"https://connect.example/__api__/v1/users/{source_guid}",
            json={"guid": source_guid, "username": "source"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/users/{target_guid}",
            json={"guid": target_guid, "username": "target"},
        )

        # No owned content
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[],
            match=[matchers.query_param_matcher({"owner_guid": source_guid}, strict_match=False)],
        )

        # Source permissions: viewer on content-guid-1
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[{"guid": content_guid, "name": "app-1", "owner_guid": "someone-else"}],
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=[
                {"id": 1, "content_guid": content_guid, "principal_guid": source_guid, "principal_type": "user", "role": "viewer"},
            ],
        )

        # Check target permissions (none)
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json={"guid": content_guid, "name": "app-1", "owner_guid": "someone-else"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=[],
        )

        # Create permission for target
        mock_create = responses.post(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json={"id": 2, "content_guid": content_guid, "principal_guid": target_guid, "principal_type": "user", "role": "viewer"},
            match=[matchers.json_params_matcher({"principal_guid": target_guid, "principal_type": "user", "role": "viewer"})],
        )

        # Destroy source permission
        mock_destroy = responses.delete(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/1",
        )

        # Lock source
        responses.get(
            "https://connect.example/__api__/v1/user",
            json={"guid": "admin-guid"},
        )
        responses.post(
            f"https://connect.example/__api__/v1/users/{source_guid}/lock",
            match=[matchers.json_params_matcher({"locked": True})],
        )

        c = Client(api_key="12345", url="https://connect.example/")
        result = merge_users(c, source=source_guid, target=target_guid)

        assert mock_create.call_count == 1
        assert mock_destroy.call_count == 1
        assert len(result.permissions_added) == 1
        assert result.permissions_added[0]["content_guid"] == content_guid
        assert result.permissions_added[0]["role"] == "viewer"

    @responses.activate
    def test_upgrade_permission(self):
        """Source has owner, target has viewer — should upgrade target."""
        source_guid = "source-guid"
        target_guid = "target-guid"
        content_guid = "content-guid-1"

        responses.get(
            f"https://connect.example/__api__/v1/users/{source_guid}",
            json={"guid": source_guid, "username": "source"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/users/{target_guid}",
            json={"guid": target_guid, "username": "target"},
        )

        # No owned content
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[],
            match=[matchers.query_param_matcher({"owner_guid": source_guid}, strict_match=False)],
        )

        # Source permissions: owner on content
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[{"guid": content_guid, "name": "app-1", "owner_guid": "someone"}],
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=[
                {"id": 1, "content_guid": content_guid, "principal_guid": source_guid, "principal_type": "user", "role": "owner"},
            ],
        )

        # Check target permissions (viewer)
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json={"guid": content_guid, "name": "app-1", "owner_guid": "someone"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=[
                {"id": 2, "content_guid": content_guid, "principal_guid": target_guid, "principal_type": "user", "role": "viewer"},
            ],
        )

        # Upgrade target permission
        mock_upgrade = responses.put(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/2",
            json={"id": 2, "content_guid": content_guid, "principal_guid": target_guid, "principal_type": "user", "role": "owner"},
        )

        # Destroy source permission
        mock_destroy = responses.delete(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/1",
        )

        # Lock source
        responses.get(
            "https://connect.example/__api__/v1/user",
            json={"guid": "admin-guid"},
        )
        responses.post(
            f"https://connect.example/__api__/v1/users/{source_guid}/lock",
            match=[matchers.json_params_matcher({"locked": True})],
        )

        c = Client(api_key="12345", url="https://connect.example/")
        result = merge_users(c, source=source_guid, target=target_guid)

        assert mock_upgrade.call_count == 1
        assert mock_destroy.call_count == 1
        assert len(result.permissions_upgraded) == 1
        assert result.permissions_upgraded[0]["old_role"] == "viewer"
        assert result.permissions_upgraded[0]["new_role"] == "owner"

    @responses.activate
    def test_skip_permission(self):
        """Source has viewer, target has owner — should skip."""
        source_guid = "source-guid"
        target_guid = "target-guid"
        content_guid = "content-guid-1"

        responses.get(
            f"https://connect.example/__api__/v1/users/{source_guid}",
            json={"guid": source_guid, "username": "source"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/users/{target_guid}",
            json={"guid": target_guid, "username": "target"},
        )

        # No owned content
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[],
            match=[matchers.query_param_matcher({"owner_guid": source_guid}, strict_match=False)],
        )

        # Source permissions: viewer
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[{"guid": content_guid, "name": "app-1", "owner_guid": "someone"}],
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=[
                {"id": 1, "content_guid": content_guid, "principal_guid": source_guid, "principal_type": "user", "role": "viewer"},
            ],
        )

        # Target already has owner
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json={"guid": content_guid, "name": "app-1", "owner_guid": "someone"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=[
                {"id": 2, "content_guid": content_guid, "principal_guid": target_guid, "principal_type": "user", "role": "owner"},
            ],
        )

        # Destroy source permission (still removed even when skipped)
        mock_destroy = responses.delete(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions/1",
        )

        # Lock source
        responses.get(
            "https://connect.example/__api__/v1/user",
            json={"guid": "admin-guid"},
        )
        responses.post(
            f"https://connect.example/__api__/v1/users/{source_guid}/lock",
            match=[matchers.json_params_matcher({"locked": True})],
        )

        c = Client(api_key="12345", url="https://connect.example/")
        result = merge_users(c, source=source_guid, target=target_guid)

        assert mock_destroy.call_count == 1
        assert len(result.permissions_skipped) == 1
        assert result.permissions_skipped[0]["reason"] == "target already has role 'owner'"


class TestMergeUsersDryRun:
    @responses.activate
    def test_no_mutations(self):
        """In dry_run mode, no PUT/POST/DELETE/PATCH calls should be made."""
        source_guid = "source-guid"
        target_guid = "target-guid"
        content_guid = "content-guid-1"

        responses.get(
            f"https://connect.example/__api__/v1/users/{source_guid}",
            json={"guid": source_guid, "username": "source"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/users/{target_guid}",
            json={"guid": target_guid, "username": "target"},
        )

        # Source owns 1 content item
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[{"guid": content_guid, "name": "app-1", "owner_guid": source_guid}],
            match=[matchers.query_param_matcher({"owner_guid": source_guid}, strict_match=False)],
        )

        # Source has viewer permission on that content
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[{"guid": content_guid, "name": "app-1", "owner_guid": source_guid}],
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=[
                {"id": 1, "content_guid": content_guid, "principal_guid": source_guid, "principal_type": "user", "role": "viewer"},
            ],
        )

        # Target has no permissions
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}",
            json={"guid": content_guid, "name": "app-1", "owner_guid": source_guid},
        )
        responses.get(
            f"https://connect.example/__api__/v1/content/{content_guid}/permissions",
            json=[],
        )

        c = Client(api_key="12345", url="https://connect.example/")
        result = merge_users(c, source=source_guid, target=target_guid, dry_run=True)

        # Verify planned actions
        assert len(result.ownership_transferred) == 1
        assert len(result.permissions_added) == 1
        assert result.source_locked is True

        # Verify no mutation calls were made
        for call in responses.calls:
            assert call.request.method == "GET", (
                f"Expected only GET calls in dry_run, got {call.request.method} to {call.request.url}"
            )


class TestMergeUsersLockSource:
    @responses.activate
    def test_lock_source_false(self):
        """When lock_source=False, source should not be locked."""
        source_guid = "source-guid"
        target_guid = "target-guid"

        responses.get(
            f"https://connect.example/__api__/v1/users/{source_guid}",
            json={"guid": source_guid, "username": "source"},
        )
        responses.get(
            f"https://connect.example/__api__/v1/users/{target_guid}",
            json={"guid": target_guid, "username": "target"},
        )

        # No owned content
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[],
            match=[matchers.query_param_matcher({"owner_guid": source_guid}, strict_match=False)],
        )

        # No permissions
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[],
        )

        c = Client(api_key="12345", url="https://connect.example/")
        result = merge_users(c, source=source_guid, target=target_guid, lock_source=False)

        assert result.source_locked is False


class TestMergeUsersWithUserObjects:
    @responses.activate
    def test_accepts_user_objects(self):
        """merge_users should accept User objects directly, not just GUIDs."""
        source_guid = "source-guid"
        target_guid = "target-guid"

        # No owned content
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[],
            match=[matchers.query_param_matcher({"owner_guid": source_guid}, strict_match=False)],
        )

        # No permissions
        responses.get(
            "https://connect.example/__api__/v1/content",
            json=[],
        )

        # Lock source
        responses.get(
            "https://connect.example/__api__/v1/user",
            json={"guid": "admin-guid"},
        )
        responses.post(
            f"https://connect.example/__api__/v1/users/{source_guid}/lock",
            match=[matchers.json_params_matcher({"locked": True})],
        )

        c = Client(api_key="12345", url="https://connect.example/")
        source = User(c._ctx, guid=source_guid, username="source")
        target = User(c._ctx, guid=target_guid, username="target")

        result = merge_users(c, source=source, target=target)

        assert result.source_locked is True
        assert result.errors == []
