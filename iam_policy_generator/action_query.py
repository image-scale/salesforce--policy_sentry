"""
Action querying module.

This module provides functions to query AWS IAM actions from the IAM definition
database. It supports filtering by access level, resource type, and other criteria.
"""

from __future__ import annotations

import functools
from typing import Any

from iam_policy_generator.iam_data import (
    get_service_data,
    get_all_service_prefixes,
    get_iam_data,
)


@functools.lru_cache(maxsize=1024)
def get_action_data(service: str, action_name: str) -> dict[str, list[dict[str, Any]]]:
    """
    Get detailed metadata about an IAM action.

    Args:
        service: An AWS service prefix like 's3' or 'kms'.
        action_name: The action name like 'GetObject'. Use '*' to get all actions.

    Returns:
        A dictionary with the service as key and a list of action data dicts as value.
        Each dict contains: action, description, access_level, resource_arn_format,
        condition_keys, dependent_actions.
    """
    result: dict[str, list[dict[str, Any]]] = {}
    service_data = get_service_data(service)

    if not service_data:
        return result

    privileges = service_data.get("privileges", {})
    privileges_lower = service_data.get("privileges_lower_name", {})

    if action_name == "*" or action_name.endswith("*"):
        prefix = action_name.rstrip("*").lower()
        entries = []
        for name, data in privileges.items():
            if not prefix or name.lower().startswith(prefix):
                entries.extend(_build_action_entries(service_data, name, data))
        result[service] = entries
        return result

    actual_name = privileges_lower.get(action_name.lower())
    if actual_name and actual_name in privileges:
        data = privileges[actual_name]
        entries = _build_action_entries(service_data, actual_name, data)
        result[service] = entries

    return result


def _build_action_entries(
    service_data: dict[str, Any],
    action_name: str,
    action_data: dict[str, Any]
) -> list[dict[str, Any]]:
    """Build action entry dictionaries for an action."""
    entries = []
    prefix = service_data.get("prefix", "")
    resources = service_data.get("resources", {})

    wildcard_condition_keys = []
    resource_types = action_data.get("resource_types", {})
    if "" in resource_types:
        wildcard_condition_keys = resource_types[""].get("condition_keys", [])

    for resource_type, rt_data in resource_types.items():
        resource_arn = "*"
        condition_keys = list(wildcard_condition_keys)
        dependent_actions = rt_data.get("dependent_actions", [])

        if resource_type and resource_type in resources:
            resource_info = resources[resource_type]
            resource_arn = resource_info.get("arn", "*")
            if resource_info.get("condition_keys"):
                condition_keys.extend(resource_info["condition_keys"])

        entry = {
            "action": f"{prefix}:{action_name}",
            "description": action_data.get("description", ""),
            "access_level": action_data.get("access_level", ""),
            "resource_arn_format": resource_arn,
            "condition_keys": condition_keys,
            "dependent_actions": dependent_actions,
        }
        entries.append(entry)

    return entries


def get_actions_with_access_level(service_prefix: str, access_level: str) -> list[str]:
    """
    Get actions that have a specific access level.

    Args:
        service_prefix: A service prefix like 's3', or 'all' for all services.
        access_level: One of 'Read', 'Write', 'List', 'Tagging', 'Permissions management'.

    Returns:
        A list of action names like ['s3:GetObject', 's3:GetBucketAcl'].
    """
    results = []

    if service_prefix == "all":
        for svc in get_all_service_prefixes():
            results.extend(get_actions_with_access_level(svc, access_level))
    else:
        service_data = get_service_data(service_prefix)
        if service_data:
            for name, data in service_data.get("privileges", {}).items():
                if data.get("access_level") == access_level:
                    results.append(f"{service_prefix}:{name}")

    return results


def get_actions_matching_arn_type(service_prefix: str, resource_type_name: str) -> list[str]:
    """
    Get actions that apply to a specific resource type.

    Args:
        service_prefix: A service prefix like 's3', or 'all' for all services.
        resource_type_name: The resource type name like 'bucket' or 'object'.
            Use '*' for wildcard-only actions.

    Returns:
        A list of action names that apply to that resource type.
    """
    if resource_type_name == "*":
        return get_actions_that_support_wildcard_arns_only(service_prefix)

    results = []

    if service_prefix == "all":
        for svc in get_all_service_prefixes():
            results.extend(get_actions_matching_arn_type(svc, resource_type_name))
    else:
        service_data = get_service_data(service_prefix)
        if service_data:
            for name, data in service_data.get("privileges", {}).items():
                resource_types_lower = data.get("resource_types_lower_name", {})
                if resource_type_name.lower() in resource_types_lower:
                    results.append(f"{service_prefix}:{name}")

    return results


