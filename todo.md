# Todo

## Plan
Build the core IAM policy generator from the ground up. Start with the data layer that loads and queries the IAM definition database, then build ARN parsing utilities, then implement action and condition querying, then add policy generation capabilities (SidGroup/policy writer), and finally add analysis/expansion features. Each task delivers user-facing functionality with tests.

## Tasks
- [x] Task 1: Implement IAM data loading and basic service querying (load iam-definition.json, get service prefixes, get actions for a service)
- [>] Task 2: Implement ARN parsing and matching (parse ARNs, match user ARNs to database ARN formats)
- [ ] Task 3: Implement action querying (get action data, filter by access level, filter by resource type)
- [ ] Task 4: Implement condition key querying (get condition keys for service, get condition key details)
- [ ] Task 5: Implement action expansion and wildcard handling (expand wildcards like s3:Get* to full actions)
- [ ] Task 6: Implement policy template generation (CRUD and Actions mode templates)
- [ ] Task 7: Implement SidGroup and policy rendering (group actions by SID, render IAM policy JSON)
- [ ] Task 8: Implement CRUD mode policy generation (generate policies from ARNs and access levels)
- [ ] Task 9: Implement Actions mode policy generation (generate policies from action lists)
- [ ] Task 10: Implement policy analysis (analyze policies by access level)
- [ ] Task 11: Implement policy minimization (reduce policy size with safe wildcards)
- [ ] Task 12: Implement CLI interface (command-line tool with write-policy, query, create-template commands)
