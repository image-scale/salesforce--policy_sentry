"""
Functions for analyzing IAM policies
"""

from __future__ import annotations

import logging
from typing import Any

from policy_sentry.analysis.expand import determine_actions_to_expand
from policy_sentry.querying.actions import (
    get_action_data,
    get_actions_with_access_level,
    remove_actions_not_matching_access_level,
)

logger = logging.getLogger(__name__)


def analyze_by_access_level(policy_json: dict[str, Any], access_level: str) -> list[str]:
    """
    Determine if a policy has any actions with a given access level.

    Arguments:
        policy_json: Policy JSON object
        access_level: Access level like "Permissions management" or "Read"

    Returns:
        List: A list of actions with that access level, sorted alphabetically
    """
    results = set()
    statements = policy_json.get("Statement", [])
    for statement in statements:
        if statement.get("Effect") == "Deny":
            continue
        action_clause = statement.get("Action")
        if not action_clause:
            continue
        if isinstance(action_clause, str):
            action_clause = [action_clause]
        # Now we need to expand wildcards, if they exist
        all_actions = determine_actions_to_expand(action_clause)
        # Now we need to filter by access level
        results.update(remove_actions_not_matching_access_level(all_actions, access_level))
    return sorted(results)


def analyze_statement_by_access_level(statement: dict[str, Any], access_level: str) -> list[str]:
    """
    Determine if a statement (part of an IAM policy) has any actions with a given access level.

    Arguments:
        statement: The statement dictionary from a policy
        access_level: Access level like "Permissions management" or "Read"

    Returns:
        List: A list of actions with that access level
    """
    results = []
    if statement.get("Effect") == "Deny":
        return results
    action_clause = statement.get("Action")
    if not action_clause:
        return results
    if isinstance(action_clause, str):
        action_clause = [action_clause]
    # Now we need to expand wildcards, if they exist
    all_actions = determine_actions_to_expand(action_clause)
    # Now we need to filter by access level
    results.extend(remove_actions_not_matching_access_level(all_actions, access_level))
    return results
