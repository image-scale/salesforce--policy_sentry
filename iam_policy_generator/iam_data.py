"""
IAM data loading and querying module.

This module loads the IAM definition data from a bundled JSON file and provides
functions to query service prefixes, actions, and related metadata.
"""

from __future__ import annotations

import functools
from pathlib import Path
from typing import Any

import orjson


SCHEMA_VERSION_KEY = "policy_sentry_schema_version"
DATA_FILE_PATH = Path(__file__).parent / "data" / "iam-definition.json"


def _load_iam_data() -> dict[str, Any]:
    """Load the IAM definition data from the bundled JSON file."""
    return orjson.loads(DATA_FILE_PATH.read_bytes())


_iam_data: dict[str, Any] = _load_iam_data()


def get_iam_data() -> dict[str, Any]:
    """Return the loaded IAM definition data dictionary."""
    return _iam_data


@functools.lru_cache(maxsize=1)
def get_schema_version() -> str:
    """Return the schema version of the IAM datastore."""
    return str(_iam_data.get(SCHEMA_VERSION_KEY, "unknown"))


@functools.lru_cache(maxsize=1)
def get_all_service_prefixes() -> set[str]:
    """
    Get all AWS service prefixes from the IAM data.

    Returns:
        A set of service prefix strings (e.g., {'s3', 'ec2', 'iam'}).
    """
    prefixes = set(_iam_data.keys())
    prefixes.discard(SCHEMA_VERSION_KEY)
    return prefixes


@functools.lru_cache(maxsize=1024)
def get_service_data(service_prefix: str) -> dict[str, Any]:
    """
    Get the full data dictionary for an AWS service.

    Args:
        service_prefix: An AWS service prefix like 's3' or 'ec2'.

    Returns:
        A dictionary containing service metadata, privileges, resources, and conditions.
        Returns an empty dict if the service is not found.
    """
    service_data = _iam_data.get(service_prefix)
    if service_data and isinstance(service_data, dict):
        return service_data

    if service_prefix == "catalog":
        return _iam_data.get("servicecatalog", {})

    return {}


@functools.lru_cache(maxsize=1024)
def get_actions_for_service(service_prefix: str, lowercase: bool = False) -> list[str]:
    """
    Get all IAM actions for a given AWS service.

    Args:
        service_prefix: An AWS service prefix like 's3' or 'ec2'.
        lowercase: If True, return action names in lowercase.

    Returns:
        A list of fully qualified action names (e.g., ['s3:GetObject', 's3:PutObject']).
        Returns an empty list if the service is not found.
    """
    service_data = get_service_data(service_prefix)
    if not service_data:
        return []

    privileges_lower = service_data.get("privileges_lower_name", {})
    if lowercase:
        action_names = privileges_lower.keys()
    else:
        action_names = privileges_lower.values()

    return [f"{service_prefix}:{name}" for name in action_names]


@functools.lru_cache(maxsize=1)
def get_all_actions(lowercase: bool = False) -> set[str]:
    """
    Get all IAM actions across all AWS services.

    Args:
        lowercase: If True, return action names in lowercase.

    Returns:
        A set of all fully qualified action names.
    """
    all_actions: set[str] = set()

    for prefix in get_all_service_prefixes():
        actions = get_actions_for_service(prefix, lowercase=lowercase)
        all_actions.update(actions)

    return all_actions
