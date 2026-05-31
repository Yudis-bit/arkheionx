"""Conservative parser for `forge test` output.

Extracts only what is plainly present in the text. It never infers token
balance deltas or invents state changes.
"""
from __future__ import annotations

import re

_MAX_CALLS = 40
_MAX_LOGS = 20


def parse_forge_output(text: str) -> dict:
    text = text or ""
    passed = len(re.findall(r"\[PASS\]", text))
    failed = len(re.findall(r"\[FAIL", text))
    skipped = len(re.findall(r"\[SKIP\]", text))

    if passed == 0 and failed == 0 and skipped == 0:
        # Fall back to the suite summary line(s): "N passed; M failed; K skipped".
        for p, f, s in re.findall(r"(\d+)\s+passed;\s+(\d+)\s+failed;\s+(\d+)\s+skipped", text):
            passed += int(p)
            failed += int(f)
            skipped += int(s)

    failing_tests = re.findall(r"\[FAIL[^\]]*\]\s*([A-Za-z_][A-Za-z0-9_]*)", text)
    skipped_tests = re.findall(r"\[SKIP[^\]]*\]\s*([A-Za-z_][A-Za-z0-9_]*)", text)
    reverts = re.findall(r"\[FAIL:\s*([^\]]+)\]", text)
    assertion_failures = sorted({
        line.strip()
        for line in text.splitlines()
        if re.search(r"assertion failed|!= expected|not satisfied|panic:", line, re.IGNORECASE)
    })[:20]
    call_sequence = [
        re.sub(r"\s+", " ", line.strip())
        for line in text.splitlines()
        if "::" in line and "(" in line
    ][:_MAX_CALLS]
    logs = [line.strip() for line in text.splitlines() if line.strip().startswith("emit ")][:_MAX_LOGS]

    return {
        "tests_run": passed + failed + skipped,
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "failing_tests": sorted(set(failing_tests)),
        "skipped_tests": sorted(set(skipped_tests)),
        "reverts": reverts,
        "assertion_failures": assertion_failures,
        "call_sequence": call_sequence,
        "logs": logs,
        "limitations": [
            "Conservative parse of forge output; only explicit results are reported.",
            "Token balance and state deltas are not inferred.",
        ],
    }
