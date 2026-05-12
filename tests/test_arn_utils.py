"""Tests for ARN parsing and matching utilities."""

import pytest

from iam_policy_generator.arn_utils import (
    parse_arn,
    get_service_from_arn,
    get_region_from_arn,
    get_account_from_arn,
    get_resource_string,
    get_resource_type,
    ResourceArn,
    does_arn_match,
    InvalidArnError,
)


class TestParseArn:
    """Tests for ARN parsing."""

    def test_parse_simple_s3_bucket_arn(self):
        """Test parsing a simple S3 bucket ARN."""
        result = parse_arn("arn:aws:s3:::mybucket")
        assert result["partition"] == "aws"
        assert result["service"] == "s3"
        assert result["region"] == ""
        assert result["account"] == ""
        assert result["resource"] == "mybucket"

    def test_parse_ec2_instance_arn(self):
        """Test parsing an EC2 instance ARN."""
        result = parse_arn("arn:aws:ec2:us-east-1:123456789012:instance/i-1234567890abcdef0")
        assert result["partition"] == "aws"
        assert result["service"] == "ec2"
        assert result["region"] == "us-east-1"
        assert result["account"] == "123456789012"
        assert result["resource"] == "instance"
        assert result["resource_path"] == "i-1234567890abcdef0"

    def test_parse_ssm_parameter_arn(self):
        """Test parsing an SSM parameter ARN."""
        result = parse_arn("arn:aws:ssm:us-east-1:123456789012:parameter/test")
        assert result["service"] == "ssm"
        assert result["resource"] == "parameter"
        assert result["resource_path"] == "test"

    def test_parse_arn_with_colon_separator(self):
        """Test parsing an ARN with colon separator in resource."""
        result = parse_arn("arn:aws:states:us-east-1:123456789012:stateMachine:myMachine")
        assert result["resource"] == "stateMachine"
        assert result["resource_path"] == "myMachine"

    def test_invalid_arn_raises_error(self):
        """Test that invalid ARN raises InvalidArnError."""
        with pytest.raises(InvalidArnError):
            parse_arn("invalid")


class TestGetServiceFromArn:
    """Tests for extracting service from ARN."""

    def test_get_service_s3(self):
        """Test extracting S3 service."""
        assert get_service_from_arn("arn:aws:s3:::mybucket") == "s3"

    def test_get_service_ec2(self):
        """Test extracting EC2 service."""
        assert get_service_from_arn("arn:aws:ec2:us-east-1:123456789012:instance/i-123") == "ec2"

    def test_get_service_iam(self):
        """Test extracting IAM service."""
        assert get_service_from_arn("arn:aws:iam::123456789012:role/myrole") == "iam"


class TestGetRegionFromArn:
    """Tests for extracting region from ARN."""

    def test_get_region_with_region(self):
        """Test extracting region when present."""
        assert get_region_from_arn("arn:aws:ec2:us-east-1:123456789012:instance/i-123") == "us-east-1"

    def test_get_region_empty_for_s3(self):
        """Test that S3 buckets return empty region."""
        assert get_region_from_arn("arn:aws:s3:::mybucket") == ""


class TestGetAccountFromArn:
    """Tests for extracting account from ARN."""

    def test_get_account_with_account(self):
        """Test extracting account when present."""
        assert get_account_from_arn("arn:aws:ec2:us-east-1:123456789012:instance/i-123") == "123456789012"

    def test_get_account_empty_for_s3(self):
        """Test that S3 buckets return empty account."""
        assert get_account_from_arn("arn:aws:s3:::mybucket") == ""


class TestGetResourceString:
    """Tests for getting resource string."""

    def test_get_resource_string_simple(self):
        """Test getting simple resource string."""
        assert get_resource_string("arn:aws:s3:::mybucket") == "mybucket"

    def test_get_resource_string_with_path(self):
        """Test getting resource string with path."""
        assert get_resource_string("arn:aws:s3:::mybucket/mykey") == "mybucket/mykey"


class TestGetResourceType:
    """Tests for extracting resource type."""

    def test_get_resource_type_parameter(self):
        """Test extracting parameter resource type."""
        assert get_resource_type("arn:aws:ssm:us-east-1:123456789012:parameter/test") == "parameter"

    def test_get_resource_type_instance(self):
        """Test extracting instance resource type."""
        assert get_resource_type("arn:aws:ec2:us-east-1:123456789012:instance/i-123") == "instance"

    def test_get_resource_type_none_for_bucket(self):
        """Test that S3 bucket has no resource type prefix."""
        assert get_resource_type("arn:aws:s3:::mybucket") is None


class TestResourceArnClass:
    """Tests for ResourceArn class."""

    def test_create_resource_arn(self):
        """Test creating a ResourceArn object."""
        arn = ResourceArn("arn:aws:s3:::mybucket")
        assert arn.service == "s3"
        assert arn.partition == "aws"

    def test_invalid_arn_raises_error(self):
        """Test that invalid ARN raises error."""
        with pytest.raises(InvalidArnError):
            ResourceArn("not-an-arn")


