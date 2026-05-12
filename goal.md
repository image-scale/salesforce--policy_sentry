# Goal

## Project
policy_sentry — a python project.

## Description
Policy Sentry is an IAM Least Privilege Policy Generator for AWS. It helps users create secure, least-privilege IAM policies based on resource ARNs and access levels (Read, Write, List, Tagging, Permissions management). The tool leverages AWS IAM documentation to look up actions, access levels, and resource types, and generates policies accordingly.

Core capabilities:
1. **IAM Database Querying** - Query AWS IAM data to look up actions, ARNs, and condition keys for any AWS service
2. **Policy Generation (CRUD Mode)** - Generate IAM policies based on resource ARNs and access levels
3. **Policy Generation (Actions Mode)** - Generate IAM policies from a list of specific IAM actions
4. **Template Creation** - Create YAML templates for policy specification
5. **ARN Matching** - Match user-supplied ARNs to raw ARN formats in the database
6. **Action Expansion** - Expand wildcard actions (e.g., s3:Get*) to full action lists
7. **Policy Analysis** - Analyze policies by access level
8. **Policy Minimization** - Minimize policy size using wildcards when needed

## Scope
- ~15 production source files to implement
- ~10 test files to write
- Reproduce core source code, tests, and configuration
