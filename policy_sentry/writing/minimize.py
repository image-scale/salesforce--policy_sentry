"""
Functions for minimizing statement actions using wildcards
"""

from __future__ import annotations


def minimize_statement_actions(
    actions: list[str], all_actions: set[str], minchars: int | None = 0
) -> list[str]:
    """
    Take a list of actions and generate a smaller list of actions with wildcards.

    Arguments:
        actions: A list of actions
        all_actions: A set of all possible actions (should be lowercase)
        minchars: Minimum number of characters before the wildcard. 0 means use the shortest possible.

    Returns:
        List: A minimized list of actions
    """
    if not actions:
        return []

    # Handle None minchars
    if minchars is None:
        minchars = 0

    # Handle wildcard-only actions (like "ec2:*")
    result = []
    non_wildcard_actions = []
    for action in actions:
        if "*" in action:
            # Keep wildcards as-is
            result.append(action.lower())
        else:
            non_wildcard_actions.append(action)

    if not non_wildcard_actions:
        return result

    # Group actions by service
    service_actions: dict[str, list[str]] = {}
    for action in non_wildcard_actions:
        if ":" in action:
            service, action_name = action.split(":", 1)
            service_lower = service.lower()
            if service_lower not in service_actions:
                service_actions[service_lower] = []
            service_actions[service_lower].append(action_name.lower())

    # Minimize actions for each service
    for service, action_names in service_actions.items():
        # Get all actions for this service from the all_actions set
        service_all_actions = set()
        for a in all_actions:
            if ":" in a:
                parts = a.split(":", 1)
                if parts[0].lower() == service:
                    service_all_actions.add(parts[1].lower())

        minimized = _minimize_service_actions(
            service, set(action_names), service_all_actions, minchars
        )
        result.extend(minimized)

    return result


def _minimize_service_actions(
    service: str, target_actions: set[str], service_all_actions: set[str], minchars: int
) -> list[str]:
    """
    Minimize actions for a single service.

    Arguments:
        service: The service prefix (lowercase)
        target_actions: Set of action names we want to match (without service prefix, lowercase)
        service_all_actions: Set of all possible action names for this service (lowercase)
        minchars: Minimum number of characters before the wildcard

    Returns:
        List: A minimized list of actions with service prefix
    """
    results = []
    covered = set()

    # Process actions sorted by name for consistent output
    sorted_targets = sorted(target_actions)

    for target in sorted_targets:
        if target in covered:
            continue

        # Find the shortest prefix that matches this target and possibly other targets,
        # but does NOT match any non-target actions
        best_prefix = None
        best_covered = set()

        # Start from shortest possible prefix and go longer
        min_len = max(1, minchars)
        for prefix_len in range(min_len, len(target) + 1):
            prefix = target[:prefix_len]

            # Find all targets that match this prefix
            matching_targets = {a for a in target_actions if a.startswith(prefix)}

            # Find all actions (targets + non-targets) that match this prefix
            matching_all = {a for a in service_all_actions if a.startswith(prefix)}

            # This prefix is valid if it ONLY matches target actions
            if matching_all == matching_targets:
                # Check if this is better than what we have
                # Prefer prefixes that cover more targets
                if best_prefix is None or len(matching_targets) > len(best_covered):
                    best_prefix = prefix
                    best_covered = matching_targets
                # If we found a valid prefix, don't go longer - we want the shortest
                break

        if best_prefix is not None:
            # Use wildcard if the prefix matches more than just the exact action
            if len(best_prefix) < len(target) or len(best_covered) > 1:
                results.append(f"{service}:{best_prefix}*")
            else:
                # Exact match, no wildcard needed
                results.append(f"{service}:{target}")
            covered.update(best_covered)
        else:
            # Couldn't find a valid prefix, use the exact action
            results.append(f"{service}:{target}")
            covered.add(target)

    return results
