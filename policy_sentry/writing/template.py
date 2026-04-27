"""
Create the YML Template files for the write-policy command.
"""

from __future__ import annotations

from typing import Any

CRUD_TEMPLATE = """mode: crud
name: ''
# Specify resource ARNs
read:
- ''
write:
- ''
list:
- ''
tagging:
- ''
permissions-management:
- ''
# Actions that do not support resource constraints
wildcard-only:
  single-actions: # standalone actions
  - ''
  # Service-wide - like 's3' or 'ec2'
  service-read:
  - ''
  service-write:
  - ''
  service-list:
  - ''
  service-tagging:
  - ''
  service-permissions-management:
  - ''
# Skip resource constraint requirements by listing actions here.
skip-resource-constraints:
- ''
# Exclude actions from the output by specifying them here. Accepts wildcards, like kms:Delete*
exclude-actions:
- ''
# If this policy needs to include an AssumeRole action
sts:
  assume-role:
    - ''
  assume-role-with-saml:
    - ''
  assume-role-with-web-identity:
    - ''
"""

ACTIONS_TEMPLATE = """mode: actions
name: ''
actions:
- ''
"""


def create_crud_template() -> str:
    """Generate the CRUD template and return as a string"""
    return CRUD_TEMPLATE


def create_actions_template() -> str:
    """Generate the Actions template and return as a string"""
    return ACTIONS_TEMPLATE


def get_crud_template_dict() -> dict[str, Any]:
    """
    Generate an empty CRUD template as a dictionary.

    Returns:
        dict: A dictionary representing the CRUD template structure with empty values.
    """
    return {
        "mode": "crud",
        "name": "",
        "read": [],
        "write": [],
        "list": [],
        "tagging": [],
        "permissions-management": [],
        "wildcard-only": {
            "single-actions": [],
            "service-read": [],
            "service-write": [],
            "service-list": [],
            "service-tagging": [],
            "service-permissions-management": [],
        },
        "skip-resource-constraints": [],
        "exclude-actions": [],
        "sts": {
            "assume-role": [],
            "assume-role-with-saml": [],
            "assume-role-with-web-identity": [],
        },
    }


def get_actions_template_dict() -> dict[str, Any]:
    """
    Generate an empty Actions template as a dictionary.

    Returns:
        dict: A dictionary representing the Actions template structure with empty values.
    """
    return {
        "mode": "actions",
        "name": "",
        "actions": [],
    }
