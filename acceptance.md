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
- [ ] parse_arn("arn:aws:s3:::bucket") returns dict with partition, service, region, account, resource
- [ ] get_service_from_arn("arn:aws:s3:::bucket") returns "s3"
- [ ] ARN class can match user ARNs to raw ARN formats from the database
- [ ] does_arn_match("arn:aws:s3:::mybucket", "arn:${Partition}:s3:::${BucketName}") returns True
- [ ] does_arn_match distinguishes S3 bucket vs object ARNs correctly
- [ ] does_arn_match handles complex ARN formats (DynamoDB tables vs backups, etc.)
- [ ] Invalid ARN raises appropriate exception
