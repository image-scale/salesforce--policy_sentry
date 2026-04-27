"""
AWS documentation-related utilities for Policy Sentry.

This module handles loading and processing access level overrides from YAML configuration.
"""

from __future__ import annotations

import logging
from typing import Any

import yaml

from policy_sentry.shared.constants import DATASTORE_FILE_PATH

logger = logging.getLogger(__name__)

# Path to access level overrides file
ACCESS_LEVEL_OVERRIDES_FILE = DATASTORE_FILE_PATH.parent / "access-level-overrides.yml"


def get_action_access_level_overrides_from_yml(service_prefix: str) -> dict[str, list[str]]:
    """
    Get the access level overrides for a given service prefix from the YAML file.

    These overrides correct AWS documentation errors where actions are listed with
    incorrect access levels.

    Arguments:
        service_prefix: The AWS service prefix, like 'iam' or 'ram'

    Returns:
        dict: A dictionary mapping access levels to lists of actions.
              Example: {"Permissions management": ["createaccesskey", "createuser"],
                       "Tagging": ["tagresource", "untagresource"]}
    """
    result: dict[str, list[str]] = {}

    try:
        with open(ACCESS_LEVEL_OVERRIDES_FILE, "r") as file:
            overrides_config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.warning(f"Access level overrides file not found: {ACCESS_LEVEL_OVERRIDES_FILE}")
        return result
    except yaml.YAMLError as e:
        logger.warning(f"Error parsing access level overrides file: {e}")
        return result

    if not overrides_config:
        return result

    service_overrides = overrides_config.get(service_prefix, {})

    if not service_overrides:
        return result

    for access_level, actions in service_overrides.items():
        if isinstance(actions, list):
            result[access_level] = actions

    return result


def get_all_access_level_overrides() -> dict[str, dict[str, list[str]]]:
    """
    Get all access level overrides from the YAML file.

    Returns:
        dict: A dictionary mapping service prefixes to their access level overrides.
              Example: {"iam": {"Permissions management": ["createaccesskey"]}}
    """
    try:
        with open(ACCESS_LEVEL_OVERRIDES_FILE, "r") as file:
            overrides_config = yaml.safe_load(file)
    except FileNotFoundError:
        logger.warning(f"Access level overrides file not found: {ACCESS_LEVEL_OVERRIDES_FILE}")
        return {}
    except yaml.YAMLError as e:
        logger.warning(f"Error parsing access level overrides file: {e}")
        return {}

    if not overrides_config:
        return {}

    result: dict[str, dict[str, list[str]]] = {}
    for service_prefix, access_levels in overrides_config.items():
        if isinstance(access_levels, dict):
            result[service_prefix] = {}
            for access_level, actions in access_levels.items():
                if isinstance(actions, list):
                    result[service_prefix][access_level] = actions

    return result
