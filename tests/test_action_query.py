"""Tests for action querying functionality."""

import pytest

from iam_policy_generator.action_query import (
    get_action_data,
    get_actions_with_access_level,
    get_actions_matching_arn_type,
    get_actions_with_arn_type_and_access_level,
    get_actions_that_support_wildcard_arns_only,
    get_actions_at_access_level_that_support_wildcard_arns_only,
    get_dependent_actions,
    filter_actions_by_access_level,
    filter_actions_to_wildcard_only,
)


class TestGetActionData:
    """Tests for get_action_data function."""

    def test_get_single_action_data(self):
        """Test getting data for a single action."""
        result = get_action_data("s3", "GetObject")
        assert "s3" in result
        assert len(result["s3"]) > 0

        entry = result["s3"][0]
        assert "action" in entry
        assert entry["action"] == "s3:GetObject"
        assert "access_level" in entry
        assert "description" in entry

    def test_get_all_actions_with_wildcard(self):
        """Test getting all actions with wildcard."""
        result = get_action_data("s3", "*")
        assert "s3" in result
        assert len(result["s3"]) > 10

    def test_get_actions_with_prefix_wildcard(self):
        """Test getting actions with prefix wildcard like 'Get*'."""
        result = get_action_data("s3", "Get*")
        assert "s3" in result
        for entry in result["s3"]:
            assert entry["action"].startswith("s3:Get")

    def test_action_data_has_access_level(self):
        """Test that action data includes access level."""
        result = get_action_data("s3", "GetObject")
        entry = result["s3"][0]
        assert entry["access_level"] == "Read"

    def test_action_data_has_resource_arn_format(self):
        """Test that action data includes resource ARN format."""
        result = get_action_data("s3", "GetObject")
        assert any(e["resource_arn_format"] != "*" for e in result["s3"])

    def test_invalid_service_returns_empty(self):
        """Test that invalid service returns empty dict."""
        result = get_action_data("nonexistent_xyz", "SomeAction")
        assert result == {}

    def test_invalid_action_returns_empty(self):
        """Test that invalid action returns empty dict."""
        result = get_action_data("s3", "NonexistentAction123")
        assert result == {} or result.get("s3") == []


class TestGetActionsWithAccessLevel:
    """Tests for get_actions_with_access_level function."""

    def test_get_read_actions_for_s3(self):
        """Test getting read actions for S3."""
        actions = get_actions_with_access_level("s3", "Read")
        assert len(actions) > 0
        assert any("GetObject" in a for a in actions)

    def test_get_write_actions_for_s3(self):
        """Test getting write actions for S3."""
        actions = get_actions_with_access_level("s3", "Write")
        assert len(actions) > 0
        assert any("PutObject" in a for a in actions)

    def test_get_permissions_management_for_all_services(self):
        """Test getting permissions management actions across all services."""
        actions = get_actions_with_access_level("all", "Permissions management")
        assert len(actions) > 50
        services = set(a.split(":")[0] for a in actions)
        assert len(services) > 5

    def test_get_list_actions_for_ec2(self):
        """Test getting list actions for EC2."""
        actions = get_actions_with_access_level("ec2", "List")
        assert len(actions) > 0
        for action in actions:
            assert action.startswith("ec2:")


class TestGetActionsMatchingArnType:
    """Tests for get_actions_matching_arn_type function."""

    def test_get_bucket_actions_for_s3(self):
        """Test getting actions that apply to S3 buckets."""
        actions = get_actions_matching_arn_type("s3", "bucket")
        assert len(actions) > 0
        assert any("DeleteBucket" in a for a in actions)

    def test_get_object_actions_for_s3(self):
        """Test getting actions that apply to S3 objects."""
        actions = get_actions_matching_arn_type("s3", "object")
        assert len(actions) > 0
        assert any("GetObject" in a for a in actions)

    def test_wildcard_returns_wildcard_only_actions(self):
        """Test that '*' returns wildcard-only actions."""
        actions = get_actions_matching_arn_type("s3", "*")
        wildcard_only = get_actions_that_support_wildcard_arns_only("s3")
        assert actions == wildcard_only


class TestGetActionsWithArnTypeAndAccessLevel:
    """Tests for get_actions_with_arn_type_and_access_level function."""

    def test_get_bucket_write_actions(self):
        """Test getting write actions for S3 buckets."""
        actions = get_actions_with_arn_type_and_access_level("s3", "bucket", "Write")
        assert len(actions) > 0
        for action in actions:
            assert action.startswith("s3:")

    def test_get_permissions_management_for_key(self):
        """Test getting permissions management actions for KMS keys."""
        actions = get_actions_with_arn_type_and_access_level("kms", "key", "Permissions management")
        assert len(actions) > 0
        assert any("PutKeyPolicy" in a for a in actions)


class TestGetActionsWildcardOnly:
    """Tests for wildcard-only action functions."""

    def test_get_wildcard_only_actions(self):
        """Test getting actions that only support wildcard ARNs."""
        actions = get_actions_that_support_wildcard_arns_only("s3")
        assert len(actions) > 0

        for action in actions:
            service, name = action.split(":")
            data = get_action_data(service, name)
            assert all(e["resource_arn_format"] == "*" for e in data.get(service, []))

    def test_wildcard_only_at_access_level(self):
        """Test getting wildcard-only actions at a specific access level."""
        actions = get_actions_at_access_level_that_support_wildcard_arns_only("s3", "List")
        for action in actions:
            assert action.startswith("s3:")


class TestGetDependentActions:
    """Tests for get_dependent_actions function."""

    def test_get_dependent_actions_for_kms_create_keystore(self):
        """Test getting dependent actions for kms:CreateCustomKeyStore."""
        deps = get_dependent_actions(["kms:CreateCustomKeyStore"])
        assert len(deps) > 0
        assert any("cloudhsm" in d.lower() for d in deps)

    def test_no_dependent_actions(self):
        """Test action with no dependencies returns empty list."""
        deps = get_dependent_actions(["s3:GetObject"])
        # GetObject typically doesn't have dependencies

    def test_multiple_actions_dependent_actions(self):
        """Test getting dependencies for multiple actions."""
        deps = get_dependent_actions(["kms:CreateCustomKeyStore", "s3:GetObject"])
        assert isinstance(deps, list)


class TestFilterActions:
    """Tests for action filtering functions."""

    def test_filter_by_access_level(self):
        """Test filtering actions by access level."""
        actions = ["s3:GetObject", "s3:PutObject", "s3:DeleteBucket"]
        read_actions = filter_actions_by_access_level(actions, "Read")
        assert "s3:GetObject" in read_actions
        assert "s3:PutObject" not in read_actions

    def test_filter_wildcard_action_to_all(self):
        """Test filtering wildcard to all actions at access level."""
        read_actions = filter_actions_by_access_level(["*"], "Read")
        assert len(read_actions) > 100

    def test_filter_to_wildcard_only(self):
        """Test filtering to wildcard-only actions."""
        # Get some actions that include both wildcard-only and resource-constrained
        actions = ["s3:GetObject", "s3:ListBuckets", "ec2:DescribeInstances"]
        wildcard_only = filter_actions_to_wildcard_only(actions)
        for action in wildcard_only:
            service, name = action.split(":")
            data = get_action_data(service, name)
            assert all(e["resource_arn_format"] == "*" for e in data.get(service, []))
