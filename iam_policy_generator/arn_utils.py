"""
ARN parsing and matching utilities.

This module provides functions for parsing AWS ARN strings and matching
user-supplied ARNs against raw ARN formats in the IAM database.

AWS ARN formats (from AWS docs):
    Case 1: arn:partition:service:region:account-id:resource
    Case 2: arn:partition:service:region:account-id:resourcetype/resource
    Case 3: arn:partition:service:region:account-id:resourcetype/resource/qualifier
    Case 4: arn:partition:service:region:account-id:resourcetype/resource:qualifier
    Case 5: arn:partition:service:region:account-id:resourcetype:resource
    Case 6: arn:partition:service:region:account-id:resourcetype:resource:qualifier
"""

from __future__ import annotations

import re
from typing import Any


SEPARATOR_PATTERN = re.compile(r"[:/]")
ARN_REGEX = re.compile(r"^arn:([^:]*):([^:]*):([^:]*):([^:]*):(.+)$")

SPECIAL_RESOURCE_TYPES = {
    "${ObjectName}",
    "${RepositoryName}",
    "${BucketName}",
    "table/${TableName}",
    "${BucketName}/${ObjectName}",
}


class InvalidArnError(Exception):
    """Raised when an invalid ARN is provided."""
    pass


def parse_arn(arn: str) -> dict[str, str]:
    """
    Parse an ARN into its component parts.

    Args:
        arn: An AWS ARN string like 'arn:aws:s3:::mybucket'.

    Returns:
        A dictionary with keys: arn, partition, service, region, account, resource, resource_path.

    Raises:
        InvalidArnError: If the ARN does not follow the expected format.
    """
    try:
        elements = arn.split(":", 5)
        if len(elements) < 6:
            raise InvalidArnError(f"The provided ARN '{arn}' is invalid. Not enough colon-separated parts.")

        result = {
            "arn": elements[0],
            "partition": elements[1],
            "service": elements[2],
            "region": elements[3],
            "account": elements[4],
            "resource": elements[5],
            "resource_path": "",
        }
    except (IndexError, ValueError) as error:
        raise InvalidArnError(f"The provided ARN '{arn}' is invalid: {error}") from error

    if "/" in result["resource"]:
        result["resource"], result["resource_path"] = result["resource"].split("/", 1)
    elif ":" in result["resource"]:
        result["resource"], result["resource_path"] = result["resource"].split(":", 1)

    return result


def get_service_from_arn(arn: str) -> str:
    """Extract the service prefix from an ARN."""
    return parse_arn(arn)["service"]


def get_region_from_arn(arn: str) -> str:
    """Extract the region from an ARN (may be empty for global resources like S3)."""
    region = parse_arn(arn)["region"]
    return region if region else ""


def get_account_from_arn(arn: str) -> str:
    """Extract the account ID from an ARN (may be empty for some resources like S3)."""
    account = parse_arn(arn)["account"]
    return account if account else ""


def get_resource_string(arn: str) -> str:
    """
    Get the resource string (everything after account-id) from an ARN.

    For 'arn:aws:s3:::mybucket/mykey', returns 'mybucket/mykey'.
    """
    parts = arn.split(":", 5)
    return parts[5] if len(parts) > 5 else ""


def get_resource_type(arn: str) -> str | None:
    """
    Extract the resource type from an ARN.

    For 'arn:aws:ssm:us-east-1:123456789012:parameter/test', returns 'parameter'.
    For 'arn:aws:s3:::mybucket', returns None (no resource type prefix).
    """
    resource_string = get_resource_string(arn)
    parts = re.split(SEPARATOR_PATTERN, resource_string)
    if len(parts) > 1:
        return parts[0]
    return None


class ResourceArn:
    """
    Class for parsing and matching ARNs.

    This class helps determine if a user-supplied ARN matches a raw ARN format
    from the IAM database.
    """

    def __init__(self, arn: str) -> None:
        """
        Initialize with an ARN string.

        Args:
            arn: An ARN string to parse.

        Raises:
            InvalidArnError: If the ARN format is invalid.
        """
        self.arn = arn

        if not ARN_REGEX.match(arn):
            raise InvalidArnError("The provided value does not follow required ARN format.")

        try:
            elements = arn.split(":", 5)
            self.partition = elements[1]
            self.service = elements[2]
            self.region = elements[3]
            self.account = elements[4]
            self.resource = elements[5]
        except IndexError as error:
            raise InvalidArnError(f"The provided ARN is invalid: {error}") from error

        self.resource_path = ""
        if "/" in self.resource:
            self.resource, self.resource_path = self.resource.split("/", 1)
        elif ":" in self.resource:
            self.resource, self.resource_path = self.resource.split(":", 1)

        self.resource_string = self._get_resource_string()

    def __repr__(self) -> str:
        return self.arn

    def _get_resource_string(self) -> str:
        """Get the full resource string from the ARN."""
        parts = self.arn.split(":", 5)
        return parts[5] if len(parts) > 5 else ""

    def matches_resource_type(self, raw_arn: str) -> bool:
        """
        Check if this ARN matches a raw ARN format from the database.

        Args:
            raw_arn: A raw ARN format like 'arn:${Partition}:s3:::${BucketName}'.

        Returns:
            True if this ARN matches the raw ARN format.
        """
        if raw_arn == "*":
            return False

        db_elements = raw_arn.split(":", 5)
        if len(db_elements) < 6:
            return False

        if self.service != db_elements[2]:
            return False

        user_resource_type = get_resource_type(self.arn)
        if user_resource_type == "*":
            return True

        db_resource_string = db_elements[5]
        db_resource_parts = re.split(SEPARATOR_PATTERN, db_resource_string)
        arn_format_list = []

        for part in db_resource_parts:
            if "${" not in part:
                arn_format_list.append(part)
            else:
                arn_format_list.append("")

        user_resource_parts = re.split(SEPARATOR_PATTERN, self.resource_string)
        user_resource_lower = [p.lower() for p in user_resource_parts]

        for part in arn_format_list:
            if part and part.lower() not in user_resource_lower:
                return False

        for idx, part in enumerate(arn_format_list):
            if part:
                if idx >= len(user_resource_parts):
                    return False
                user_part = user_resource_parts[idx]
                if user_part != "*" and part.lower() != user_part.lower():
                    return False

        if db_resource_string in SPECIAL_RESOURCE_TYPES:
            if db_resource_string in ("table/${TableName}", "${BucketName}"):
                return len(self.resource_string.split("/")) == len(db_resource_string.split("/"))

            if "/" in self.resource_string and "/" in db_resource_string:
                return True
            if "/" not in self.resource_string and "/" not in db_resource_string:
                return True
            return False

        return True


def does_arn_match(user_arn: str, db_arn: str) -> bool:
    """
    Check if a user-supplied ARN matches a raw ARN format from the database.

    Args:
        user_arn: A user-supplied ARN like 'arn:aws:s3:::mybucket'.
        db_arn: A raw ARN format like 'arn:${Partition}:s3:::${BucketName}'.

    Returns:
        True if the ARNs match.
    """
    resource = ResourceArn(user_arn)
    return resource.matches_resource_type(db_arn)
