# Acceptance Criteria

(Updated before each feature implementation. Define what "done" means for each task.)

## Task 1: Implement IAM data loading and basic service querying

### Acceptance Criteria
- [x] Load IAM definition JSON file and access it as a dictionary
- [x] get_all_service_prefixes() returns all AWS service prefixes (e.g., 's3', 'ec2', 'iam')
- [x] get_service_data('s3') returns the full data dictionary for S3 service
- [x] get_actions_for_service('s3') returns all actions for S3 (e.g., 's3:GetObject', 's3:PutObject')
- [x] get_actions_for_service('s3', lowercase=True) returns actions in lowercase
- [x] Invalid service prefix returns empty results (not an error)
- [x] Schema version can be retrieved from the data

## Task 2: Implement ARN parsing and matching

### Acceptance Criteria
- [x] parse_arn("arn:aws:s3:::bucket") returns dict with partition, service, region, account, resource
- [x] get_service_from_arn("arn:aws:s3:::bucket") returns "s3"
- [x] ARN class can match user ARNs to raw ARN formats from the database
- [x] does_arn_match("arn:aws:s3:::mybucket", "arn:${Partition}:s3:::${BucketName}") returns True
- [x] does_arn_match distinguishes S3 bucket vs object ARNs correctly
- [x] does_arn_match handles complex ARN formats (DynamoDB tables vs backups, etc.)
- [x] Invalid ARN raises appropriate exception

## Task 3: Implement action querying

### Acceptance Criteria
- [ ] get_action_data('s3', 'GetObject') returns action metadata (access level, resource types, description)
- [ ] get_action_data('s3', '*') returns all S3 actions
- [ ] get_actions_with_access_level('s3', 'Read') returns all S3 read actions
- [ ] get_actions_with_access_level('all', 'Permissions management') returns all permission management actions across services
- [ ] get_actions_matching_arn_type('s3', 'bucket') returns actions that apply to S3 buckets
- [ ] get_actions_that_support_wildcard_arns_only('s3') returns actions that don't support resource constraints
- [ ] get_dependent_actions(['kms:CreateCustomKeyStore']) returns dependent actions
