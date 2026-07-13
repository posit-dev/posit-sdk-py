"""Admin utilities for Posit Connect."""

from __future__ import annotations

from dataclasses import dataclass, field

from typing_extensions import TYPE_CHECKING, List

from .permissions import PermissionRole

if TYPE_CHECKING:
    from .client import Client
    from .users import User


@dataclass
class MergeResult:
    """Result of a user merge operation.

    Attributes
    ----------
    permissions_added : list[dict]
        Permissions created on the target user. Each entry contains
        ``content_guid`` and ``role``.
    permissions_upgraded : list[dict]
        Permissions upgraded on the target user. Each entry contains
        ``content_guid``, ``old_role``, and ``new_role``.
    permissions_skipped : list[dict]
        Permissions that were not transferred because the target already
        had an equal or stronger role. Each entry contains
        ``content_guid``, ``role``, and ``reason``.
    ownership_transferred : list[str]
        Content GUIDs whose ownership was transferred from source to target.
    source_locked : bool
        Whether the source user was locked.
    errors : list[dict]
        Any errors encountered during the merge. Each entry contains
        ``content_guid``, ``action``, and ``error``.
    """

    permissions_added: list[dict] = field(default_factory=list)
    permissions_upgraded: list[dict] = field(default_factory=list)
    permissions_skipped: list[dict] = field(default_factory=list)
    ownership_transferred: list[str] = field(default_factory=list)
    source_locked: bool = False
    errors: list[dict] = field(default_factory=list)


def merge_users(
    client: Client,
    source: User | str,
    target: User | str,
    *,
    dry_run: bool = False,
    lock_source: bool = True,
) -> MergeResult:
    """Merge two user accounts by transferring content and permissions.

    Transfers all content ownership and permission grants from the
    ``source`` user to the ``target`` user, then optionally locks the
    source account.

    When both users have permissions on the same content item, the
    stronger role is kept on the target (using :class:`PermissionRole`
    for comparison).

    Parameters
    ----------
    client : Client
        An authenticated Posit Connect client.
    source : User | str
        The user to merge *from* (will be locked afterwards). Accepts a
        :class:`User` object or a GUID string.
    target : User | str
        The user to merge *into* (will receive content and permissions).
        Accepts a :class:`User` object or a GUID string.
    dry_run : bool
        If ``True``, compute what would happen without making any
        changes. Default is ``False``.
    lock_source : bool
        If ``True``, lock the source user account after transferring
        content and permissions. Default is ``True``.

    Returns
    -------
    MergeResult
        A summary of all actions taken (or planned, if ``dry_run``).

    Examples
    --------
    ```python
    from posit.connect import Client
    from posit.connect.admin import merge_users

    client = Client()

    # Preview what would happen
    result = merge_users(client, source="stale-guid", target="active-guid", dry_run=True)
    print(result)

    # Execute the merge
    result = merge_users(client, source="stale-guid", target="active-guid")
    ```
    """
    from .users import User

    # Resolve GUIDs to User objects
    if isinstance(source, str):
        source = client.users.get(source)
    if isinstance(target, str):
        target = client.users.get(target)

    result = MergeResult()

    # Step 1: Transfer content ownership
    _transfer_ownership(source, target, result, dry_run=dry_run)

    # Step 2: Transfer permissions
    _transfer_permissions(source, target, result, dry_run=dry_run)

    # Step 3: Lock the source user
    if lock_source and not dry_run:
        try:
            source.lock(force=True)
            result.source_locked = True
        except Exception as e:
            result.errors.append({
                "action": "lock_source",
                "error": str(e),
            })
    elif lock_source and dry_run:
        result.source_locked = True

    return result


def _transfer_ownership(
    source: User,
    target: User,
    result: MergeResult,
    *,
    dry_run: bool,
) -> None:
    """Transfer content ownership from source to target."""
    owned_content = source.content.find()

    for content_item in owned_content:
        content_guid = content_item["guid"]
        try:
            if not dry_run:
                content_item.update(owner_guid=target["guid"])
            result.ownership_transferred.append(content_guid)
        except Exception as e:
            result.errors.append({
                "content_guid": content_guid,
                "action": "transfer_ownership",
                "error": str(e),
            })


def _transfer_permissions(
    source: User,
    target: User,
    result: MergeResult,
    *,
    dry_run: bool,
) -> None:
    """Transfer permission grants from source to target."""
    source_perms = source.permissions.find()

    for source_perm in source_perms:
        content_guid = source_perm["content_guid"]
        source_role = PermissionRole(source_perm["role"])

        try:
            # Check if target already has a permission on this content
            target_perm = None
            content_perms = source_perm.content.permissions.find(
                principal_guid=target["guid"],
            )
            if content_perms:
                target_perm = content_perms[0]

            if target_perm is None:
                # Target has no permission — add it
                if not dry_run:
                    source_perm.content.permissions.create(
                        principal_guid=target["guid"],
                        principal_type="user",
                        role=source_perm["role"],
                    )
                result.permissions_added.append({
                    "content_guid": content_guid,
                    "role": source_perm["role"],
                })
            else:
                old_role = target_perm["role"]
                target_role = PermissionRole(old_role)
                if source_role > target_role:
                    # Source role is stronger — upgrade target
                    if not dry_run:
                        target_perm.update(role=source_perm["role"])
                    result.permissions_upgraded.append({
                        "content_guid": content_guid,
                        "old_role": old_role,
                        "new_role": source_perm["role"],
                    })
                else:
                    # Target already has equal or stronger role — skip
                    result.permissions_skipped.append({
                        "content_guid": content_guid,
                        "role": source_perm["role"],
                        "reason": f"target already has role '{target_perm['role']}'",
                    })

            # Remove source's permission
            if not dry_run:
                source_perm.destroy()

        except Exception as e:
            result.errors.append({
                "content_guid": content_guid,
                "action": "transfer_permission",
                "error": str(e),
            })
