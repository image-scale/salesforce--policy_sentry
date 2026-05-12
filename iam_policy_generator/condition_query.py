"""
Condition key querying module.

This module provides functions to query AWS IAM condition keys from the
IAM definition database.
"""

from __future__ import annotations

import functools
from typing import Any

from iam_policy_generator.iam_data import get_service_data
from iam_policy_generator.action_query import get_action_data


def _matches_condition_key(db_key: str, query_key: str) -> bool:
    """
    Check if a condition key from the database matches a query condition key.

    Handles pattern matching for keys like:
    - s3:ExistingObjectTag/<key>
    - license-manager:ResourceTag/${TagKey}
    - secretsmanager:ResourceTag/tag-key
    """
    db_lower = db_key.lower()
    query_lower = query_key.lower()

    if db_lower == query_lower:
        return True

    if "$" in db_lower:
        prefix = db_lower.split("$")[0]
        if query_lower.startswith(prefix):
            return True
    elif "<" in db_lower:
        prefix = db_lower.split("<")[0]
        if query_lower.startswith(prefix):
            return True
    elif "tag-key" in db_lower:
        prefix = db_lower.split("tag-key")[0]
        if query_lower.startswith(prefix):
            return True

    return False


@functools.lru_cache(maxsize=1024)
def get_condition_keys_for_service(service_prefix: str) -> list[str]:
    """
    Get all condition keys available for an AWS service.

    Args:
        service_prefix: An AWS service prefix like 's3' or 'ec2'.

    Returns:
        A list of condition key names.
    """
    service_data = get_service_data(service_prefix)
    if not service_data:
        return []

    conditions = service_data.get("conditions", {})
    return list(conditions.keys())


def get_condition_key_details(service_prefix: str, condition_key_name: str) -> dict[str, str]:
    """
    Get detailed metadata about a condition key.

    Args:
        service_prefix: An AWS service prefix like 'ec2'.
        condition_key_name: The condition key name like 'ec2:Vpc'.

    Returns:
        A dictionary with name, description, and condition_value_type.
        Returns empty dict if not found.
    """
    service_data = get_service_data(service_prefix)
    if not service_data:
        return {}

    conditions = service_data.get("conditions", {})
    for key_name, key_data in conditions.items():
        if _matches_condition_key(key_name, condition_key_name):
            return {
                "name": key_name,
                "description": key_data.get("description", ""),
                "condition_value_type": key_data.get("type", "").lower(),
            }

    return {}


def get_condition_value_type(condition_key: str) -> str | None:
    """
    Get the data type for a condition key.

    Args:
        condition_key: A condition key like 'ec2:Vpc' or 's3:prefix'.

    Returns:
        The type name like 'string', 'bool', 'date', 'arn', 'number', or None.
    """
    if ":" not in condition_key:
        return None

    service_prefix = condition_key.split(":")[0]
    service_data = get_service_data(service_prefix)
    if not service_data:
        return None

    conditions = service_data.get("conditions", {})
    for key_name, key_data in conditions.items():
        if _matches_condition_key(key_name, condition_key):
            return _normalize_condition_type(key_data.get("type", ""))

    return None


def _normalize_condition_type(type_str: str) -> str:
    """Normalize condition type strings to standard names."""
    type_lower = type_str.lower()

    if type_lower in ("arn",):
        return "arn"
    if type_lower in ("bool", "boolean"):
        return "bool"
    if type_lower == "date":
        return "date"
    if type_lower in ("long", "numeric"):
        return "number"
    if type_lower in ("string", "arrayofstring"):
        return "string"
    if type_lower == "ip":
        return "ip"

    return type_lower


def get_conditions_for_action_and_raw_arn(action: str, raw_arn: str) -> list[str]:
    """
    Get condition keys available for a specific action and resource ARN.

    Args:
        action: An IAM action like 's3:GetObject'.
        raw_arn: A raw ARN format like 'arn:${Partition}:s3:::${BucketName}/${ObjectName}'.

    Returns:
        A list of condition key names.
    """
    if ":" not in action:
        return []

    service_prefix, action_name = action.split(":", 1)
    action_data = get_action_data(service_prefix, action_name)

    conditions = []
    for entries in action_data.values():
        for entry in entries:
            if entry.get("resource_arn_format", "").lower() == raw_arn.lower():
                conditions.extend(entry.get("condition_keys", []))

    return conditions


def get_condition_keys_for_raw_arn(raw_arn: str) -> list[str]:
    """
    Get condition keys available for a specific raw ARN format.

    Args:
        raw_arn: A raw ARN format like 'arn:${Partition}:s3:::${BucketName}'.

    Returns:
        A list of condition key names.
    """
    elements = raw_arn.split(":", 5)
    if len(elements) < 3:
        return []

    service_prefix = elements[2]
    service_data = get_service_data(service_prefix)
    if not service_data:
        return []

    results = set()
    for resource_data in service_data.get("resources", {}).values():
        if resource_data.get("arn") == raw_arn:
            results.update(resource_data.get("condition_keys", []))

    return list(results)


def get_actions_matching_condition_key(service_prefix: str, condition_key: str) -> list[str]:
    """
    Get all actions in a service that support a specific condition key.

    Args:
        service_prefix: An AWS service prefix like 's3'.
        condition_key: A condition key like 's3:prefix'.

    Returns:
        A list of action names.
    """
    service_data = get_service_data(service_prefix)
    if not service_data:
        return []

    results = []
    for action_name, action_data in service_data.get("privileges", {}).items():
        for rt_data in action_data.get("resource_types", {}).values():
            condition_keys = rt_data.get("condition_keys", [])
            for key in condition_keys:
                if _matches_condition_key(key, condition_key):
                    results.append(f"{service_prefix}:{action_name}")
                    break

    return results
