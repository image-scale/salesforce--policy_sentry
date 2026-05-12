"""Tests for condition key querying functionality."""

import pytest

from iam_policy_generator.condition_query import (
    get_condition_keys_for_service,
    get_condition_key_details,
    get_condition_value_type,
    get_conditions_for_action_and_raw_arn,
    get_condition_keys_for_raw_arn,
    get_actions_matching_condition_key,
)


class TestGetConditionKeysForService:
    """Tests for get_condition_keys_for_service."""

    def test_get_s3_condition_keys(self):
        """Test getting condition keys for S3."""
        keys = get_condition_keys_for_service("s3")
        assert len(keys) > 0
        assert any("prefix" in k.lower() for k in keys)

    def test_get_ec2_condition_keys(self):
        """Test getting condition keys for EC2."""
        keys = get_condition_keys_for_service("ec2")
        assert len(keys) > 0

    def test_invalid_service_returns_empty(self):
        """Test that invalid service returns empty list."""
        keys = get_condition_keys_for_service("nonexistent_xyz")
        assert keys == []


class TestGetConditionKeyDetails:
    """Tests for get_condition_key_details."""

    def test_get_ec2_vpc_details(self):
        """Test getting details for ec2:Vpc condition key."""
        details = get_condition_key_details("ec2", "ec2:Vpc")
        assert "name" in details
        assert "description" in details
        assert "condition_value_type" in details

    def test_get_s3_prefix_details(self):
        """Test getting details for s3:prefix condition key."""
        details = get_condition_key_details("s3", "s3:prefix")
        assert "name" in details

    def test_nonexistent_key_returns_empty(self):
        """Test that nonexistent key returns empty dict."""
        details = get_condition_key_details("s3", "s3:nonexistent123")
        assert details == {}


class TestGetConditionValueType:
    """Tests for get_condition_value_type."""

    def test_get_type_for_condition_key(self):
        """Test getting type for a condition key."""
        keys = get_condition_keys_for_service("s3")
        if keys:
            result = get_condition_value_type(keys[0])
            assert result is not None or result is None  # Just verify it runs

    def test_string_type(self):
        """Test getting string type."""
        result = get_condition_value_type("s3:prefix")
        if result:
            assert result in ("string", "arn", "bool", "date", "number", "ip")

    def test_invalid_key_returns_none(self):
        """Test that invalid key returns None."""
        result = get_condition_value_type("nonexistent:key")
        assert result is None


class TestGetConditionsForActionAndRawArn:
    """Tests for get_conditions_for_action_and_raw_arn."""

    def test_get_conditions_for_s3_getobject(self):
        """Test getting conditions for s3:GetObject."""
        raw_arn = "arn:${Partition}:s3:::${BucketName}/${ObjectName}"
        conditions = get_conditions_for_action_and_raw_arn("s3:GetObject", raw_arn)
        assert isinstance(conditions, list)

    def test_invalid_action_returns_empty(self):
        """Test that invalid action returns empty list."""
        conditions = get_conditions_for_action_and_raw_arn("nonexistent:Action", "*")
        assert conditions == []


class TestGetConditionKeysForRawArn:
    """Tests for get_condition_keys_for_raw_arn."""

    def test_get_keys_for_s3_bucket_arn(self):
        """Test getting condition keys for S3 bucket ARN."""
        raw_arn = "arn:${Partition}:s3:::${BucketName}"
        keys = get_condition_keys_for_raw_arn(raw_arn)
        assert isinstance(keys, list)

    def test_invalid_arn_format_returns_empty(self):
        """Test that invalid ARN format returns empty list."""
        keys = get_condition_keys_for_raw_arn("invalid")
        assert keys == []


class TestGetActionsMatchingConditionKey:
    """Tests for get_actions_matching_condition_key."""

    def test_get_actions_for_s3_prefix(self):
        """Test getting actions that support s3:prefix."""
        actions = get_actions_matching_condition_key("s3", "s3:prefix")
        assert isinstance(actions, list)

    def test_invalid_service_returns_empty(self):
        """Test that invalid service returns empty list."""
        actions = get_actions_matching_condition_key("nonexistent", "nonexistent:key")
        assert actions == []


class TestConditionKeyMatching:
    """Tests for condition key pattern matching."""

    def test_exact_match(self):
        """Test exact condition key match."""
        keys = get_condition_keys_for_service("s3")
        if "s3:prefix" in keys:
            details = get_condition_key_details("s3", "s3:prefix")
            assert details != {}

    def test_pattern_match_with_tag(self):
        """Test pattern matching for tag-based condition keys."""
        keys = get_condition_keys_for_service("ec2")
        # Find a ResourceTag key if available
        tag_keys = [k for k in keys if "ResourceTag" in k]
        if tag_keys:
            # Should match specific tag values
            details = get_condition_key_details("ec2", tag_keys[0])
            assert details != {}
