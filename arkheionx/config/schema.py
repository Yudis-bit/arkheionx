"""Stable Arkheionx config normalization and validation helpers."""
from __future__ import annotations

import copy
import datetime as dt
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from arkheionx.rules.registry import RULE_PACKS, is_known_finding_prefix, validate_rule_pack_keys


CONFIG_SCHEMA_VERSION = "1.7.0"

PROTOCOL_TYPES = (
    "auto",
    "generic",
    "vault",
    "oracle",
    "access-control",
    "rewards",
    "staking",
    "amm",
    "lending",
    "hybrid",
)
MIN_CONFIDENCE_LEVELS = ("low", "medium", "high")
OUTPUT_PROFILES = ("concise", "standard", "full", "ci")
TEST_PLAN_OUTPUT_PROFILES = ("concise", "standard", "full")
RULE_PACK_KEYS = tuple(RULE_PACKS.keys())

DANGEROUS_CONFIG_KEYS = {
    "rpc_url",
    "private_key",
    "mnemonic",
    "live_target",
    "exploit",
    "exploit_mode",
    "attack",
    "attack_mode",
    "drain",
    "drain_mode",
    "profit",
    "profit_mode",
    "clone_url",
    "remote_target",
    "bypass_safety",
    "disable_safety",
}

DEFAULT_CONFIG: dict[str, Any] = {
    "schema_version": CONFIG_SCHEMA_VERSION,
    "protocol_type": "auto",
    "rule_packs": [],
    "min_confidence": "low",
    "output_profile": "standard",
    "scan": {
        "ignore_generated_artifacts": True,
        "include_generated_artifacts": False,
        "extra_ignore_paths": [],
        "extra_ignore_globs": [],
        "max_file_size_kb": None,
        "include_tests": True,
        "include_docs": True,
    },
    "reports": {
        "include_related_knowledge": True,
        "include_evidence_snippets": True,
        "include_suggested_tests": True,
        "include_issue_plan": True,
        "include_executive_summary": True,
        "max_top_gaps": 5,
    },
    "test_plan": {
        "include_foundry_skeletons": True,
        "group_by_rule_family": True,
        "include_low_confidence": False,
        "output_profile": "standard",
    },
    "suppressions": [],
    "additional_search_tags": [],
    "analysis": {
        "semantic_lite": True,
        "slither": False,
        "min_confidence_for_issue_plan": "low",
        "downgrade_keyword_only": True,
        "max_evidence_per_finding": 5,
    },
}


@dataclass(frozen=True)
class ConfigValidationResult:
    valid: bool
    errors: list[str]
    warnings: list[str]
    normalized_config: dict[str, Any]
    source: str = ""


def stable_default_config() -> dict[str, Any]:
    return copy.deepcopy(DEFAULT_CONFIG)


def _dangerous_key_name(key: object) -> str:
    return str(key).strip().lower().replace("-", "_")


