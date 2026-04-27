"""Parse pytest verbose output into per-test results."""
from __future__ import annotations

import re


def parse_log(log: str) -> dict[str, str]:
    """Parse test runner output into per-test results.

    Args:
        log: Full stdout+stderr output of `bash run_test.sh 2>&1`.

    Returns:
        Dict mapping test_id to status.
        - test_id: pytest native format (e.g. "tests/foo.py::TestClass::test_func[param]")
        - status: one of "PASSED", "FAILED", "SKIPPED", "ERROR"
        - Must include ALL tests that appear in the output, not just failures.
    """
    results: dict[str, str] = {}

    # Match pytest verbose lines like:
    # test/util/test_arns.py::ArnsTestCase::test_parse_arn PASSED  [ 64%]
    # Handles PASSED, FAILED, SKIPPED, ERROR, XFAIL, XPASS
    test_line_re = re.compile(
        r"^(\S+::\S+)\s+(PASSED|FAILED|SKIPPED|ERROR|XFAIL|XPASS)\s*(?:\[.*\])?\s*$"
    )

    # Match collection errors like: ERROR tests/foo.py
    collection_error_re = re.compile(
        r"^ERROR\s+([\w/\\.]+\.py)\b"
    )

    for line in log.splitlines():
        line = line.strip()

        m = test_line_re.match(line)
        if m:
            test_id = m.group(1)
            status = m.group(2)
            # Normalize XFAIL/XPASS
            if status == "XFAIL":
                status = "SKIPPED"
            elif status == "XPASS":
                status = "PASSED"
            results[test_id] = status
            continue

        m = collection_error_re.match(line)
        if m:
            module_path = m.group(1)
            results[module_path] = "ERROR"

    return results

