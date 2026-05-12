# Acceptance Criteria

(Updated before each feature implementation. Define what "done" means for each task.)

## Task 1: Implement IAM data loading and basic service querying

### Acceptance Criteria
- [ ] Load IAM definition JSON file and access it as a dictionary
- [ ] get_all_service_prefixes() returns all AWS service prefixes (e.g., 's3', 'ec2', 'iam')
- [ ] get_service_data('s3') returns the full data dictionary for S3 service
- [ ] get_actions_for_service('s3') returns all actions for S3 (e.g., 's3:GetObject', 's3:PutObject')
- [ ] get_actions_for_service('s3', lowercase=True) returns actions in lowercase
- [ ] Invalid service prefix returns empty results (not an error)
- [ ] Schema version can be retrieved from the data