class TestDoesArnMatch:
    """Tests for ARN matching."""

    def test_s3_bucket_matches(self):
        """Test S3 bucket matches bucket ARN format."""
        user_arn = "arn:aws:s3:::mybucket"
        db_arn = "arn:${Partition}:s3:::${BucketName}"
        assert does_arn_match(user_arn, db_arn) is True

    def test_s3_object_matches_object_format(self):
        """Test S3 object matches object ARN format."""
        user_arn = "arn:aws:s3:::mybucket/mykey"
        db_arn = "arn:${Partition}:s3:::${BucketName}/${ObjectName}"
        assert does_arn_match(user_arn, db_arn) is True

    def test_s3_object_does_not_match_bucket_format(self):
        """Test S3 object does NOT match bucket ARN format."""
        user_arn = "arn:aws:s3:::mybucket/mykey"
        db_arn = "arn:${Partition}:s3:::${BucketName}"
        assert does_arn_match(user_arn, db_arn) is False

    def test_s3_bucket_does_not_match_object_format(self):
        """Test S3 bucket does NOT match object ARN format."""
        user_arn = "arn:aws:s3:::mybucket"
        db_arn = "arn:${Partition}:s3:::${BucketName}/${ObjectName}"
        assert does_arn_match(user_arn, db_arn) is False

    def test_ssm_parameter_matches(self):
        """Test SSM parameter matches parameter format."""
        user_arn = "arn:aws:ssm:us-east-1:123456789012:parameter/test"
        db_arn = "arn:${Partition}:ssm:${Region}:${Account}:parameter/${FullyQualifiedParameterName}"
        assert does_arn_match(user_arn, db_arn) is True

    def test_codecommit_repo_matches(self):
        """Test CodeCommit repository ARN matches."""
        user_arn = "arn:aws:codecommit:us-east-1:123456789012:MyDemoRepo"
        db_arn = "arn:${Partition}:codecommit:${Region}:${Account}:${RepositoryName}"
        assert does_arn_match(user_arn, db_arn) is True

    def test_different_services_dont_match(self):
        """Test ARNs from different services don't match."""
        user_arn = "arn:aws:s3:::mybucket"
        db_arn = "arn:${Partition}:ec2:${Region}:${Account}:instance/${InstanceId}"
        assert does_arn_match(user_arn, db_arn) is False

    def test_wildcard_arn_does_not_match(self):
        """Test that wildcard '*' raw ARN returns False."""
        user_arn = "arn:aws:s3:::mybucket"
        assert does_arn_match(user_arn, "*") is False

    def test_dynamodb_table_matches_table_format(self):
        """Test DynamoDB table matches table format."""
        user_arn = "arn:aws:dynamodb:us-east-1:123456789123:table/mytable"
        db_table = "arn:${Partition}:dynamodb:${Region}:${Account}:table/${TableName}"
        assert does_arn_match(user_arn, db_table) is True

    def test_dynamodb_table_does_not_match_index(self):
        """Test DynamoDB table does NOT match index format."""
        user_arn = "arn:aws:dynamodb:us-east-1:123456789123:table/mytable"
        db_index = "arn:${Partition}:dynamodb:${Region}:${Account}:table/${TableName}/index/${IndexName}"
        assert does_arn_match(user_arn, db_index) is False

    def test_dynamodb_table_does_not_match_backup(self):
        """Test DynamoDB table does NOT match backup format."""
        user_arn = "arn:aws:dynamodb:us-east-1:123456789123:table/mytable"
        db_backup = "arn:${Partition}:dynamodb:${Region}:${Account}:table/${TableName}/backup/${BackupName}"
        assert does_arn_match(user_arn, db_backup) is False

    def test_batch_job_definition_matches(self):
        """Test Batch job definition with revision matches."""
        user_arn = "arn:aws:batch:region:account-id:job-definition/job-name:revision"
        db_arn = "arn:${Partition}:batch:${Region}:${Account}:job-definition/${JobDefinitionName}:${Revision}"
        assert does_arn_match(user_arn, db_arn) is True

    def test_states_statemachine_matches(self):
        """Test Step Functions state machine ARN matches."""
        user_arn = "arn:aws:states:region:account-id:stateMachine:stateMachineName"
        db_arn = "arn:${Partition}:states:${Region}:${Account}:stateMachine:${StateMachineName}"
        assert does_arn_match(user_arn, db_arn) is True

    def test_resource_wildcard_matches(self):
        """Test resource type wildcard matches any resource type."""
        user_arn = "arn:${Partition}:rds:${Region}:${Account}:*:*"
        db_arn = "arn:${Partition}:rds:${Region}:${Account}:db:${DbInstanceName}"
        assert does_arn_match(user_arn, db_arn) is True

    def test_rds_db_does_not_match_cluster(self):
        """Test RDS db instance does not match cluster format."""
        user_arn = "arn:${Partition}:rds:${Region}:${Account}:cluster:${DbClusterInstanceName}"
        db_arn = "arn:${Partition}:rds:${Region}:${Account}:db:${DbInstanceName}"
        assert does_arn_match(user_arn, db_arn) is False
