"""Strict, in-memory review package validation (v3.6, additive, internal-only).

Validates a ``ReviewPackageManifest`` and produces a populated
``ReviewPackageValidationResult``. All checks are local/static and read-only:
they never mutate the manifest, never write files, and never echo secret values
(the secret scan reports a pattern class and a relative path only). The result
keeps ``manual_review_required`` true and ``ready_for_submission`` false, and it
never emits HUMAN_REVIEWED or any audit/severity/bounty claim.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

from .checksums import is_probable_checksum, sha256_file
from .ids import package_validation_id
from .model import (
    PACKAGE_DRAFT,
    PACKAGE_INVALID,
    PACKAGE_PARTIAL,
    PACKAGE_READY_FOR_HUMAN_REVIEW,
    ReviewPackageManifest,
    ReviewPackageValidationResult,
    to_dict,
)

PASS, WARN, FAIL, SKIP = "PASS", "WARN", "FAIL", "SKIP"
INFO, WARNING, ERROR = "info", "warning", "error"

_SAFETY_TRUE_FLAGS = (
    "local_static_only", "no_rpc", "no_private_keys", "no_seed_phrases",
    "no_live_chain_calls", "no_transaction_broadcasting", "no_exploit_automation",
    "no_auto_submit", "no_automatic_human_reviewed", "no_confirmed_vulnerabilities",
    "no_final_severity", "no_audit_passed_claim", "no_bounty_eligibility",
)

_MAX_SCAN_BYTES = 1024 * 1024
# Conservative secret pattern classes. Names only are ever reported, never values.
_SECRET_PATTERNS = {
    "private_key_like": re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----|\b0x[0-9a-fA-F]{64}\b"),
    "seed_phrase_like": re.compile(r"\b(?:[a-z]{3,8} ){11,}[a-z]{3,8}\b"),
    "rpc_url_like": re.compile(r"\b[a-z][a-z0-9+.\-]*://[^\s/@]+:[^\s/@]+@"),
    "api_key_like": re.compile(r"(?i)\b(?:api[_-]?key|secret)\b['\"=:\s]+[A-Za-z0-9_\-]{16,}"),
    "bearer_token_like": re.compile(r"\bBearer\s+[A-Za-z0-9._\-]{8,}\b|\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
}


def _check(name, status, severity, message, artifact_id="", path="", kind=""):
    return {"name": name, "status": status, "severity": severity, "message": message,
            "artifact_id": artifact_id, "path": path, "kind": kind}


def validate_manifest_shape(manifest: ReviewPackageManifest) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    checks.append(_check("shape_manifest_version", PASS if manifest.manifest_version else FAIL,
                         INFO if manifest.manifest_version else ERROR, "manifest_version present"))
    has_id = bool(manifest.package_id)
    checks.append(_check("shape_package_id", PASS if has_id else FAIL,
                         INFO if has_id else ERROR, "package_id present"))
    if has_id:
        ok = manifest.package_id.startswith("review-package:")
        checks.append(_check("shape_package_id_format", PASS if ok else FAIL,
                             INFO if ok else ERROR, "package_id uses review-package: prefix"))
    for field_name in ("included_artifacts", "required_artifacts", "optional_artifacts"):
        ok = isinstance(getattr(manifest, field_name), list)
        checks.append(_check(f"shape_{field_name}_list", PASS if ok else FAIL,
                             INFO if ok else ERROR, f"{field_name} is a list"))
    ok_sb = isinstance(manifest.safety_boundary, dict)
    checks.append(_check("shape_safety_boundary", PASS if ok_sb else FAIL,
                         INFO if ok_sb else ERROR, "safety_boundary present"))
    for art in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        missing = [f for f in ("artifact_id", "kind", "path", "relative_path") if not getattr(art, f, "")]
        if not isinstance(getattr(art, "exists", None), bool):
            missing.append("exists")
        if not isinstance(getattr(art, "required", None), bool):
            missing.append("required")
        status = PASS if not missing else FAIL
        checks.append(_check("shape_artifact_fields", status, INFO if not missing else ERROR,
                             "artifact fields present" if not missing else f"artifact missing fields: {','.join(missing)}",
                             artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
    return checks


def validate_required_artifacts(manifest: ReviewPackageManifest) -> list[dict[str, object]]:
    present = {a.kind for a in manifest.included_artifacts if a.exists}
    checks: list[dict[str, object]] = []
    for kind in sorted(manifest.required_artifacts):
        ok = kind in present
        checks.append(_check("required_artifact_present", PASS if ok else FAIL,
                             INFO if ok else WARNING,
                             f"required artifact present: {kind}" if ok else f"required artifact missing: {kind}",
                             kind=kind))
    return checks


def _path_problem(value: str) -> str:
    if not value:
        return ""
    if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
        return "absolute path"
    if "\\" in value:
        return "backslash separators"
    if ".." in value.split("/"):
        return "path traversal"
    if "/home/" in value or "/Users/" in value:
        return "home directory leak"
    return ""


def validate_artifact_paths(manifest: ReviewPackageManifest) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for art in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        for label, value, expect_prefix in (("path", art.path, True), ("relative_path", art.relative_path, False)):
            problem = _path_problem(value)
            if problem:
                checks.append(_check("path_safety", FAIL, ERROR, f"{label} has {problem}",
                                     artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
                continue
            if expect_prefix and value and not value.startswith(".arkheionx/out/"):
                checks.append(_check("path_prefix", WARN, WARNING, "path is not under .arkheionx/out/",
                                     artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
            elif not expect_prefix and value.startswith(".arkheionx/out/"):
                checks.append(_check("path_prefix", WARN, WARNING, "relative_path should not include .arkheionx/out/",
                                     artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
            else:
                checks.append(_check("path_safety", PASS, INFO, f"{label} is safe relative POSIX",
                                     artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
    return checks


def _resolve(art, repo_path, artifacts_root):
    if art.path:
        return Path(str(repo_path)) / art.path
    if artifacts_root is not None and art.relative_path:
        return Path(str(artifacts_root)) / art.relative_path
    return None


def validate_artifact_entries(manifest, repo_path, artifacts_root=None) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for art in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        target = _resolve(art, repo_path, artifacts_root)
        actual = bool(target and target.is_file())
        if art.exists and not actual:
            checks.append(_check("entry_state", FAIL, ERROR, "artifact marked exists but file is missing",
                                 artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
        elif not art.exists and actual:
            checks.append(_check("entry_state", WARN, WARNING, "file present but artifact marked missing",
                                 artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
        elif art.exists and actual and art.size_bytes and target.stat().st_size != art.size_bytes:
            checks.append(_check("entry_state", WARN, WARNING, "recorded size does not match file size",
                                 artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
        else:
            checks.append(_check("entry_state", PASS, INFO, "artifact state is consistent",
                                 artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
    return checks


def validate_checksums(manifest, repo_path, *, strict: bool = False) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for art in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        target = Path(str(repo_path)) / art.path if art.path else None
        if not (target and target.is_file()):
            continue
        declared = art.checksum_sha256 or manifest.checksums.get(art.relative_path, "")
        if not declared:
            checks.append(_check("checksum_present", FAIL if strict else WARN, ERROR if strict else WARNING,
                                 "no checksum recorded for artifact",
                                 artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
            continue
        if not is_probable_checksum(declared):
            checks.append(_check("checksum_malformed", FAIL, ERROR, "recorded checksum is malformed",
                                 artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
            continue
        ok = declared == sha256_file(target)
        checks.append(_check("checksum_match", PASS if ok else FAIL, INFO if ok else ERROR,
                             "checksum matches file" if ok else "checksum does not match file",
                             artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
    return checks


def validate_safety_boundary(manifest: ReviewPackageManifest) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    checks.append(_check("safety_manual_review_required", PASS if manifest.manual_review_required is True else FAIL,
                         INFO if manifest.manual_review_required is True else ERROR, "manual_review_required is true"))
    checks.append(_check("safety_ready_for_submission", PASS if manifest.ready_for_submission is False else FAIL,
                         INFO if manifest.ready_for_submission is False else ERROR, "ready_for_submission is false"))
    boundary = manifest.safety_boundary if isinstance(manifest.safety_boundary, dict) else {}
    for flag in _SAFETY_TRUE_FLAGS:
        if flag not in boundary:
            checks.append(_check("safety_flag", WARN, WARNING, f"safety flag not declared: {flag}"))
        elif boundary[flag] is not True:
            checks.append(_check("safety_flag", FAIL, ERROR, f"safety flag is not true: {flag}"))
        else:
            checks.append(_check("safety_flag", PASS, INFO, f"safety flag is true: {flag}"))
    blob = json.dumps(to_dict(manifest))
    emits = "HUMAN_REVIEWED" in blob
    checks.append(_check("safety_no_human_reviewed", FAIL if emits else PASS,
                         ERROR if emits else INFO,
                         "manifest emits a human-reviewed status (forbidden)" if emits
                         else "manifest does not emit a human-reviewed status"))
    return checks


def _readable_text(path: Path) -> str | None:
    try:
        with path.open("rb") as handle:
            data = handle.read(_MAX_SCAN_BYTES)
    except OSError:
        return None
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def scan_artifact_for_secret_patterns(path: str | Path) -> list[str]:
    text = _readable_text(Path(str(path)))
    if text is None:
        return []
    return sorted(name for name, pattern in _SECRET_PATTERNS.items() if pattern.search(text))


def validate_secret_patterns(manifest, repo_path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    for art in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        target = Path(str(repo_path)) / art.path if art.path else None
        if not (target and target.is_file()):
            continue
        if _readable_text(target) is None and target.stat().st_size > 0:
            checks.append(_check("secret_scan", WARN, WARNING, "artifact not scanned (binary or unreadable)",
                                 artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
            continue
        for klass in scan_artifact_for_secret_patterns(target):
            checks.append(_check("safety_secret_pattern", FAIL, ERROR, f"{klass} pattern detected",
                                 artifact_id=art.artifact_id, path=art.relative_path, kind=art.kind))
    return checks


def derive_validation_status(errors, warnings, missing_required, included_artifact_count) -> str:
    if errors:
        return PACKAGE_INVALID
    if included_artifact_count == 0:
        return PACKAGE_DRAFT
    if missing_required:
        return PACKAGE_PARTIAL
    return PACKAGE_READY_FOR_HUMAN_REVIEW


def build_validation_result(package_id, checks, *, checked_at: str = "") -> ReviewPackageValidationResult:
    checks = sorted(checks, key=lambda c: (c["name"], c.get("kind", ""), c.get("path", ""), c["message"]))
    errors = [c["message"] for c in checks if c["severity"] == ERROR]
    warnings = [c["message"] for c in checks if c["severity"] == WARNING]
    missing_required = [c["kind"] for c in checks if c["name"] == "required_artifact_present" and c["status"] == FAIL]
    checksum_mismatches = [c["path"] or c["message"] for c in checks if c["name"].startswith("checksum") and c["status"] == FAIL]
    schema_failures = [c["message"] for c in checks if c["name"].startswith("shape") and c["status"] == FAIL]
    safety_failures = [c["message"] for c in checks if c["name"].startswith("safety") and c["status"] == FAIL]
    stale = [c["path"] for c in checks if c["name"] == "entry_state" and c["status"] in (FAIL, WARN) and c["path"]]
    count = sum(1 for c in checks if c["name"] == "entry_state")
    status = derive_validation_status(errors, warnings, missing_required, count)
    return ReviewPackageValidationResult(
        validation_id=package_validation_id(package_id or "review-package:unknown"),
        package_id=package_id,
        status=status,
        checked_at=checked_at,
        checks=checks,
        errors=errors,
        warnings=warnings,
        missing_required_artifacts=missing_required,
        stale_artifacts=stale,
        checksum_mismatches=checksum_mismatches,
        schema_failures=schema_failures,
        safety_failures=safety_failures,
        manual_review_required=True,
        ready_for_human_review=status == PACKAGE_READY_FOR_HUMAN_REVIEW,
        ready_for_submission=False,
    )


_LV_JSON_KINDS = (
    "local_validation_summary", "local_validation_run", "local_test_result",
    "local_trace_receipt", "local_validation_artifacts_index",
)
_LV_KINDS = set(_LV_JSON_KINDS) | {"local_validation_checksums"}
_LV_BOUNDARY_KINDS = ("local_validation_summary", "local_validation_artifacts_index")
_LV_READY_TRUE_RE = re.compile(r'"ready_for_submission"\s*:\s*true')


def _lv_overclaim(text: str) -> list[str]:
    """Return forbidden positive-claim markers found in generated content.

    Negative disclaimers ("No final severity and no bounty eligibility", "not an
    audit") are intentionally not flagged; only positive overclaim forms are.
    """

    found: list[str] = []
    if "HUMAN_REVIEWED" in text:
        found.append("HUMAN_REVIEWED")
    if _LV_READY_TRUE_RE.search(text):
        found.append("ready_for_submission true")
    lowered = text.lower()
    for marker in ("audit passed", "confirmed vulnerability", "final severity:",
                   "guaranteed bounty", "bounty guaranteed"):
        if marker in lowered:
            found.append(marker)
    return found


def _validate_lv_checksums(path: Path, art, repo_path) -> list[dict[str, object]]:
    checks: list[dict[str, object]] = []
    lv_root = path.parent.parent  # .../local-validation
    try:
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        return [_check("local_validation.checksums.readable", FAIL, ERROR, "could not read checksum file",
                       art.artifact_id, art.relative_path, art.kind)]
    ok = True
    for line in lines:
        if "  " not in line:
            ok = False
            checks.append(_check("local_validation.checksums.format", FAIL, ERROR, "malformed checksum line",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        digest, rel = line.split("  ", 1)
        if not is_probable_checksum(digest):
            ok = False
            checks.append(_check("local_validation.checksums.format", FAIL, ERROR, "malformed checksum digest",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        referenced = lv_root / rel
        if not referenced.is_file():
            ok = False
            checks.append(_check("local_validation.checksums.referenced_exists", FAIL, ERROR,
                                 f"checksum references missing file: {rel}", art.artifact_id, art.relative_path, art.kind))
        elif sha256_file(referenced) != digest:
            ok = False
            checks.append(_check("local_validation.checksums.match", FAIL, ERROR,
                                 f"checksum does not match file: {rel}", art.artifact_id, art.relative_path, art.kind))
    if ok and lines:
        checks.append(_check("local_validation.checksums.match", PASS, INFO, "local validation checksums match",
                             art.artifact_id, art.relative_path, art.kind))
    return checks


def validate_local_validation_artifacts(manifest, repo_path, artifacts_root=None) -> list[dict[str, object]]:
    """Additive checks for optional local-validation artifacts (v3.7).

    Local-validation artifacts are optional: a missing one is a warning, never a
    failure. JSON must parse; the summary/index must keep ``manual_review_required``
    true and ``ready_for_submission`` false; no positive overclaim or human-reviewed
    marker may appear; and the SHA256SUMS file must be well-formed and match.
    """

    checks: list[dict[str, object]] = []
    for art in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        if art.kind not in _LV_KINDS:
            continue
        target = _resolve(art, repo_path, artifacts_root)
        if not (target and target.is_file()):
            checks.append(_check("local_validation.present", WARN, WARNING, "local validation artifact missing",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except OSError:
            checks.append(_check("local_validation.readable", FAIL, ERROR, "could not read artifact",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        for marker in _lv_overclaim(text):
            checks.append(_check("safety.local_validation.no_overclaim", FAIL, ERROR,
                                 f"local validation artifact contains forbidden marker: {marker}",
                                 art.artifact_id, art.relative_path, art.kind))
        if art.kind == "local_validation_checksums":
            checks += _validate_lv_checksums(target, art, repo_path)
            continue
        try:
            data = json.loads(text)
        except ValueError:
            checks.append(_check("local_validation.parseable", FAIL, ERROR, "local validation JSON is malformed",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        checks.append(_check("local_validation.parseable", PASS, INFO, "local validation JSON parses",
                             art.artifact_id, art.relative_path, art.kind))
        if art.kind in _LV_BOUNDARY_KINDS and isinstance(data, dict):
            if data.get("manual_review_required") is not True:
                checks.append(_check("safety.local_validation.manual_review_required", FAIL, ERROR,
                                     "local validation manual_review_required must be true",
                                     art.artifact_id, art.relative_path, art.kind))
            if data.get("ready_for_submission") is not False:
                checks.append(_check("safety.local_validation.not_ready_for_submission", FAIL, ERROR,
                                     "local validation ready_for_submission must be false",
                                     art.artifact_id, art.relative_path, art.kind))
    return checks


# Optional protocol intelligence graph artifacts (Agent 9, v3.8). They are never
# required for package readiness and are review context only: they never finalize
# a security conclusion. Graph consistency never proves protocol safety and a
# graph warning never proves a vulnerability.
_GRAPH_JSON_KINDS = (
    "protocol_graph", "protocol_graph_node", "protocol_graph_edge",
    "protocol_graph_check", "protocol_graph_coverage_summary",
    "protocol_graph_artifacts_index",
)
_GRAPH_KINDS = set(_GRAPH_JSON_KINDS) | {"protocol_graph_checksums"}
# Known graph artifacts whose top-level value is expected to be a JSON object.
_GRAPH_OBJECT_KINDS = (
    "protocol_graph", "protocol_graph_node", "protocol_graph_edge",
    "protocol_graph_check", "protocol_graph_coverage_summary",
)

# Positive overclaim wording that must never appear in a graph artifact. These
# are forbidden claims, not allowed output: no bounty-eligibility claim, and never
# a claim that the graph proves protocol safety or that a graph warning proves a
# vulnerability. Negative disclaimers are intentionally not flagged.
_GRAPH_FORBIDDEN_WORDING = (
    "bounty eligible",
    "graph proves safety",
    "graph consistency proves safety",
    "proves protocol safety",
    "warning proves vulnerability",
    "graph warning proves vulnerability",
)


def _graph_overclaim(text: str) -> list[str]:
    """Forbidden positive-claim markers in a protocol-graph artifact.

    Reuses the local-validation overclaim scan (HUMAN_REVIEWED, ready_for_submission
    true, audit passed, confirmed vulnerability, final severity, guaranteed bounty)
    and adds graph-specific forbidden wording.
    """

    found = _lv_overclaim(text)
    lowered = text.lower()
    for marker in _GRAPH_FORBIDDEN_WORDING:
        if marker in lowered:
            found.append(marker)
    return found


def _graph_path_problem(value: object) -> str:
    """Path-safety problem for a string value embedded in a graph artifact."""

    if not isinstance(value, str) or not value:
        return ""
    if value.startswith("/") or re.match(r"^[A-Za-z]:[\\/]", value):
        return "absolute path"
    if "\\" in value:
        return "backslash separators"
    if ".." in value.split("/"):
        return "path traversal"
    return ""


def _walk_strings(value: object):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _walk_strings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from _walk_strings(item)


def _validate_graph_checksums(path: Path, art, repo_path) -> list[dict[str, object]]:
    """Validate a protocol-graph SHA256SUMS file.

    Lines are ``<sha256>  <relative-path>`` with relative paths under
    ``protocol-graph/``; referenced files must exist and match. The checksum file
    is not expected to list itself; a self-reference line is ignored (consistently)
    rather than treated as an error.
    """

    checks: list[dict[str, object]] = []
    graph_root = path.parent.parent  # .../protocol-graph
    try:
        lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    except OSError:
        return [_check("protocol_graph.checksums.readable", FAIL, ERROR, "could not read checksum file",
                       art.artifact_id, art.relative_path, art.kind)]
    ok = True
    for line in lines:
        if "  " not in line:
            ok = False
            checks.append(_check("protocol_graph.checksums.format", FAIL, ERROR, "malformed checksum line",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        digest, rel = line.split("  ", 1)
        if not is_probable_checksum(digest):
            ok = False
            checks.append(_check("protocol_graph.checksums.format", FAIL, ERROR, "malformed checksum digest",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        problem = _graph_path_problem(rel)
        if problem:
            ok = False
            checks.append(_check("safety.protocol_graph.checksums.path_safety", FAIL, ERROR,
                                 f"checksum path has {problem}", art.artifact_id, art.relative_path, art.kind))
            continue
        if rel == "checksums/SHA256SUMS":  # the file is not required to list itself
            continue
        referenced = graph_root / rel
        if not referenced.is_file():
            ok = False
            checks.append(_check("protocol_graph.checksums.referenced_exists", FAIL, ERROR,
                                 f"checksum references missing file: {rel}", art.artifact_id, art.relative_path, art.kind))
        elif sha256_file(referenced) != digest:
            ok = False
            checks.append(_check("protocol_graph.checksums.match", FAIL, ERROR,
                                 f"checksum does not match file: {rel}", art.artifact_id, art.relative_path, art.kind))
    if ok and lines:
        checks.append(_check("protocol_graph.checksums.match", PASS, INFO, "protocol graph checksums match",
                             art.artifact_id, art.relative_path, art.kind))
    return checks


def validate_protocol_graph_artifacts(manifest, repo_path, artifacts_root=None) -> list[dict[str, object]]:
    """Additive checks for optional protocol-graph artifacts (Agent 9, v3.8).

    Protocol-graph artifacts are optional and never required: a missing one is a
    warning, never a failure. Known JSON artifacts must parse; no embedded string
    value may carry an absolute path, backslash separators, or a traversal segment;
    a present ``manual_review_required`` must be true and a present
    ``ready_for_submission`` must be false; and no positive overclaim or
    human-reviewed marker may appear. The SHA256SUMS file must be well-formed and
    match. Nothing here proves protocol safety, and a graph warning never proves a
    vulnerability.
    """

    checks: list[dict[str, object]] = []
    for art in sorted(manifest.included_artifacts, key=lambda a: a.relative_path):
        if art.kind not in _GRAPH_KINDS:
            continue
        target = _resolve(art, repo_path, artifacts_root)
        if not (target and target.is_file()):
            checks.append(_check("protocol_graph.present", WARN, WARNING, "protocol graph artifact missing",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        try:
            text = target.read_text(encoding="utf-8")
        except OSError:
            checks.append(_check("protocol_graph.readable", FAIL, ERROR, "could not read artifact",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        for marker in _graph_overclaim(text):
            checks.append(_check("safety.protocol_graph.no_overclaim", FAIL, ERROR,
                                 f"protocol graph artifact contains forbidden marker: {marker}",
                                 art.artifact_id, art.relative_path, art.kind))
        if art.kind == "protocol_graph_checksums":
            checks += _validate_graph_checksums(target, art, repo_path)
            continue
        try:
            data = json.loads(text)
        except ValueError:
            checks.append(_check("protocol_graph.parseable", FAIL, ERROR, "protocol graph JSON is malformed",
                                 art.artifact_id, art.relative_path, art.kind))
            continue
        checks.append(_check("protocol_graph.parseable", PASS, INFO, "protocol graph JSON parses",
                             art.artifact_id, art.relative_path, art.kind))
        if art.kind in _GRAPH_OBJECT_KINDS and not isinstance(data, dict):
            checks.append(_check("protocol_graph.shape", WARN, WARNING,
                                 "protocol graph artifact is not a JSON object",
                                 art.artifact_id, art.relative_path, art.kind))
        for value in _walk_strings(data):
            problem = _graph_path_problem(value)
            if problem:
                checks.append(_check("safety.protocol_graph.path_safety", FAIL, ERROR,
                                     f"protocol graph artifact value has {problem}",
                                     art.artifact_id, art.relative_path, art.kind))
                break  # one path-safety failure per artifact is enough
        if isinstance(data, dict):
            if "manual_review_required" in data and data.get("manual_review_required") is not True:
                checks.append(_check("safety.protocol_graph.manual_review_required", FAIL, ERROR,
                                     "protocol graph manual_review_required must be true",
                                     art.artifact_id, art.relative_path, art.kind))
            if "ready_for_submission" in data and data.get("ready_for_submission") is not False:
                checks.append(_check("safety.protocol_graph.not_ready_for_submission", FAIL, ERROR,
                                     "protocol graph ready_for_submission must be false",
                                     art.artifact_id, art.relative_path, art.kind))
    return checks


def validate_review_package_manifest(
    manifest: ReviewPackageManifest,
    repo_path: str | Path,
    artifacts_root: str | Path | None = None,
    *,
    strict: bool = True,
    protocol_model: dict | None = None,
) -> ReviewPackageValidationResult:
    checks: list[dict[str, object]] = []
    checks += validate_manifest_shape(manifest)
    checks += validate_required_artifacts(manifest)
    checks += validate_artifact_paths(manifest)
    checks += validate_artifact_entries(manifest, repo_path, artifacts_root)
    checks += validate_checksums(manifest, repo_path, strict=strict)
    checks += validate_safety_boundary(manifest)
    checks += validate_secret_patterns(manifest, repo_path)
    checks += validate_local_validation_artifacts(manifest, repo_path, artifacts_root)
    checks += validate_protocol_graph_artifacts(manifest, repo_path, artifacts_root)
    if protocol_model is not None:
        from .crossref import validate_package_cross_references

        checks += validate_package_cross_references(manifest, repo_path, None, protocol_model)
    # Protocol-graph cross-references resolve internally / against local-validation
    # artifacts even without a protocol model, so they run unconditionally. The call
    # is a no-op (returns no checks) when no protocol-graph artifacts are present.
    from .crossref import validate_protocol_graph_cross_references

    checks += validate_protocol_graph_cross_references(manifest, repo_path, None, protocol_model)
    return build_validation_result(manifest.package_id, checks)
