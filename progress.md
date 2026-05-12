# Progress

(Updated after each feature commit.)

## Round 1
**Task**: Task 1 — Implement IAM data loading and basic service querying
**Files created**: iam_policy_generator/__init__.py, iam_policy_generator/iam_data.py, iam_policy_generator/data/iam-definition.json, tests/test_iam_data.py, pyproject.toml
**Commit**: Add IAM data loading and service querying functionality
**Acceptance**: 7/7 criteria met
**Verification**: tests FAIL on previous state, PASS on current state

## Round 2
**Task**: Task 2 — Implement ARN parsing and matching
**Files created**: iam_policy_generator/arn_utils.py, tests/test_arn_utils.py
**Commit**: Add ARN parsing and matching functionality
**Acceptance**: 7/7 criteria met
**Verification**: tests FAIL on previous state, PASS on current state

## Round 3
**Task**: Task 3 — Implement action querying
**Files created**: iam_policy_generator/action_query.py, tests/test_action_query.py
**Commit**: Add action querying functionality for IAM actions
**Acceptance**: 7/7 criteria met
**Verification**: tests FAIL on previous state, PASS on current state