def find_dangerous_keys(value: Any, path: str = "$") -> list[str]:
    matches: list[str] = []
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = _dangerous_key_name(key)
            child_path = f"{path}.{key}"
            if normalized in DANGEROUS_CONFIG_KEYS:
                matches.append(child_path)
            matches.extend(find_dangerous_keys(item, child_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            matches.extend(find_dangerous_keys(item, f"{path}[{index}]"))
    return matches


def _merge_dict(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge_dict(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item.strip()]


def _normalize_legacy(raw: dict[str, Any], warnings: list[str]) -> dict[str, Any]:
    normalized = copy.deepcopy(raw)
    if "schema_version" not in normalized:
        if "version" in normalized:
            warnings.append("Legacy `version` field detected; normalized to `schema_version` 1.7.0.")
        normalized["schema_version"] = CONFIG_SCHEMA_VERSION

    if "suppressions" not in normalized and isinstance(normalized.get("suppress_findings"), list):
        normalized["suppressions"] = normalized["suppress_findings"]
        warnings.append("Legacy `suppress_findings` field detected; prefer `suppressions`.")

    if "scan" not in normalized or not isinstance(normalized.get("scan"), dict):
        normalized["scan"] = {}
    scan = normalized["scan"]
    if isinstance(normalized.get("ignore_paths"), list):
        existing = _string_list(scan.get("extra_ignore_paths", []))
        scan["extra_ignore_paths"] = existing + _string_list(normalized.get("ignore_paths"))
        warnings.append("Legacy `ignore_paths` field detected; prefer `scan.extra_ignore_paths`.")

    if "reports" not in normalized or not isinstance(normalized.get("reports"), dict):
        normalized["reports"] = {}
    if isinstance(normalized.get("report"), dict):
        report = normalized["report"]
        if "max_top_gaps" in report and "max_top_gaps" not in normalized["reports"]:
            normalized["reports"]["max_top_gaps"] = report["max_top_gaps"]
            warnings.append("Legacy `report.max_top_gaps` field detected; prefer `reports.max_top_gaps`.")

    if "min_confidence" not in normalized and isinstance(normalized.get("analysis"), dict):
        legacy_min = normalized["analysis"].get("min_confidence_for_issue_plan")
        if isinstance(legacy_min, str):
            normalized["min_confidence"] = legacy_min

    return normalized


def normalize_config(raw: dict[str, Any] | None, source: str = "") -> ConfigValidationResult:
    errors: list[str] = []
    warnings: list[str] = []
    if raw is None:
        raw = {}
    if not isinstance(raw, dict):
        return ConfigValidationResult(False, ["Config must be a JSON object."], warnings, stable_default_config(), source)

    dangerous = find_dangerous_keys(raw)
    if dangerous:
        errors.extend(
            f"Dangerous config key `{item}` is not supported. Arkheionx config is local/static and cannot enable live targets, secrets, or attack modes."
            for item in dangerous
        )

    legacy = _normalize_legacy(raw, warnings)
    config = _merge_dict(stable_default_config(), legacy)
    _validate_shape(config, errors, warnings)
    valid = not errors
    return ConfigValidationResult(valid, errors, warnings, config, source)


def _validate_enum(config: dict[str, Any], key: str, allowed: tuple[str, ...], errors: list[str]) -> None:
    value = config.get(key)
    if value not in allowed:
        errors.append(f"`{key}` must be one of {', '.join(allowed)}.")


def _validate_bool(parent: dict[str, Any], key: str, path: str, errors: list[str]) -> None:
    if key in parent and not isinstance(parent[key], bool):
        errors.append(f"`{path}.{key}` must be a boolean.")


def _validate_shape(config: dict[str, Any], errors: list[str], warnings: list[str]) -> None:
    if config.get("schema_version") != CONFIG_SCHEMA_VERSION:
        warnings.append(f"Config schema_version `{config.get('schema_version')}` will be normalized as {CONFIG_SCHEMA_VERSION}.")
        config["schema_version"] = CONFIG_SCHEMA_VERSION

    _validate_enum(config, "protocol_type", PROTOCOL_TYPES, errors)
    _validate_enum(config, "min_confidence", MIN_CONFIDENCE_LEVELS, errors)
    _validate_enum(config, "output_profile", OUTPUT_PROFILES, errors)

    rule_packs = config.get("rule_packs", [])
    if not isinstance(rule_packs, list) or not all(isinstance(item, str) for item in rule_packs):
        errors.append("`rule_packs` must be a list of rule-pack keys.")
    else:
        unknown = validate_rule_pack_keys(rule_packs)
        if unknown:
            errors.append(f"Unknown rule pack(s): {', '.join(sorted(unknown))}.")

    scan = config.get("scan")
    if not isinstance(scan, dict):
        errors.append("`scan` must be an object.")
    else:
        for key in ["ignore_generated_artifacts", "include_generated_artifacts", "include_tests", "include_docs"]:
            _validate_bool(scan, key, "scan", errors)
        for key in ["extra_ignore_paths", "extra_ignore_globs"]:
            if key in scan and not isinstance(scan[key], list):
                errors.append(f"`scan.{key}` must be a list of strings.")
            elif key in scan and not all(isinstance(item, str) for item in scan[key]):
                errors.append(f"`scan.{key}` must contain only strings.")
        max_file_size = scan.get("max_file_size_kb")
        if max_file_size is not None and (not isinstance(max_file_size, int) or max_file_size <= 0):
            errors.append("`scan.max_file_size_kb` must be a positive integer when set.")
        if scan.get("include_generated_artifacts"):
            warnings.append("`scan.include_generated_artifacts` is advanced/debug behavior and may cause generated reports to influence scans.")

    reports = config.get("reports")
    if not isinstance(reports, dict):
        errors.append("`reports` must be an object.")
    else:
        for key in [
            "include_related_knowledge",
            "include_evidence_snippets",
            "include_suggested_tests",
            "include_issue_plan",
            "include_executive_summary",
        ]:
            _validate_bool(reports, key, "reports", errors)
        max_top = reports.get("max_top_gaps")
        if max_top is not None and (not isinstance(max_top, int) or not 1 <= max_top <= 20):
            errors.append("`reports.max_top_gaps` must be an integer from 1 to 20.")

    test_plan = config.get("test_plan")
    if not isinstance(test_plan, dict):
        errors.append("`test_plan` must be an object.")
    else:
        for key in ["include_foundry_skeletons", "group_by_rule_family", "include_low_confidence"]:
            _validate_bool(test_plan, key, "test_plan", errors)
        if test_plan.get("output_profile") not in TEST_PLAN_OUTPUT_PROFILES:
            errors.append(f"`test_plan.output_profile` must be one of {', '.join(TEST_PLAN_OUTPUT_PROFILES)}.")

    additional_tags = config.get("additional_search_tags", [])
    if not isinstance(additional_tags, list) or not all(isinstance(item, str) for item in additional_tags):
        errors.append("`additional_search_tags` must be a list of strings.")

    suppressions = config.get("suppressions", [])
    if not isinstance(suppressions, list):
        errors.append("`suppressions` must be a list.")
        return
    for index, item in enumerate(suppressions):
        if not isinstance(item, dict):
            errors.append(f"`suppressions[{index}]` must be an object.")
            continue
        _validate_suppression(item, index, errors, warnings)


def _validate_suppression(item: dict[str, Any], index: int, errors: list[str], warnings: list[str]) -> None:
    prefix = f"suppressions[{index}]"
    finding_id = str(item.get("id", "")).strip()
    if not finding_id:
        errors.append(f"`{prefix}.id` is required.")
    elif not is_known_finding_prefix(finding_id):
        errors.append(f"`{prefix}.id` must use a known Arkheionx finding prefix.")

    reason = str(item.get("reason", "")).strip()
    if not reason:
        errors.append(f"`{prefix}.reason` is required.")

    for key in ["path", "owner"]:
        if key in item and not isinstance(item[key], str):
            errors.append(f"`{prefix}.{key}` must be a string.")

    for key in ["expires", "review_after"]:
        if key in item and item[key]:
            try:
                dt.date.fromisoformat(str(item[key]))
            except ValueError:
                errors.append(f"`{prefix}.{key}` must be an ISO date like YYYY-MM-DD.")

    unknown = set(item) - {"id", "path", "reason", "expires", "owner", "review_after"}
    if unknown:
        warnings.append(f"`{prefix}` contains non-standard field(s): {', '.join(sorted(unknown))}.")


def load_config_file(path: Path) -> tuple[dict[str, Any], str | None]:
    try:
        import json

        payload = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        return {}, f"Could not read config `{path}`: {exc}"
    except ValueError as exc:
        return {}, f"Could not parse config `{path}`: {exc}"
    if not isinstance(payload, dict):
        return {}, f"Config `{path}` must be a JSON object."
    return payload, None
