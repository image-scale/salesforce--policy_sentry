"""
Given a Policy Sentry YAML file, generate an IAM policy with least privilege.
"""

from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import click

from policy_sentry import set_stream_logger
from policy_sentry.util.file import read_yaml_file
from policy_sentry.writing.sid_group import SidGroup

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


def write_policy_with_template(cfg: dict[str, Any], minimize: int | None = None) -> dict[str, Any]:
    """
    Write an IAM policy by processing the Policy Sentry YAML template.

    This function is the primary library interface for generating least-privilege policies.

    Arguments:
        cfg: The loaded YAML template as a dict. Must follow Policy Sentry format.
        minimize: Minimize the resulting statement with *safe* usage of wildcards to reduce
                  policy length. Set this to the character length you want - for example, 0, or 4.
                  Defaults to None (no minimization).

    Returns:
        Dictionary: The rendered IAM JSON Policy
    """
    sid_group = SidGroup()
    return sid_group.process_template(cfg, minimize=minimize)


@click.command(
    short_help="Write an IAM policy based on a Policy Sentry YAML template."
)
@click.option(
    "--input-file",
    "-i",
    type=click.Path(exists=True),
    required=True,
    help="Path to the Policy Sentry YAML input file",
)
@click.option(
    "--minimize",
    "-m",
    type=int,
    required=False,
    default=None,
    help="Minimize the output by using wildcards to reduce character count. "
         "Supply an integer representing the minimum number of characters to include. "
         "Default is None (no minimization).",
)
@click.option(
    "--verbose",
    "-v",
    type=click.Choice(["critical", "error", "warning", "info", "debug"], case_sensitive=False),
)
def write_policy(input_file: str, minimize: int | None, verbose: str | None) -> None:
    """
    Write an IAM policy based on a Policy Sentry YAML template.

    This command reads a YAML template file that defines the desired permissions
    either in CRUD mode (specifying resource ARNs and access levels) or Actions mode
    (specifying individual IAM actions). It then generates a least-privilege IAM
    policy as JSON output.
    """
    if verbose:
        log_level = getattr(logging, verbose.upper())
        set_stream_logger(level=log_level)

    cfg = read_yaml_file(input_file)
    policy = write_policy_with_template(cfg, minimize=minimize)
    print(json.dumps(policy, indent=4))