def get_actions_with_arn_type_and_access_level(
    service_prefix: str,
    resource_type_name: str,
    access_level: str
) -> list[str]:
    """
    Get actions that match both a resource type and access level.

    Args:
        service_prefix: A service prefix like 's3', or 'all' for all services.
        resource_type_name: The resource type name like 'bucket'.
        access_level: One of 'Read', 'Write', 'List', 'Tagging', 'Permissions management'.

    Returns:
        A list of action names matching both criteria.
    """
    if resource_type_name == "*":
        return get_actions_at_access_level_that_support_wildcard_arns_only(
            service_prefix, access_level
        )

    results = []

    if service_prefix == "all":
        for svc in get_all_service_prefixes():
            results.extend(
                get_actions_with_arn_type_and_access_level(svc, resource_type_name, access_level)
            )
    else:
        service_data = get_service_data(service_prefix)
        if service_data:
            prefix = service_data.get("prefix", service_prefix)
            for name, data in service_data.get("privileges", {}).items():
                if data.get("access_level") == access_level:
                    resource_types_lower = data.get("resource_types_lower_name", {})
                    if resource_type_name.lower() in resource_types_lower:
                        results.append(f"{prefix}:{name}")

    return results


def get_actions_that_support_wildcard_arns_only(service_prefix: str) -> list[str]:
    """
    Get actions that only support wildcard (*) resource ARNs.

    These are actions that do not support resource-level permissions.

    Args:
        service_prefix: A service prefix like 's3', or 'all' for all services.

    Returns:
        A list of action names that only support wildcard ARNs.
    """
    results = []

    if service_prefix == "all":
        for svc in get_all_service_prefixes():
            results.extend(get_actions_that_support_wildcard_arns_only(svc))
    else:
        service_data = get_service_data(service_prefix)
        if service_data:
            for name, data in service_data.get("privileges", {}).items():
                resource_types = data.get("resource_types", {})
                if len(resource_types) == 1 and "" in resource_types:
                    results.append(f"{service_prefix}:{name}")

    return results


def get_actions_at_access_level_that_support_wildcard_arns_only(
    service_prefix: str,
    access_level: str
) -> list[str]:
    """
    Get wildcard-only actions at a specific access level.

    Args:
        service_prefix: A service prefix like 's3', or 'all' for all services.
        access_level: One of 'Read', 'Write', 'List', 'Tagging', 'Permissions management'.

    Returns:
        A list of wildcard-only action names at that access level.
    """
    results = []

    if service_prefix == "all":
        for svc in get_all_service_prefixes():
            results.extend(
                get_actions_at_access_level_that_support_wildcard_arns_only(svc, access_level)
            )
    else:
        service_data = get_service_data(service_prefix)
        if service_data:
            for name, data in service_data.get("privileges", {}).items():
                if data.get("access_level") == access_level:
                    resource_types = data.get("resource_types", {})
                    if len(resource_types) == 1 and "" in resource_types:
                        results.append(f"{service_prefix}:{name}")

    return results


def get_dependent_actions(action_list: list[str]) -> list[str]:
    """
    Get dependent actions for a list of actions.

    Some IAM actions require additional actions to be permitted.
    This function returns those dependent actions.

    Args:
        action_list: A list of action names like ['kms:CreateCustomKeyStore'].

    Returns:
        A list of dependent action names.
    """
    dependent = set()

    for action in action_list:
        if ":" not in action:
            continue
        service, action_name = action.split(":", 1)
        action_data = get_action_data(service, action_name)
        for entry_list in action_data.values():
            for entry in entry_list:
                deps = entry.get("dependent_actions", [])
                dependent.update(deps)

    return list(dependent)


def filter_actions_by_access_level(actions: list[str], access_level: str) -> list[str]:
    """
    Filter a list of actions to only include those matching an access level.

    Args:
        actions: A list of action names.
        access_level: One of 'Read', 'Write', 'List', 'Tagging', 'Permissions management'.

    Returns:
        A filtered list of action names.
    """
    results = []

    if actions == ["*"]:
        for svc in get_all_service_prefixes():
            results.extend(get_actions_with_access_level(svc, access_level))
        return results

    for action in actions:
        if ":" not in action:
            continue
        service, action_name = action.split(":", 1)
        matched = _get_action_if_access_level_matches(service, action_name, access_level)
        if matched:
            results.append(matched)

    return results


def _get_action_if_access_level_matches(
    service: str,
    action_name: str,
    access_level: str
) -> str | None:
    """Return action name if it matches access level, else None."""
    service_data = get_service_data(service.lower())
    if not service_data:
        return None

    privileges_lower = service_data.get("privileges_lower_name", {})
    actual_name = privileges_lower.get(action_name.lower())
    if not actual_name:
        return None

    privileges = service_data.get("privileges", {})
    action_data = privileges.get(actual_name)
    if action_data and action_data.get("access_level") == access_level:
        return f"{service}:{actual_name}"

    return None


def filter_actions_to_wildcard_only(actions: list[str]) -> list[str]:
    """
    Filter a list of actions to only include those that support wildcard ARNs only.

    Args:
        actions: A list of action names.

    Returns:
        A filtered list of action names that only support wildcard ARNs.
    """
    results = []

    for action in set(actions):
        if ":" not in action:
            continue
        service, action_name = action.split(":", 1)
        action_data = get_action_data(service, action_name)

        for entries in action_data.values():
            if len(entries) == 1 and entries[0]["resource_arn_format"] == "*":
                results.append(entries[0]["action"])
                break

    return results
