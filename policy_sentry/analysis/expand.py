"""
Allow users to expand wildcards in IAM action strings, and identify
policies that are overly permissive.
"""

from __future__ import annotations

from fnmatch import fnmatch

from policy_sentry.querying.all import get_all_actions


def expand_action(action: str, raise_error: bool = True) -> list[str]:
    """
    expand_action: expand a potentially-wildcarded action to a list of
    expanded actions.

    Arguments:
        action: An action, like `s3:GetObject` or `ec2:Describe*`
        raise_error: Whether or not to throw an error if the action can't be
            found.
    Returns:
        list: A list of actions.
    """
    # get all actions from the database
    all_actions = get_all_actions()

    # Handle service:*
    if action == "*":
        return ["*"]

    results = []
    # fnmatch is case insensitive
    action_lower = action.lower()
    for possible_action in all_actions:
        if fnmatch(possible_action.lower(), action_lower):
            results.append(possible_action)

    if not results and raise_error:
        raise Exception(f"No match found for {action}")

    return results


def determine_actions_to_expand(action_list: list[str]) -> list[str]:
    """
    Loop through a list of actions and use expand_action to get the list of actions back.
    """
    # Loop through every action string provided by user
    results = []
    for action in action_list:
        result = expand_action(action=action, raise_error=False)
        results.extend(result)
    return results


def get_expanded_policy(policy: dict) -> dict:
    """
    Given a policy, expand the wildcards in the actions.

    Arguments:
        policy: A policy dict with Statement containing Action lists

    Returns:
        dict: The policy with all wildcards expanded
    """
    expanded_policy = {
        "Version": policy.get("Version", "2012-10-17"),
        "Statement": [],
    }

    statements = policy.get("Statement", [])
    for statement in statements:
        new_statement = statement.copy()
        actions = statement.get("Action", [])

        # Ensure actions is a list
        if isinstance(actions, str):
            actions = [actions]

        expanded_actions = []
        for action in actions:
            expanded = expand_action(action, raise_error=False)
            if expanded:
                expanded_actions.extend(expanded)
            else:
                # If no expansion found, keep the original
                expanded_actions.append(action)

        # Remove duplicates and sort
        expanded_actions = sorted(set(expanded_actions))
        new_statement["Action"] = expanded_actions
        expanded_policy["Statement"].append(new_statement)

    return expanded_policy
