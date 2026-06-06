"""Conservative parser for saved Foundry / local validation output (v3.7, additive).

Converts saved ``forge test`` output into ``LocalTestResult`` records. It prefers
a saved structured (``forge test --json``) document and falls back to a
conservative line-based text parse. It never shells out, never calls ``forge``,
never reads or writes files, requires no Foundry install, and performs no RPC or
network access. Importing it has no filesystem side effects.

The parser only extracts what is plainly present: exact test names, pass / fail /
skip / error status, and gas / duration when available. It assigns no IDs, links
nothing to the Protocol Intelligence Model, invents nothing, and makes no
vulnerability, severity, audit, or bounty claim. Unrecognized content becomes a
warning, never a fabricated result.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

from .model import (
    SUPPORT_NONE,
    TEST_ERROR,
    TEST_FAILED,
    TEST_PASSED,
    TEST_SKIPPED,
    TEST_UNKNOWN,
    LocalTestResult,
    to_dict,
)

FOUNDRY_JSON = "foundry_json"
FOUNDRY_TEXT = "foundry_text"
FOUNDRY_UNKNOWN = "foundry_unknown"

_STATUS_MAP = {
    "pass": TEST_PASSED, "passed": TEST_PASSED, "success": TEST_PASSED, "ok": TEST_PASSED,
    "fail": TEST_FAILED, "failed": TEST_FAILED, "failure": TEST_FAILED,
    "skip": TEST_SKIPPED, "skipped": TEST_SKIPPED,
    "error": TEST_ERROR, "errored": TEST_ERROR,
}

_TEXT_LINE_RE = re.compile(
    r"^\s*\[(PASS|FAIL|SKIP|ERROR)[^\]]*\]\s+([A-Za-z_]\w*\s*\([^)]*\))(?:\s*\(gas:\s*([0-9]+)\))?"
)
_SUITE_RE = re.compile(r"^\s*Ran\s+\d+\s+tests?\s+for\s+(\S+)")
_UNKNOWN_MARKER_RE = re.compile(r"^\s*\[[A-Za-z]")


@dataclass
class ParsedFoundryOutput:
    tool: str = "foundry"
    source_format: str = ""
    test_results: list[LocalTestResult] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    metadata: dict[str, object] = field(default_factory=dict)


def foundry_status_to_local_status(value: str) -> str:
    return _STATUS_MAP.get(str(value or "").strip().lower(), TEST_UNKNOWN)


def extract_gas_used(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        text = value.strip().replace("_", "").replace(",", "")
        return int(text) if text.isdigit() else None
    if isinstance(value, dict):
        unit = value.get("Unit")
        if isinstance(unit, dict) and "gas" in unit:
            return extract_gas_used(unit["gas"])
        if "gas" in value:
            return extract_gas_used(value["gas"])
    return None


def extract_duration_ms(value: object) -> int | None:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, dict):
        if "secs" in value or "nanos" in value:
            try:
                secs = int(value.get("secs", 0) or 0)
                nanos = int(value.get("nanos", 0) or 0)
            except (TypeError, ValueError):
                return None
            return secs * 1000 + nanos // 1_000_000
        return None
    text = str(value).strip().lower()
    match = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*(ms|s|us|ns)?$", text)
    if not match:
        return None
    number = float(match.group(1))
    factor = {"ms": 1.0, "s": 1000.0, "us": 0.001, "ns": 1e-6}[match.group(2) or "ms"]
    return int(number * factor)


def split_foundry_test_identifier(value: str) -> tuple[str, str]:
    """Return (contract_name, function_name) from a Foundry test identifier.

    Splits exactly (file prefix dropped at the first ``:``); never guesses. An
    ambiguous or unrecognized token yields an empty contract or function.
    """

    text = str(value or "").strip()
    if not text:
        return "", ""
    after_colon = text.split(":", 1)[1] if ":" in text else text
    if "." in after_colon:
        contract, function = after_colon.rsplit(".", 1)
    elif after_colon.endswith("()") or after_colon.startswith(("test", "invariant", "prove", "statefulFuzz")):
        contract, function = "", after_colon
    elif re.search(r"\s", after_colon):
        contract, function = "", ""
    else:
        contract, function = after_colon, ""
    if function.endswith("()"):
        function = function[:-2]
    return contract.strip(), function.strip()


def _names(suite: str, test_name: str, entry: dict) -> tuple[str, str]:
    contract = str(entry.get("contract") or entry.get("contract_name") or "")
    function = str(entry.get("function") or entry.get("function_name") or "")
    if not contract and suite:
        contract = split_foundry_test_identifier(suite)[0]
    if not function:
        function = split_foundry_test_identifier(test_name)[1]
    return contract, function


def _entry_name(entry: dict) -> str:
    return str(entry.get("test_name") or entry.get("name") or entry.get("test") or "")


def _gas_from_entry(entry: dict) -> int | None:
    for candidate in (entry.get("gas_used"), entry.get("gas"), entry.get("kind")):
        if candidate is not None:
            gas = extract_gas_used(candidate)
            if gas is not None:
                return gas
    return None


def _duration_from_entry(entry: dict) -> int | None:
    for key in ("duration_ms", "duration"):
        if key in entry and entry[key] is not None:
            value = extract_duration_ms(entry[key])
            if value is not None:
                return value
    return None


def _build_result(suite: str, test_name: str, entry: dict, run_id: str, tool: str) -> LocalTestResult:
    contract, function = _names(suite, test_name, entry)
    return LocalTestResult(
        run_id=run_id,
        tool=tool,
        test_name=test_name,
        contract_name=contract,
        function_name=function,
        selector=str(entry.get("selector", "") or ""),
        status=foundry_status_to_local_status(entry.get("status", "")),
        duration_ms=_duration_from_entry(entry),
        gas_used=_gas_from_entry(entry),
        file_path=str(entry.get("file_path", "") or ""),
        evidence_support=SUPPORT_NONE,
    )


def _collect_test_entries(payload: object, out: ParsedFoundryOutput) -> list[tuple[str, str, dict]]:
    entries: list[tuple[str, str, dict]] = []
    if isinstance(payload, list):
        return [("", _entry_name(item), item) for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        out.warnings.append("unrecognized Foundry JSON payload (not an object or array)")
        return entries
    for key in ("tests", "test_results", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [
                (str(item.get("suite", "") or item.get("contract", "") or ""), _entry_name(item), item)
                for item in value if isinstance(item, dict)
            ]
        if isinstance(value, dict) and key in ("test_results", "results"):
            named = [(("", str(name), entry)) for name, entry in value.items() if isinstance(entry, dict)]
            if named:
                return named
    recognized = False
    for suite, suite_value in payload.items():
        if isinstance(suite_value, dict) and isinstance(suite_value.get("test_results"), dict):
            recognized = True
            for name, entry in suite_value["test_results"].items():
                if isinstance(entry, dict):
                    entries.append((str(suite), str(name), entry))
    if not recognized and not entries:
        out.warnings.append("unrecognized Foundry JSON structure; no test entries extracted")
    return entries


def parse_foundry_json_payload(payload: object, *, run_id: str = "", tool: str = "foundry") -> ParsedFoundryOutput:
    out = ParsedFoundryOutput(tool=tool, source_format=FOUNDRY_JSON)
    for suite, test_name, entry in _collect_test_entries(payload, out):
        if not test_name:
            out.warnings.append("skipped a JSON test entry with no recognizable name")
            continue
        out.test_results.append(_build_result(suite, test_name, entry, run_id, tool))
    return out


def parse_foundry_text_output(text: str, *, run_id: str = "", tool: str = "foundry") -> ParsedFoundryOutput:
    out = ParsedFoundryOutput(tool=tool, source_format=FOUNDRY_TEXT)
    current_contract = ""
    for line in (text or "").splitlines():
        suite_match = _SUITE_RE.match(line)
        if suite_match:
            current_contract = split_foundry_test_identifier(suite_match.group(1))[0]
            continue
        line_match = _TEXT_LINE_RE.match(line)
        if line_match:
            marker, signature, gas = line_match.group(1), line_match.group(2).strip(), line_match.group(3)
            out.test_results.append(LocalTestResult(
                run_id=run_id,
                tool=tool,
                test_name=signature,
                contract_name=current_contract,
                function_name=split_foundry_test_identifier(signature)[1],
                status=foundry_status_to_local_status(marker),
                gas_used=extract_gas_used(gas),
                evidence_support=SUPPORT_NONE,
            ))
            continue
        if _UNKNOWN_MARKER_RE.match(line):
            out.warnings.append(f"unrecognized result marker line: {line.strip()}")
    return out


def parse_foundry_output(text: str, *, run_id: str = "", tool: str = "foundry") -> ParsedFoundryOutput:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text is required for parse_foundry_output")
    try:
        payload = json.loads(text)
    except (ValueError, TypeError):
        return parse_foundry_text_output(text, run_id=run_id, tool=tool)
    return parse_foundry_json_payload(payload, run_id=run_id, tool=tool)


def parsed_foundry_output_to_dict(output: ParsedFoundryOutput) -> dict[str, object]:
    return to_dict(output)
