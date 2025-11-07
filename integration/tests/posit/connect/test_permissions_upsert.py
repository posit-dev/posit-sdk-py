"""Integration tests for permissions upsert behavior (Connect 2025.11.0+).

This test module verifies the behavior change in POST /v1/content/{guid}/permissions
from create-only to upsert functionality.

Old behavior (< 2025.11.0): POST returns 409 when permission already exists
New behavior (>= 2025.11.0): POST performs upsert (201 on create, 200 on update)
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import pytest
from packaging import version

from posit import connect
from posit.connect.errors import ClientError

from . import CONNECT_VERSION


class TestPermissionsUpsert:
    """Test the upsert behavior of the permissions endpoint."""

    @classmethod
    def setup_class(cls):
        """Set up test fixtures."""
        cls.client = connect.Client()

        # Use timestamp to ensure unique names
        timestamp = int(time.time())
        cls.content = cls.client.content.create(name=f"test-permissions-upsert-{timestamp}")

        # Create test users and groups for permission testing
        cls.user = cls.client.users.create(
            username=f"permission_upsert_user_{timestamp}",
            email=f"permission_upsert_user_{timestamp}@example.com",
            password="s3cur3p@ssword",
        )
        cls.group = cls.client.groups.create(name=f"PermissionUpsertGroup_{timestamp}")

    @classmethod
    def teardown_class(cls):
        """Clean up test fixtures."""
        cls.content.delete()
        cls.group.delete()

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_create_permission_returns_201(self):
        """Test that creating a new permission returns HTTP 201."""
        # Create a new user permission using the low-level API to check status code
        response = self.client._ctx.client.post(
            f"v1/content/{self.content['guid']}/permissions",
            json={
                "principal_guid": self.user["guid"],
                "principal_type": "user",
                "role": "viewer",
            },
        )

        assert response.status_code == 201, "New permission should return 201 Created"
        permission = response.json()
        assert permission["principal_guid"] == self.user["guid"]
        assert permission["role"] == "viewer"

        # Clean up
        self.content.permissions.destroy(self.user)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_duplicate_permission_returns_200(self):
        """Test that creating a duplicate permission returns HTTP 200 (no-op)."""
        # Create initial permission
        self.content.permissions.create(self.user, role="viewer")

        # Attempt to create the same permission again
        response = self.client._ctx.client.post(
            f"v1/content/{self.content['guid']}/permissions",
            json={
                "principal_guid": self.user["guid"],
                "principal_type": "user",
                "role": "viewer",
            },
        )

        assert response.status_code == 200, "Duplicate permission should return 200 OK"
        permission = response.json()
        assert permission["principal_guid"] == self.user["guid"]
        assert permission["role"] == "viewer"

        # Clean up
        self.content.permissions.destroy(self.user)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_update_permission_role_returns_200(self):
        """Test that updating an existing permission role returns HTTP 200."""
        # Create initial permission with viewer role
        self.content.permissions.create(self.group, role="viewer")

        # Update to owner role using create (which is now upsert)
        # Using group instead of user because groups can have owner role
        response = self.client._ctx.client.post(
            f"v1/content/{self.content['guid']}/permissions",
            json={
                "principal_guid": self.group["guid"],
                "principal_type": "group",
                "role": "owner",
            },
        )

        assert response.status_code == 200, "Permission update should return 200 OK"
        permission = response.json()
        assert permission["principal_guid"] == self.group["guid"]
        assert permission["role"] == "owner", "Role should be updated to owner"

        # Verify the permission was updated, not duplicated
        permissions = self.content.permissions.find(principal_guid=self.group["guid"])
        assert len(permissions) == 1, "Should only have one permission for this group"
        assert permissions[0]["role"] == "owner"

        # Clean up
        self.content.permissions.destroy(self.group)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_group_permission_upsert(self):
        """Test that group permissions also support upsert behavior."""
        # Create initial group permission
        self.content.permissions.create(self.group, role="viewer")

        # Update the group permission
        response = self.client._ctx.client.post(
            f"v1/content/{self.content['guid']}/permissions",
            json={
                "principal_guid": self.group["guid"],
                "principal_type": "group",
                "role": "owner",
            },
        )

        assert response.status_code == 200, "Group permission update should return 200 OK"
        permission = response.json()
        assert permission["principal_guid"] == self.group["guid"]
        assert permission["role"] == "owner"

        # Verify only one permission exists
        permissions = self.content.permissions.find(principal_guid=self.group["guid"])
        assert len(permissions) == 1, "Should only have one permission for this group"

        # Clean up
        self.content.permissions.destroy(self.group)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_high_level_create_method_with_upsert(self):
        """Test that the high-level create() method works correctly with upsert."""
        # Create permission using high-level API
        # Note: Only testing with viewer role since regular users can't be owners
        perm1 = self.content.permissions.create(self.user, role="viewer")
        assert perm1["role"] == "viewer"

        # Call create again with same user and same role
        # This should perform a no-op upsert (not create a duplicate)
        perm2 = self.content.permissions.create(self.user, role="viewer")
        assert perm2["role"] == "viewer"

        # Verify we have only one permission
        all_permissions = self.content.permissions.find()
        user_permissions = [p for p in all_permissions if p["principal_guid"] == self.user["guid"]]
        assert len(user_permissions) == 1, "Should only have one permission after upsert"
        assert user_permissions[0]["role"] == "viewer"

        # Clean up
        self.content.permissions.destroy(self.user)

    @pytest.mark.skipif(
        CONNECT_VERSION >= version.parse("2025.11.0-dev"),
        reason="Test old behavior (< 2025.11.0) - expects 409 on duplicate",
    )
    def test_old_behavior_duplicate_returns_409(self):
        """Test that old versions return 409 on duplicate permission creation."""
        # Create initial permission
        self.content.permissions.create(self.user, role="viewer")

        # Attempt to create duplicate should raise a ClientError with 409
        with pytest.raises(ClientError) as exc_info:
            self.client._ctx.client.post(
                f"v1/content/{self.content['guid']}/permissions",
                json={
                    "principal_guid": self.user["guid"],
                    "principal_type": "user",
                    "role": "viewer",
                },
            )

        assert exc_info.value.http_status == 409, "Old behavior should return 409 Conflict"
        assert exc_info.value.error_code == 154, "Should be duplicate user permission error"
        assert "already in the content permission list" in exc_info.value.error_message

        # Clean up
        self.content.permissions.destroy(self.user)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_idempotent_permission_creation(self):
        """Test that calling create multiple times is idempotent with upsert."""
        # This is a common pattern - add permissions in a loop
        principals = [self.user, self.group]
        role = "viewer"

        # First pass - create permissions
        for principal in principals:
            self.content.permissions.create(principal, role=role)

        # Second pass - should not fail, just no-op or update
        for principal in principals:
            self.content.permissions.create(principal, role=role)

        # Verify we only have two permissions (one per principal)
        all_permissions = self.content.permissions.find()
        assert len(all_permissions) == 2

        # Clean up
        self.content.permissions.destroy(self.user)
        self.content.permissions.destroy(self.group)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_concurrent_permission_creates(self):
        """Test that concurrent creates of the same permission are handled correctly.

        This tests for race conditions in the transaction handling.
        Multiple threads try to create the same permission simultaneously.
        Expected: Only one permission should exist, no duplicates, no errors.
        """
        num_concurrent_requests = 10

        def create_permission(thread_id: int):
            """Create a permission in a thread."""
            try:
                result = self.content.permissions.create(
                    self.user,
                    role="viewer",
                )
                return {"thread_id": thread_id, "success": True, "result": result, "error": None}
            except Exception as e:
                return {"thread_id": thread_id, "success": False, "result": None, "error": str(e)}

        # Execute concurrent creates
        results = []
        with ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
            futures = [
                executor.submit(create_permission, i) for i in range(num_concurrent_requests)
            ]
            for future in as_completed(futures):
                results.append(future.result())

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        print(f"\nConcurrent creates - Successful: {len(successful)}, Failed: {len(failed)}")

        # All requests should succeed (upsert behavior)
        assert len(successful) == num_concurrent_requests, (
            f"Expected all {num_concurrent_requests} requests to succeed, "
            f"but {len(failed)} failed: {failed}"
        )

        # Verify only ONE permission exists (no duplicates)
        permissions = self.content.permissions.find(principal_guid=self.user["guid"])
        assert len(permissions) == 1, (
            f"Expected exactly 1 permission, but found {len(permissions)}. "
            f"This indicates a race condition created duplicate records!"
        )

        # Clean up
        self.content.permissions.destroy(self.user)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_concurrent_permission_updates(self):
        """Test that concurrent updates to the same permission are handled correctly.

        This tests for lost updates and inconsistent state.
        Multiple threads try to update the same permission with different roles.
        Expected: Only one permission exists, final role is deterministic or acceptable.
        """
        # Create initial permission
        self.content.permissions.create(self.user, role="viewer")

        num_concurrent_requests = 10

        def update_permission(thread_id: int):
            """Update permission - alternating between viewer and viewer."""
            try:
                # All threads try to set to viewer (testing concurrent no-op updates)
                result = self.content.permissions.create(
                    self.user,
                    role="viewer",
                )
                return {"thread_id": thread_id, "success": True, "result": result, "error": None}
            except Exception as e:
                return {"thread_id": thread_id, "success": False, "result": None, "error": str(e)}

        # Execute concurrent updates
        results = []
        with ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
            futures = [
                executor.submit(update_permission, i) for i in range(num_concurrent_requests)
            ]
            for future in as_completed(futures):
                results.append(future.result())

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        print(f"\nConcurrent updates - Successful: {len(successful)}, Failed: {len(failed)}")

        # All requests should succeed
        assert len(successful) == num_concurrent_requests, (
            f"Expected all {num_concurrent_requests} requests to succeed, "
            f"but {len(failed)} failed: {failed}"
        )

        # Verify still only ONE permission exists
        permissions = self.content.permissions.find(principal_guid=self.user["guid"])
        assert len(permissions) == 1, (
            f"Expected exactly 1 permission after concurrent updates, but found {len(permissions)}"
        )

        # Verify final state is correct
        assert permissions[0]["role"] == "viewer"

        # Clean up
        self.content.permissions.destroy(self.user)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_concurrent_conflicting_updates(self):
        """Test concurrent updates with DIFFERENT target values.

        This is the critical test for detecting lost updates.
        Multiple threads try to update the same group permission to different roles.
        This tests if the transaction handling properly serializes updates.
        """
        # Create initial group permission with viewer role
        self.content.permissions.create(self.group, role="viewer")

        num_threads = 20
        # Half try to set to "viewer", half try to set to "owner"

        def update_permission(thread_id: int, target_role: str):
            """Update permission to a specific role."""
            try:
                result = self.content.permissions.create(
                    self.group,
                    role=target_role,
                )
                return {
                    "thread_id": thread_id,
                    "target_role": target_role,
                    "success": True,
                    "result_role": result.get("role"),
                    "error": None,
                }
            except Exception as e:
                return {
                    "thread_id": thread_id,
                    "target_role": target_role,
                    "success": False,
                    "result_role": None,
                    "error": str(e),
                }

        # Execute concurrent conflicting updates
        results = []
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = []
            for i in range(num_threads):
                # Alternate between viewer and owner
                target_role = "viewer" if i % 2 == 0 else "owner"
                futures.append(executor.submit(update_permission, i, target_role))

            for future in as_completed(futures):
                results.append(future.result())

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]
        viewer_attempts = [r for r in results if r["target_role"] == "viewer"]
        owner_attempts = [r for r in results if r["target_role"] == "owner"]

        print("\nConcurrent conflicting updates:")
        print(f"  Total threads: {num_threads}")
        print(f"  Viewer update attempts: {len(viewer_attempts)}")
        print(f"  Owner update attempts: {len(owner_attempts)}")
        print(f"  Successful: {len(successful)}, Failed: {len(failed)}")

        # All requests should succeed (upsert behavior)
        assert len(successful) == num_threads, (
            f"Expected all {num_threads} requests to succeed, but {len(failed)} failed: {failed}"
        )

        # Critical check: Verify only ONE permission exists
        permissions = self.content.permissions.find(principal_guid=self.group["guid"])
        assert len(permissions) == 1, (
            f"Expected exactly 1 permission after conflicting updates, "
            f"but found {len(permissions)}. This indicates a race condition!"
        )

        # Final role should be either "viewer" or "owner" (last-write-wins is acceptable)
        final_role = permissions[0]["role"]
        assert final_role in ["viewer", "owner"], (
            f"Final role is '{final_role}' which is neither 'viewer' nor 'owner'. "
            f"This indicates data corruption!"
        )

        print(f"  Final state: 1 permission with role='{final_role}'")
        print("  Result: Last-write-wins behavior (acceptable)")

        # Clean up
        self.content.permissions.destroy(self.group)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_concurrent_mixed_operations(self):
        """Test concurrent creates and deletes of the same permission.

        This is the most challenging scenario - some threads creating/updating
        while others are deleting. Tests for deadlocks and consistency.
        """
        num_create_threads = 5
        num_delete_threads = 3
        total_threads = num_create_threads + num_delete_threads

        def create_permission(thread_id: int):
            """Create/update a permission."""
            try:
                time.sleep(0.01 * thread_id)  # Stagger slightly
                result = self.content.permissions.create(
                    self.user,
                    role="viewer",
                )
                return {
                    "thread_id": thread_id,
                    "operation": "create",
                    "success": True,
                    "result": result,
                    "error": None,
                }
            except Exception as e:
                return {
                    "thread_id": thread_id,
                    "operation": "create",
                    "success": False,
                    "result": None,
                    "error": str(e),
                }

        def delete_permission(thread_id: int):
            """Try to delete the permission."""
            try:
                time.sleep(0.01 * thread_id)  # Stagger slightly
                # Find and delete
                perms = self.content.permissions.find(principal_guid=self.user["guid"])
                if perms:
                    self.content.permissions.destroy(perms[0])
                    return {
                        "thread_id": thread_id,
                        "operation": "delete",
                        "success": True,
                        "result": None,
                        "error": None,
                    }
                else:
                    return {
                        "thread_id": thread_id,
                        "operation": "delete",
                        "success": True,
                        "result": "no_permission_found",
                        "error": None,
                    }
            except Exception as e:
                # Delete may fail if permission doesn't exist - that's ok
                return {
                    "thread_id": thread_id,
                    "operation": "delete",
                    "success": False,
                    "result": None,
                    "error": str(e),
                }

        # Execute mixed concurrent operations
        results: List = []
        with ThreadPoolExecutor(max_workers=total_threads) as executor:
            futures = []

            # Submit create operations
            for i in range(num_create_threads):
                futures.append(executor.submit(create_permission, i))

            # Submit delete operations
            for i in range(num_delete_threads):
                futures.append(executor.submit(delete_permission, i + num_create_threads))

            for future in as_completed(futures):
                results.append(future.result())

        # Analyze results
        creates = [r for r in results if r["operation"] == "create"]
        deletes = [r for r in results if r["operation"] == "delete"]

        create_success = [r for r in creates if r["success"]]
        create_failed = [r for r in creates if not r["success"]]
        delete_success = [r for r in deletes if r["success"]]
        delete_failed = [r for r in deletes if not r["success"]]

        print("\nConcurrent mixed operations:")
        print(f"  Creates - Success: {len(create_success)}, Failed: {len(create_failed)}")
        print(f"  Deletes - Success: {len(delete_success)}, Failed: {len(delete_failed)}")

        # All creates should succeed (upsert behavior)
        assert len(create_success) == num_create_threads, (
            f"Expected all {num_create_threads} creates to succeed, "
            f"but {len(create_failed)} failed: {create_failed}"
        )

        # Final state: Check for consistency
        # Permission may or may not exist depending on timing, but should not have duplicates
        final_permissions = self.content.permissions.find(principal_guid=self.user["guid"])

        assert len(final_permissions) <= 1, (
            f"Expected 0 or 1 permission after mixed operations, "
            f"but found {len(final_permissions)}. This indicates a race condition!"
        )

        print(f"  Final state: {len(final_permissions)} permission(s) exist")

        # Clean up if permission still exists
        if final_permissions:
            self.content.permissions.destroy(self.user)

    @pytest.mark.skipif(
        CONNECT_VERSION < version.parse("2025.11.0-dev"),
        reason="Requires Connect 2025.11.0 or later for upsert behavior",
    )
    def test_concurrent_permission_stress(self):
        """Stress test with many concurrent operations.

        This is an aggressive stress test with a high number of concurrent
        requests to expose potential race conditions or transaction issues.
        """
        num_concurrent_requests = 50

        def create_permission(thread_id: int):
            """Create a permission with minimal delay."""
            try:
                result = self.content.permissions.create(
                    self.user,
                    role="viewer",
                )
                return {"thread_id": thread_id, "success": True, "error": None}
            except Exception as e:
                return {"thread_id": thread_id, "success": False, "error": str(e)}

        # Execute many concurrent creates
        results = []
        with ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
            futures = [
                executor.submit(create_permission, i) for i in range(num_concurrent_requests)
            ]
            for future in as_completed(futures):
                results.append(future.result())

        # Analyze results
        successful = [r for r in results if r["success"]]
        failed = [r for r in results if not r["success"]]

        print(f"\nStress test with {num_concurrent_requests} threads:")
        print(f"  Successful: {len(successful)}, Failed: {len(failed)}")

        if failed:
            print(f"  Failed requests: {failed}")

        # All requests should succeed
        assert len(successful) == num_concurrent_requests, (
            f"Expected all {num_concurrent_requests} requests to succeed, but {len(failed)} failed"
        )

        # Critical check: Verify only ONE permission exists
        permissions = self.content.permissions.find(principal_guid=self.user["guid"])
        assert len(permissions) == 1, (
            f"RACE CONDITION DETECTED! Expected exactly 1 permission, "
            f"but found {len(permissions)}. This indicates the transaction "
            f"handling is not properly preventing duplicate inserts!"
        )

        print(f"  Final state: {len(permissions)} permission (✓ correct)")

        # Clean up
        self.content.permissions.destroy(self.user)
