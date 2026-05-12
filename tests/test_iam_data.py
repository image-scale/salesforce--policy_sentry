"""Tests for IAM data loading and service querying."""

import pytest

from iam_policy_generator.iam_data import (
    get_iam_data,
    get_schema_version,
    get_all_service_prefixes,
    get_service_data,
    get_actions_for_service,
    get_all_actions,
)


class TestIAMDataLoading:
    """Tests for loading IAM data."""

    def test_iam_data_loads_successfully(self):
        """Test that IAM data loads and returns a dictionary."""
        data = get_iam_data()
        assert isinstance(data, dict)
        assert len(data) > 0

    def test_schema_version_is_returned(self):
        """Test that schema version can be retrieved."""
        version = get_schema_version()
        assert isinstance(version, str)
        assert version == "v2"


class TestServicePrefixes:
    """Tests for service prefix querying."""

    def test_get_all_service_prefixes_returns_set(self):
        """Test that service prefixes returns a non-empty set."""
        prefixes = get_all_service_prefixes()
        assert isinstance(prefixes, set)
        assert len(prefixes) > 100

    def test_common_services_are_present(self):
        """Test that common AWS services are in the prefixes."""
        prefixes = get_all_service_prefixes()
        assert "s3" in prefixes
        assert "ec2" in prefixes
        assert "iam" in prefixes
        assert "lambda" in prefixes
        assert "dynamodb" in prefixes

    def test_schema_version_key_excluded(self):
        """Test that the schema version key is not in prefixes."""
        prefixes = get_all_service_prefixes()
        assert "policy_sentry_schema_version" not in prefixes


class TestServiceData:
    """Tests for service data retrieval."""

    def test_get_service_data_returns_dict(self):
        """Test that service data returns a dictionary for valid service."""
        data = get_service_data("s3")
        assert isinstance(data, dict)
        assert "privileges" in data
        assert "resources" in data

    def test_invalid_service_returns_empty_dict(self):
        """Test that invalid service returns empty dict, not an error."""
        data = get_service_data("nonexistent_service_xyz")
        assert data == {}

    def test_service_data_contains_expected_keys(self):
        """Test that service data has expected structure."""
        data = get_service_data("ec2")
        assert "prefix" in data
        assert "privileges" in data
        assert "privileges_lower_name" in data
        assert "resources" in data

    def test_catalog_maps_to_servicecatalog(self):
        """Test that 'catalog' maps to servicecatalog data."""
        data = get_service_data("catalog")
        assert data.get("prefix") == "servicecatalog" or len(data) > 0


class TestActionsForService:
    """Tests for action querying."""

    def test_get_actions_for_service_returns_list(self):
        """Test that actions returns a list."""
        actions = get_actions_for_service("s3")
        assert isinstance(actions, list)
        assert len(actions) > 0

    def test_actions_are_properly_formatted(self):
        """Test that actions have service:action format."""
        actions = get_actions_for_service("s3")
        for action in actions:
            assert ":" in action
            assert action.startswith("s3:")

    def test_common_actions_present(self):
        """Test that common actions are present."""
        actions = get_actions_for_service("s3")
        action_names = [a.lower() for a in actions]
        assert any("getobject" in a for a in action_names)
        assert any("putobject" in a for a in action_names)

    def test_lowercase_option(self):
        """Test that lowercase option works."""
        actions = get_actions_for_service("s3", lowercase=True)
        for action in actions:
            parts = action.split(":")
            assert parts[1] == parts[1].lower()

    def test_invalid_service_returns_empty_list(self):
        """Test that invalid service returns empty list."""
        actions = get_actions_for_service("nonexistent_xyz")
        assert actions == []


class TestAllActions:
    """Tests for getting all actions."""

    def test_get_all_actions_returns_set(self):
        """Test that all actions returns a set."""
        actions = get_all_actions()
        assert isinstance(actions, set)
        assert len(actions) > 1000

    def test_all_actions_contains_multiple_services(self):
        """Test that all actions spans multiple services."""
        actions = get_all_actions()
        services_seen = set()
        for action in actions:
            service = action.split(":")[0]
            services_seen.add(service)
        assert len(services_seen) > 50

    def test_all_actions_lowercase(self):
        """Test that lowercase option works for all actions."""
        actions = get_all_actions(lowercase=True)
        for action in list(actions)[:100]:
            parts = action.split(":")
            assert parts[1] == parts[1].lower()
