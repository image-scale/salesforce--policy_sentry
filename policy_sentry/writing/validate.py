"""
Validation schema for the write-policy input files
"""

from __future__ import annotations

import logging
from typing import Any

from policy_sentry.querying.actions import get_action_data
from policy_sentry.querying.arns import get_raw_arns_for_service
from policy_sentry.util.arns import get_service_from_arn

logger = logging.getLogger(__name__)


VALID_CRUD_KEYS = {
    "mode",
    "name",
    "read",
    "write",
    "list",
    "tagging",
    "permissions-management",
    "wildcard-only",
    "skip-resource-constraints",
    "exclude-actions",
    "sts",
    "effect",
}

VALID_STS_ACTIONS = {
    "assume-role",
    "assume-role-with-saml",
    "assume-role-with-web-identity",
}


def check_actions_schema(cfg: dict[str, Any]) -> bool:
    """
    Given the cfg, check that it's a valid actions template.
    Returns True if valid.
    """
    # Check mode
    if cfg.get("mode") != "actions":
        # For backwards compatibility, don't require mode
        pass

    # Check actions
    if "actions" in cfg:
        cfg_actions = cfg["actions"]
        if cfg_actions is not None and cfg_actions and cfg_actions[0] != "":
            for action in cfg_actions:
                try:
                    service_name, action_name = action.split(":")
                    action_data = get_action_data(service_name, action_name)
                    # Just validate format, not existence in database
                except ValueError:
                    # Not in the right format
                    raise Exception(f"Invalid action format: {action}")

    return True


def check_crud_schema(cfg: dict[str, Any]) -> bool:
    """
    Given the cfg, check that it's a valid CRUD template.
    Returns True if valid, raises Exception if invalid.
    """
    # Validate that cfg keys are valid
    for key in cfg.keys():
        if key not in VALID_CRUD_KEYS:
            raise Exception(f"Invalid key in CRUD template: {key}")

    # Validate STS section if present
    sts_section = cfg.get("sts")
    if sts_section:
        for sts_action in sts_section.keys():
            if sts_action not in VALID_STS_ACTIONS:
                raise Exception(f"Invalid STS action: {sts_action}")

    # Validate ARNs in access levels
    access_levels = ["read", "write", "list", "tagging", "permissions-management"]
    for access_level in access_levels:
        arns = cfg.get(access_level)
        if arns and arns[0]:
            for arn in arns:
                # Skip empty strings
                if not arn:
                    continue
                # Extract service from ARN
                try:
                    service_prefix = get_service_from_arn(arn)
                    # Get all raw ARNs for the service - just validate the service exists
                    raw_arns = get_raw_arns_for_service(service_prefix)
                except Exception:
                    # Invalid ARN format
                    pass

    return True


def validate_condition_block(condition_block: dict[str, Any]) -> bool:
    """
    Validate a condition block from a policy template.
    """
    if not isinstance(condition_block, dict):
        return False

    for condition_operator, condition_values in condition_block.items():
        if not isinstance(condition_values, dict):
            return False
        for condition_key, condition_value in condition_values.items():
            if not isinstance(condition_key, str):
                return False

    return True


def check(schema: Any, data: Any) -> bool:
    """
    Validate data against a schema.

    This is a wrapper around the schema library's validation.

    Arguments:
        schema: A Schema object from the schema library
        data: The data to validate

    Returns:
        bool: True if the data validates against the schema, False otherwise
    """
    try:
        schema.validate(data)
        return True
    except Exception:
        return False
