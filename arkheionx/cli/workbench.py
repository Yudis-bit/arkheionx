"""CLI handlers for the Foundry-style Arkheionx workbench.

Commands: doctor, open, map, flow, hunt, prove. Output is compact by default;
`--full`/`--show-all`/`--json`/`--mermaid` expand it. Exit codes:
0 = ok (compiler/execution confirmed), 1 = heuristic-only warning, 2 = failure.
"""
from __future__ import annotations

import json
import platform
import shlex
import shutil
import subprocess
import sys
import time
from argparse import Namespace
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.cli import colors, exit_codes, screen
from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.flow.mermaid import render_mermaid
from arkheionx.flow.render import render_flow
from arkheionx.hunt.render import render_hunt
from arkheionx.hunt.test_suggestions import suggest_tests
from arkheionx.evidence.builder import build_evidence
from arkheionx.evidence import index as _evindex
from arkheionx.evidence.status import build_status
from arkheionx.evidence.validate import validate_artifacts
from arkheionx.evidence.render import render_evidence, render_status, render_validate
from arkheionx.proof.generator import generate_scaffold, harness_name
from arkheionx.proof.payloads import build_proof_payload, build_trace_payload, target_slug
from arkheionx.proof.render import render_trace
from arkheionx.proof.runner import ExecResult, execute_target
from arkheionx.reporting.builder import build_report
from arkheionx.reporting.render import render_report
from arkheionx.protocol import foundry as foundry_mod
from arkheionx.protocol.detector import analyze
from arkheionx.protocol.model import COMPILER_CONFIRMED, EXECUTION_CONFIRMED, HEURISTIC, to_dict
from arkheionx.protocol.render import build_json, foundry_header, hidden_block, mode_header, render_map, self_disp
from arkheionx.protocol.semantic_adapter import find_solidity_files
from arkheionx.review_map import (
    build_assumptions_payload,
    build_evidence_links_payload,
    build_proof_plan_payload,
    build_review_map,
    build_test_gap_map,
    build_value_paths_payload,
    default_out_dir,
    render_assumptions_cli,
    render_evidence_links_cli,
    render_proof_plan_cli,
    render_test_gap_map_cli,
    render_value_paths_cli,
    status_of,
    write_artifacts,
)
from arkheionx.review_map.model import HIGH as RM_HIGH
from arkheionx.research import (
    build_agent_brief_from_review_map,
    build_case_study_from_review_map,
    build_hypothesis_log_from_review_map,
    default_research_dir,
    render_agent_brief_cli,
    render_case_study_cli,
    render_hypothesis_log_cli,
    write_agent_brief,
    write_case_study,
    write_hypothesis_log,
)
from arkheionx.cli_ui import TerminalUI
from arkheionx.rules.registry import list_rule_packs

SUCCESS = exit_codes.SUCCESS          # 0
WARNING = exit_codes.RUNTIME_ERROR    # 1 (heuristic-only / usable warning)
FAILED = exit_codes.INVALID_ARGUMENTS # 2 (cannot complete)


def _print_report(text: str) -> None:
    """Print a human report with restrained color (no-op when color disabled)."""
    print(colors.colorize_report(text))


def _resolve_root(repo: str) -> Path | None:
    root = Path(repo).expanduser().resolve()
    return root if root.is_dir() else None


def _from_report(args: Namespace) -> Path | None:
    value = getattr(args, "from_report", "")
    return Path(value).expanduser() if value else None


def _writer(args: Namespace) -> ArtifactWriter:
    base = getattr(args, "artifacts_dir", "") or ""
    return ArtifactWriter(Path(base).expanduser() if base else None)


def _run_analysis(args: Namespace, root: Path):
    return analyze(
        root,
        from_report=_from_report(args),
        use_foundry=bool(getattr(args, "foundry", False) or getattr(args, "build", False)),
        run_build=bool(getattr(args, "build", False)),
        show_all=bool(getattr(args, "show_all", False)),
        top=int(getattr(args, "top", 10) or 10),
    )


def _exit_for(analysis) -> int:
    return SUCCESS if analysis.snapshot.evidence_level != HEURISTIC else WARNING


def _emit(args: Namespace, payload: dict, writer: ArtifactWriter, json_name: str, extra: dict | None = None) -> dict[str, str]:
    artifacts: dict[str, str] = {}
    if getattr(args, "no_artifacts", False):
        return artifacts
    path = writer.write_text(json_name, json.dumps(payload, indent=2))
    artifacts["JSON"] = str(path)
    for label, (name, content) in (extra or {}).items():
        artifacts[label] = str(writer.write_text(name, content))
    return artifacts


# --------------------------------------------------------------------------
# open / map / flow / hunt
# --------------------------------------------------------------------------
def open_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    start = time.monotonic()
    analysis = _run_analysis(args, root)
    elapsed = time.monotonic() - start
    if getattr(args, "json", False):
        print(json.dumps(build_json(analysis, {}, [f"arkheionx map {args.repo}"]), indent=2))
        return _exit_for(analysis)
    return _open_human(args, analysis, elapsed)


def _open_human(args: Namespace, analysis, elapsed: float) -> int:
    """Render `open` through the TerminalUI DX layer (presentation only)."""
    ui = TerminalUI()
    snap = analysis.snapshot
    flow = analysis.money_flow
    ui.banner("ARKHEIONX OPEN", "One-command project orientation - local/static, no RPC, no keys.")
    ui.info(f"Target: {args.repo}")
    ui.info(f"Mode:   local/static ({mode_header(snap.evidence_level)})")
    ui.info("")
    ui.step_done(
        "Analyzing project",
        f"{snap.contracts_analyzed} contracts, {len(analysis.functions)} functions",
        elapsed=elapsed, index=1, total=1,
    )
    ui.summary("Summary", [
        ("Protocol", " + ".join(snap.protocol_types) or "generic"),
        ("Active contracts", snap.contracts_analyzed),
        ("Functions", len(analysis.functions)),
        ("Hidden support", sum(analysis.hidden_counts.values())),
        ("Review surfaces", len(analysis.hunter_targets)),
        ("Evidence", snap.evidence_level),
    ])
    ui.section("Top Surfaces")
    if analysis.hunter_targets:
        for i, t in enumerate(analysis.hunter_targets[:3], 1):
            reason = t.why_it_matters[0] if t.why_it_matters else ""
            ui.info(f"  {i}. {t.target_id.split('#')[0]:<36} {t.score:>3}  {reason}")
    else:
        ui.info("  - No value-moving functions detected in production code.")
    ui.section("Money Flow")
    ui.info(f"  In:      {', '.join(self_disp(analysis, flow.entrypoints))[:90] or '-'}")
    ui.info(f"  Stored:  {', '.join(flow.value_holders[:3]) or '-'}")
    ui.info(f"  Out:     {', '.join(self_disp(analysis, flow.exits))[:90] or '-'}")
    ui.info(f"  Control: {', '.join(sorted({d.split('.')[-1] for d in self_disp(analysis, flow.privileged_movers)}))[:90] or '-'}")
    hidden = hidden_block(analysis.hidden_counts)
    if hidden:
        ui.section("Hidden")
        ui.info("  " + ", ".join(hidden) + " (use --show-all)")
    ui.section("Next")
    ui.info(f"  Map the protocol:     arkheionx map {args.repo}")
    ui.info(f"  Find review surfaces: arkheionx hunt {args.repo} --top 5")
    ui.info(f"  Build a review map:   arkheionx review-map {args.repo}")
    ui.section("Boundary")
    ui.info("  Local/static guidance only. Not confirmed vulnerabilities. Human review required.")
    return _exit_for(analysis)


def map_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    analysis = _run_analysis(args, root)
    payload = build_json(analysis, {}, [f"arkheionx hunt {args.repo} --top 5"])
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return _exit_for(analysis)
    artifacts = _emit(args, payload, _writer(args), "map.json")
    _print_report(render_map(analysis, args.repo, artifacts, full=bool(getattr(args, "full", False))))
    return _exit_for(analysis)


def flow_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    analysis = _run_analysis(args, root)
    mermaid = render_mermaid(analysis.money_flow)
    payload = build_json(analysis, {}, [f"arkheionx hunt {args.repo} --top 5"])
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return _exit_for(analysis)
    if getattr(args, "mermaid", False):
        print(mermaid)
        return _exit_for(analysis)
    artifacts = _emit(args, payload, _writer(args), "flow.json", {"Mermaid": ("money-flow.mmd", mermaid)})
    _print_report(render_flow(analysis, args.repo, artifacts, full=bool(getattr(args, "full", False))))
    return _exit_for(analysis)


def hunt_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    analysis = _run_analysis(args, root)
    payload = build_json(analysis, {}, [])
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return _exit_for(analysis)
    artifacts = _emit(args, payload, _writer(args), "hunt.json")
    _print_report(render_hunt(analysis, args.repo, int(getattr(args, "top", 10) or 10), artifacts, full=bool(getattr(args, "full", False))))
    return _exit_for(analysis)


# --------------------------------------------------------------------------
# prove
# --------------------------------------------------------------------------
def _parse_target(target: str) -> tuple[str, str, str, str]:
    """Return (path, contract, function, signature) components; empty if absent."""
    path = ""
    rest = target.strip()
    if ":" in rest:
        path, rest = rest.split(":", 1)
    signature = ""
    if "(" in rest:
        rest, sig = rest.split("(", 1)
        signature = "(" + sig
    contract = ""
    function = rest
    if "." in rest:
        contract, function = rest.rsplit(".", 1)
    return path.strip(), contract.strip(), function.strip(), signature.strip()


def _resolve_target(functions, target: str):
    path, contract, function, signature = _parse_target(target)
    matches = []
    for fr in functions:
        if function.lower() != fr.function_name.lower():
            continue
        if contract and contract.lower() != fr.contract_name.lower():
            continue
        if path and not fr.file_path.endswith(path) and fr.file_path != path:
            continue
        if signature and signature.replace(" ", "") not in fr.signature.replace(" ", ""):
            continue
        matches.append(fr)
    return matches


def _resolve_or_explain(args: Namespace, root: Path):
    """Return (match, error_exit_code). On success error_exit_code is None."""
    target = str(getattr(args, "target", "") or "").strip()
    if not target:
        print(f"error: --target Contract.function is required. Run `arkheionx hunt {args.repo}` to list targets.")
        return None, FAILED
    analysis = _run_analysis(args, root)
    matches = _resolve_target(analysis.all_functions, target)
    if not matches:
        print(f"error: could not resolve target `{target}`. Run `arkheionx hunt {args.repo}` to list targets.")
        return None, FAILED
    if len({(m.contract_name, m.function_name) for m in matches}) > 1:
        print("Target is ambiguous. Choose one:\n")
        ordered = sorted(matches, key=lambda x: x.contract_name)
        for i, m in enumerate(ordered, 1):
            print(f"{i}. {m.display_id}")
        print("\nThen run, for example:")
        print(f"arkheionx prove {args.repo} --target {ordered[0].display_id}")
        return None, FAILED
    return matches[0], None


def prove_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    match, err = _resolve_or_explain(args, root)
    if err is not None:
        return err

    tests, invariants = suggest_tests(match)
    scaffold = generate_scaffold(match.contract_name, match.function_name, tests, invariants)
    harness = harness_name(match.contract_name, match.function_name)
    writer = _writer(args)
    slug = target_slug(match.display_id)
    no_artifacts = bool(getattr(args, "no_artifacts", False))

    run = bool(getattr(args, "run", False))
    do_build = bool(getattr(args, "build", False))
    result = ExecResult(foundry=foundry_mod.detect_foundry(root))
    status = "scaffolded"
    evidence = HEURISTIC

    if run:
        result = execute_target(root, match.function_name)
        status, evidence = result.status, result.evidence_level
    elif do_build and result.foundry.status == foundry_mod.AVAILABLE_NOT_BUILT:
        fstat, build_out = foundry_mod.build_and_confirm(root)
        result.foundry = fstat
        result.build_status = fstat.status
        result.build_output = build_out
        if fstat.status == foundry_mod.BUILD_PASSED:
            evidence = COMPILER_CONFIRMED
        elif fstat.status == foundry_mod.BUILD_FAILED:
            status = "build_failed"
    elif result.foundry.status not in {foundry_mod.AVAILABLE_NOT_BUILT, foundry_mod.BUILD_PASSED}:
        status = "scaffolded"  # foundry not available; scaffold only

    generated_files: list[str] = []
    raw_test_path = trace_json_path = ""
    proof_json_path = writer.path_for(f"proof/{slug}/proof.json")
    if not no_artifacts:
        generated_files.append(str(writer.write_text(f"proof/{slug}/generated-test.sol", scaffold)))
        if result.build_output:
            writer.write_text(f"proof/{slug}/foundry-build.txt", result.build_output)
        if result.test_output:
            raw_test_path = str(writer.write_text(f"proof/{slug}/foundry-test.txt", result.test_output))
            trace_payload = build_trace_payload(
                match.qualified_id,
                status,
                evidence,
                raw_test_path,
                result.trace,
                target_id=match.stable_id or match.display_id,
                review_map_target=match.display_id,
                source_proof_json=str(proof_json_path),
            )
            trace_json_path = str(writer.write_text(f"proof/{slug}/trace.json", json.dumps(trace_payload, indent=2)))
    next_cmds = [f"arkheionx trace {args.repo} --target {match.display_id}"]
    payload = build_proof_payload(
        match.display_id, match.stable_id or match.display_id, str(root), status, evidence,
        result, generated_files, raw_test_path, (raw_test_path, trace_json_path), next_cmds,
        review_map_target=match.display_id,
    )
    if not no_artifacts:
        generated_files.append(str(writer.write_text(f"proof/{slug}/proof.json", json.dumps(payload, indent=2))))
        _refresh_index(args, writer)
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return SUCCESS if evidence == EXECUTION_CONFIRMED else WARNING

    lines = [
        "ARKHEIONX PROVE",
        f"Target: {match.qualified_id}",
        f"Status: {status}",
        f"Mode: {_mode_label(evidence)}",
        f"Foundry: {foundry_header(result.foundry)}",
        "",
        "Generated",
    ]
    lines += [f"  {f}" for f in generated_files]
    lines += [
        "",
        "Proof",
        f"  {_proof_note(status, result)}",
        f"  Evidence level: {evidence}",
        "",
        "Next",
    ]
    if evidence == EXECUTION_CONFIRMED:
        lines.append(f"  arkheionx trace {args.repo} --target {match.display_id}")
    else:
        lines.append("  Complete the scaffold TODOs, then run:")
        lines.append(f"  forge test --match-contract {harness} -vvvv")
        lines.append(f"  or: arkheionx prove {args.repo} --target {match.display_id} --run")
    _print_report("\n".join(lines))
    return SUCCESS if evidence == EXECUTION_CONFIRMED else WARNING


_PROOF_NOTES = {
    "no_foundry": "Foundry not available; generated scaffold only. Not proof.",
    "build_failed": "forge build failed; not proof. See foundry-build.txt.",
    "no_tests_matched": "No existing test matched this target; not proof.",
    "skipped_not_proof": "Matched tests were skipped; a skipped test is not proof.",
    "scaffolded": "Scaffold generated (contains vm.skip TODOs); not executed as proof.",
    "tested_passed": "A relevant test executed and passed (does not prove absence of a bug).",
    "tested_failed": "A relevant test executed and failed (does not by itself prove a vulnerability).",
    "tested_mixed": "Relevant tests executed with mixed results.",
}


def _proof_note(status: str, result: ExecResult) -> str:
    return _PROOF_NOTES.get(status, "Scaffold generated; not executed as proof.")


def _mode_label(evidence: str) -> str:
    return {"EXECUTION_CONFIRMED": "execution-confirmed", "COMPILER_CONFIRMED": "compiler-confirmed"}.get(evidence, "heuristic")


def trace_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    match, err = _resolve_or_explain(args, root)
    if err is not None:
        return err
    writer = _writer(args)
    slug = target_slug(match.display_id)
    next_no_proof = f"arkheionx prove {args.repo} --target {match.display_id} --run"

    if bool(getattr(args, "run", False)):
        result = execute_target(root, match.function_name)
        status, evidence = result.status, result.evidence_level
        raw_path = ""
        proof_json_path = writer.path_for(f"proof/{slug}/proof.json")
        source_proof_json = str(proof_json_path) if proof_json_path.exists() else ""
        payload = build_trace_payload(
            match.qualified_id,
            status,
            evidence,
            raw_path,
            result.trace,
            target_id=match.stable_id or match.display_id,
            review_map_target=match.display_id,
            source_proof_json=source_proof_json,
        )
        if not getattr(args, "no_artifacts", False) and result.test_output:
            raw_path = str(writer.write_text(f"proof/{slug}/foundry-test.txt", result.test_output))
            payload = build_trace_payload(
                match.qualified_id,
                status,
                evidence,
                raw_path,
                result.trace,
                target_id=match.stable_id or match.display_id,
                review_map_target=match.display_id,
                source_proof_json=source_proof_json,
            )
            tj = str(writer.write_text(f"proof/{slug}/trace.json", json.dumps(payload, indent=2)))
            artifacts = {"Raw": raw_path, "JSON": tj}
            _refresh_index(args, writer)
        else:
            artifacts = {}
        if getattr(args, "json", False):
            print(json.dumps(payload, indent=2))
            return SUCCESS if evidence == EXECUTION_CONFIRMED else WARNING
        nxt = f"arkheionx evidence {args.repo} --target {match.display_id}" if evidence == EXECUTION_CONFIRMED else next_no_proof
        _print_report(render_trace(match.qualified_id, args.repo, status, evidence, foundry_header(result.foundry), result.trace, artifacts, nxt))
        return SUCCESS if evidence == EXECUTION_CONFIRMED else WARNING

    # No --run: summarize an existing proof artifact if present.
    trace_json = writer.path_for(f"proof/{slug}/trace.json")
    if trace_json.exists():
        payload = json.loads(trace_json.read_text(encoding="utf-8"))
        evidence = payload.get("evidence_level", HEURISTIC)
        artifacts = {"Raw": payload.get("source_raw_output", ""), "JSON": str(trace_json)}
        if getattr(args, "json", False):
            print(json.dumps(payload, indent=2))
            return SUCCESS if evidence == EXECUTION_CONFIRMED else WARNING
        nxt = f"arkheionx evidence {args.repo} --target {match.display_id}" if evidence == EXECUTION_CONFIRMED else next_no_proof
        _print_report(render_trace(match.qualified_id, args.repo, payload.get("status", ""), evidence, "ready", payload, artifacts, nxt))
        return SUCCESS if evidence == EXECUTION_CONFIRMED else WARNING

    if getattr(args, "json", False):
        print(json.dumps(build_trace_payload(match.qualified_id, "no_proof", HEURISTIC, "", {}), indent=2))
        return WARNING
    _print_report(render_trace(match.qualified_id, args.repo, "no_proof", HEURISTIC, foundry_header(foundry_mod.detect_foundry(root)), {}, {}, next_no_proof))
    return WARNING


# --------------------------------------------------------------------------
# doctor
# --------------------------------------------------------------------------
def _git_info(root: Path) -> str:
    if shutil.which("git") is None or not (root / ".git").exists():
        return ""
    try:
        branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=root, capture_output=True, text=True, timeout=10)
        dirty = subprocess.run(["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return ""
    if branch.returncode != 0:
        return ""
    state = "dirty" if dirty.stdout.strip() else "clean"
    return f"{branch.stdout.strip()} ({state})"


def _doctor_install_view(root: Path) -> int:
    """Compact install-health command-center: arkheionx doctor --install."""
    import os
    import sys

    foundry_status = foundry_mod.detect_foundry(root, with_version=True)
    cmd_path = shutil.which("arkheionx") or "not on PATH"
    bin_hint = str(Path.home() / ".arkheionx" / "bin")
    on_path = any(p == bin_hint for p in os.environ.get("PATH", "").split(os.pathsep))
    reachable = on_path or cmd_path != "not on PATH"

    install_dir = Path(os.environ.get("ARKHEIONX_INSTALL_DIR", str(Path.home() / ".arkheionx")))
    receipt = install_dir / "install.json"

    lines = screen.header("ArkheionX Doctor", "LOCAL / STATIC / INSTALL HEALTH")
    lines += screen.kv_rows([("Status", screen.chip("OK"))])
    lines += screen.section("Install")
    lines += screen.chip_rows([
        ("OK" if reachable else "REVIEW", "ArkheionX command", cmd_path),
        ("OK", "Python runtime", f"{sys.executable} ({platform.python_version()})"),
        ("OK", "Package import", "ok"),
        ("OK", "Package version", __import__("arkheionx").__version__),
    ])
    lines += screen.section("Foundry")
    lines += screen.chip_rows([
        ("OK" if foundry_status.forge_available else "REVIEW", "forge", foundry_status.forge_version or "missing"),
        ("LOCAL", "mode", foundry_header(foundry_status)),
    ])
    lines += screen.section("PATH")
    if reachable:
        lines.append("ArkheionX is reachable on your PATH.")
    else:
        lines.append(f'export PATH="{bin_hint}:$PATH"')
    if receipt.is_file():
        try:
            data = json.loads(receipt.read_text(encoding="utf-8"))
            version = data.get("installed_version") or data.get("ref")
            method = data.get("install_method") or data.get("source_kind")
            if version or method:
                lines.append(f"Receipt: {' '.join(str(v) for v in (method, version) if v)}")
        except Exception:
            lines.append("Receipt: malformed (reinstall to repair)")
    lines += screen.section("Next")
    lines.append(f"arkheionx open {_rel_display(str(root), root) or '.'}")
    print("\n".join(lines))
    return SUCCESS


def doctor_command(args: Namespace) -> int:
    repo = getattr(args, "repo", ".") or "."
    root = _resolve_root(repo) or Path.cwd()
    if getattr(args, "install", False):
        return _doctor_install_view(root)
    import os

    foundry_status = foundry_mod.detect_foundry(root, with_version=True)
    try:
        analysis = analyze(root, use_foundry=False, top=10)
        sources, _tests = find_solidity_files(root)
        active = analysis.snapshot.contracts_analyzed
    except Exception as exc:  # package/parse failure
        out = screen.header("ArkheionX Doctor", "LOCAL / STATIC / HUMAN REVIEW REQUIRED")
        out += screen.kv_rows([("Status", screen.chip("FAIL"))])
        out += ["", f"Error: {exc}"]
        print("\n".join(out))
        return FAILED

    compiler_ready = foundry_status.has_foundry_toml and foundry_status.forge_available
    status_chip = "OK" if foundry_status.status in {foundry_mod.AVAILABLE_NOT_BUILT, foundry_mod.BUILD_PASSED} else "WARN"
    version = __import__("arkheionx").__version__
    pyver = platform.python_version()
    git = _git_info(root)
    git_disp = git.replace("(", "").replace(")", "").strip() if git else ""
    writable = os.access(root, os.W_OK)

    lines = screen.header("ArkheionX Doctor", "LOCAL / STATIC / HUMAN REVIEW REQUIRED")
    top_rows = [("Status", screen.chip(status_chip)), ("Version", version), ("Python", pyver)]
    if git_disp:
        top_rows.append(("Git", git_disp))
    lines += screen.kv_rows(top_rows)

    lines += screen.section("Environment")
    env_rows = [("OK", "ArkheionX package", version), ("OK", "Python runtime", pyver)]
    if git_disp:
        env_rows.append(("OK", "Git checkout", git_disp))
    lines += screen.chip_rows(env_rows)

    lines += screen.section("Project")
    lines += screen.chip_rows([
        ("OK" if foundry_status.has_foundry_toml else "REVIEW", "Foundry project",
         "detected" if foundry_status.has_foundry_toml else "not detected"),
        ("OK", "Solidity files", str(len(sources))),
        ("OK", "Active contracts", str(active)),
        ("OK", "Rule packs", str(len(list_rule_packs()))),
        ("OK" if writable else "REVIEW", "Artifacts directory", "writable" if writable else "read-only"),
    ])

    lines += screen.section("Safety")
    lines += screen.chip_rows([
        ("LOCAL", "RPC calls", "disabled by default"),
        ("LOCAL", "Live-chain actions", "disabled"),
        ("LOCAL", "Private keys", "not requested"),
        ("LOCAL", "Analysis", "authorized local/static only"),
    ])

    lines += screen.section("Next")
    if compiler_ready:
        lines.append("Run `arkheionx map .` then `arkheionx hunt .` (use --build for compiler-confirmed results).")
    elif not foundry_status.has_foundry_toml:
        lines.append("Run inside a Foundry repository for compiler-confirmed results.")
    else:
        lines.append("Install Foundry (forge) for compiler-confirmed results.")
    lines.append(f"arkheionx review-map {_rel_display(str(root), root) or '.'}")
    print("\n".join(lines))
    return SUCCESS


# --------------------------------------------------------------------------
# evidence / report (v2.3.0)
# --------------------------------------------------------------------------
_PROVEN = {"EXECUTION_CONFIRMED", "EVIDENCE_READY"}


def _resolve_match(args: Namespace, root: Path):
    """Return (match, analysis, error_code). error_code is None on success."""
    target = str(getattr(args, "target", "") or "").strip()
    if not target:
        print("error: --target Contract.function is required")
        return None, None, FAILED
    analysis = _run_analysis(args, root)
    matches = _resolve_target(analysis.all_functions, target)
    if not matches:
        print(f"error: could not resolve target `{target}`. Run `arkheionx hunt {args.repo}` to list targets.")
        return None, None, FAILED
    if len({(m.contract_name, m.function_name) for m in matches}) > 1:
        print("Target is ambiguous. Choose one:\n")
        ordered = sorted(matches, key=lambda x: x.contract_name)
        for i, m in enumerate(ordered, 1):
            print(f"{i}. {m.display_id}")
        print(f"\nThen run, for example:\narkheionx {args.command} {args.repo} --target {ordered[0].display_id}")
        return None, None, FAILED
    return matches[0], analysis, None


def _display_from_target_id(target_id: str) -> str:
    tail = target_id.split(":")[-1].split("#")[0]
    return tail.split("(")[0]


def _read_json_file(path_str: str):
    candidate = Path(path_str).expanduser()
    if not candidate.exists():
        return None
    try:
        return json.loads(candidate.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None


def evidence_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    writer = _writer(args)
    proof_override = trace_override = None
    proof_source_path = trace_source_path = ""
    from_proof = str(getattr(args, "from_proof", "") or "").strip()
    if from_proof:
        proof_path = Path(from_proof).expanduser()
        proof_override = _read_json_file(str(proof_path))
        if proof_override is None:
            print(f"error: could not read proof artifact: {from_proof}")
            return FAILED
        proof_source_path = str(proof_path.resolve())
        trace_path = proof_path.parent / "trace.json"
        trace_override = _read_json_file(str(trace_path))
        if trace_override is not None:
            trace_source_path = str(trace_path.resolve())
        if not getattr(args, "target", ""):
            args.target = _display_from_target_id(str(proof_override.get("target_id", proof_override.get("target", ""))))

    match, analysis, err = _resolve_match(args, root)
    if err is not None:
        return err
    pkg = build_evidence(
        match, root, writer, analysis,
        write=not getattr(args, "no_artifacts", False),
        proof_override=proof_override, trace_override=trace_override,
        proof_source_path=proof_source_path, trace_source_path=trace_source_path,
    )
    _refresh_index(args, writer)
    if getattr(args, "json", False):
        print(json.dumps(pkg.payload, indent=2) if pkg.payload else json.dumps({"status": pkg.status, "next": pkg.next_command}))
        return SUCCESS if pkg.evidence_level in _PROVEN else WARNING
    _print_report(render_evidence(pkg, args.repo))
    return SUCCESS if pkg.evidence_level in _PROVEN else WARNING


def report_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    writer = _writer(args)
    from_evidence = str(getattr(args, "from_evidence", "") or "").strip()
    evidence_source_path = ""

    if from_evidence:
        evidence = _read_json_file(from_evidence)
        if evidence is None:
            print(f"error: could not read evidence package: {from_evidence}")
            return FAILED
        evidence_source_path = str(Path(from_evidence).expanduser().resolve())
    else:
        match, analysis, err = _resolve_match(args, root)
        if err is not None:
            return err
        pkg = build_evidence(match, root, writer, analysis, write=not getattr(args, "no_artifacts", False))
        if pkg.status == "no_proof":
            print(
                "ARKHEIONX REPORT\n"
                f"Project: {args.repo}\nTarget: {pkg.target}\nStatus: no-evidence\nMode: heuristic\n\n"
                "No evidence package found.\n\nNext\n"
                f"  arkheionx prove {args.repo} --target {match.display_id} --run\n"
                f"  arkheionx evidence {args.repo} --target {match.display_id}"
            )
            return WARNING
        evidence = pkg.payload
        evidence_source_path = pkg.json_path

    draft = build_report(
        evidence,
        root,
        writer,
        write=not getattr(args, "no_artifacts", False),
        evidence_source_path=evidence_source_path,
    )
    _refresh_index(args, writer)
    if getattr(args, "json", False):
        print(json.dumps(draft.payload, indent=2))
        return SUCCESS if draft.evidence_level in _PROVEN else WARNING
    _print_report(render_report(draft, args.repo))
    return SUCCESS if draft.evidence_level in _PROVEN else WARNING


# --------------------------------------------------------------------------
# evidence-status / validate-artifacts (v2.4.0)
# --------------------------------------------------------------------------
def _refresh_index(args: Namespace, writer) -> None:
    if getattr(args, "no_artifacts", False):
        return
    try:
        _evindex.refresh_index(args.repo, writer)
    except Exception:  # index is a cache; never fail the command over it
        pass


def evidence_status_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    writer = _writer(args)
    target = str(getattr(args, "target", "") or "").strip() or None
    payload = build_status(args.repo, writer, target=target)
    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
    else:
        _print_report(render_status(payload, args.repo))
    return SUCCESS if payload["status"] == "ok" else WARNING


def validate_artifacts_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    writer = _writer(args)
    counts, issues = validate_artifacts(writer)
    if getattr(args, "json", False):
        print(json.dumps({"status": "warning" if issues else "ok", "checked": counts, "issues": issues}, indent=2))
    else:
        _print_report(render_validate(counts, issues, args.repo))
    return WARNING if issues else SUCCESS


# --------------------------------------------------------------------------
# review-map (v3.1.0)
# --------------------------------------------------------------------------
def _rel_display(path: str, root: Path) -> str:
    try:
        return Path(path).resolve().relative_to(root.resolve()).as_posix()
    except ValueError:
        return path


def _review_map_artifact_roots(args: Namespace) -> list[Path]:
    out = str(getattr(args, "out", "") or "").strip()
    return [Path(out).expanduser()] if out else []


def review_map_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"ArkheionX error: input path not found or not a directory: {args.repo}")
        print("Next: run this command with a local repository path you are authorized to review.")
        return FAILED
    inspect_start = time.monotonic()
    sources, test_files = find_solidity_files(root)
    inspect_elapsed = time.monotonic() - inspect_start
    if not sources:
        print(f"Error: no Solidity files found in {args.repo}.")
        print("Next: run inside a Solidity/Foundry repository or try a bundled demo:")
        print("  arkheionx demo --copy amm-swap ./arkheionx-demo")
        print("  arkheionx review-map ./arkheionx-demo")
        return FAILED

    top = getattr(args, "top", 10)
    top = 10 if top is None else int(top)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED

    target = str(getattr(args, "target", "") or "").strip()
    include_low = bool(getattr(args, "include_low_confidence", False))

    # Machine-readable path: pure JSON only. No banner, progress, spinner, color.
    if getattr(args, "json", False):
        try:
            review_map = build_review_map(
                root,
                top=top,
                target=target,
                include_low_confidence=include_low,
                artifact_roots=_review_map_artifact_roots(args),
            )
        except ValueError as exc:
            print(f"error: could not resolve target `{exc}`. Run `arkheionx review-map {args.repo}` to list review targets.")
            return FAILED
        print(json.dumps(review_map.to_payload(), indent=2))
        return SUCCESS if status_of(review_map) == "ok" else WARNING

    return _review_map_human(args, root, sources, test_files, inspect_elapsed, top, target, include_low)


def _review_map_human(args, root, sources, test_files, inspect_elapsed, top, target, include_low) -> int:
    import sys

    no_write = bool(getattr(args, "no_write", False))
    out = str(getattr(args, "out", "") or "").strip()
    out_dir = Path(out).expanduser() if out else default_out_dir(root)
    repo = args.repo
    stream = sys.stdout

    head = screen.header(
        "ArkheionX Review Map",
        "LOCAL / STATIC / NO RPC / HUMAN REVIEW REQUIRED",
        stream=stream,
    )
    head += screen.kv_rows([
        ("Target", repo),
        ("Mode", "heuristic review guidance"),
        ("Writes", "in-memory only (--no-write)" if no_write else _rel_display(str(out_dir), root)),
    ], stream=stream)
    print("\n".join(head))

    # Progress: real multi-step work with a TTY-only spinner; static rows in CI.
    print("\n".join(screen.section("Progress", stream=stream)))
    reporter = screen.StepReporter(
        ["Inspect repository", "Map review surface", "Write artifacts"], stream=stream,
    )
    with reporter.step("Inspect repository") as detail:
        detail.detail = f"{len(sources)} source files, {len(test_files)} test files"
    try:
        with reporter.step("Map review surface") as detail:
            review_map = build_review_map(
                root,
                top=top,
                target=target,
                include_low_confidence=include_low,
                artifact_roots=_review_map_artifact_roots(args),
            )
            s = review_map.summary
            detail.detail = (
                f"{s.contracts_analyzed} contracts, {s.functions_mapped} functions, "
                f"{s.value_paths} value paths, {s.test_gaps} test gaps"
            )
    except ValueError as exc:
        print(f"ArkheionX error: could not resolve target `{exc}`.")
        print(f"Next: run `arkheionx review-map {repo}` to list review targets.")
        return FAILED

    artifacts: dict[str, str] = {}
    if no_write:
        with reporter.step("Write artifacts") as detail:
            detail.detail = "in-memory only (--no-write)"
    else:
        try:
            with reporter.step("Write artifacts") as detail:
                written = write_artifacts(review_map, out_dir)
                detail.detail = f"{len(written)} files"
        except OSError as exc:
            print(f"ArkheionX error: could not write artifacts to {out_dir}: {exc}")
            print("Next: choose a writable --out directory or pass --no-write.")
            return FAILED
        artifacts = {name: _rel_display(path, root) for name, path in written.items()}

    body: list[str] = []
    body += _review_map_inspect_first(review_map, repo, top, stream)
    body += _review_map_summary(review_map, stream)
    body += _review_map_artifacts(artifacts, stream)
    body += _review_map_next(repo, artifacts, stream)
    status = status_of(review_map)
    body += screen.section("Boundary", stream=stream)
    body.append("Review guidance only. Not confirmed vulnerabilities. Human review required.")
    body.append(
        "Compiler-confirmed (exit code 0)."
        if status == "ok"
        else "Heuristic review guidance; exit code 1 is intentional, not a crash."
    )
    print("\n".join(body))
    return SUCCESS if status == "ok" else WARNING


def _review_map_inspect_first(rm, repo: str, top: int, stream=None) -> list[str]:
    notes = rm.reviewer_notes[: min(top, 3)]
    if not notes:
        return []
    out = screen.section("Inspect first", stream=stream)
    chip_width = max(len(note.priority) for note in notes)
    label_width = len("Signals")
    for i, note in enumerate(notes, 1):
        why = note.body.split(".")[0].strip() or "value-relevant surface"
        step = note.next_step.replace("arkheionx prove . ", f"arkheionx prove {repo} ")
        priority = screen.chip(note.priority, chip_width, stream=stream)
        out.append(f"{i}  {priority}   {note.title}")
        out.append(f"{'Signals'.ljust(label_width)}  {why}")
        out.append(f"{'Next'.ljust(label_width)}  {step}")
        out.append("")
    if out and out[-1] == "":
        out.pop()
    return out


def _review_map_summary(rm, stream=None) -> list[str]:
    s = rm.summary
    out = screen.section("Summary", stream=stream)
    out += screen.kv_rows([
        ("Contracts", s.contracts_analyzed),
        ("Functions", s.functions_mapped),
        ("Value paths", s.value_paths),
        ("Assumptions", s.assumptions),
        ("Test gaps", s.test_gaps),
        ("Proof suggestions", s.proof_suggestions),
    ], stream=stream)
    return out


def _review_map_artifacts(artifacts: dict[str, str], stream=None) -> list[str]:
    if not artifacts:
        return []
    # Terminal shows only the three primary artifacts; the full set stays on disk.
    primary = (("Review map", "review-map.md"), ("Test gaps", "test-gaps.json"), ("Proof plan", "proof-plan.json"))
    rows = [(label, screen.dim(artifacts[name], stream=stream)) for label, name in primary if name in artifacts]
    if not rows:
        return []
    return screen.section("Artifacts", stream=stream) + screen.kv_rows(rows, stream=stream)


def _review_map_next(repo: str, artifacts: dict[str, str], stream=None) -> list[str]:
    rows: list[tuple[str, str]] = []
    if "review-map.md" in artifacts:
        rows.append(("Open review map", screen.dim(artifacts["review-map.md"], stream=stream)))
    if "test-gaps.json" in artifacts:
        rows.append(("Inspect gaps", screen.dim(artifacts["test-gaps.json"], stream=stream)))
    rows.append(("Machine readable", f"arkheionx review-map {repo} --json"))
    return screen.section("Next", stream=stream) + screen.kv_rows(rows[:3], stream=stream)


# --------------------------------------------------------------------------
# test-gap-map (v3.3.0 focused review-map view)
# --------------------------------------------------------------------------
def _test_gap_map_artifact_path(args: Namespace, root: Path) -> Path:
    out = str(getattr(args, "out", "") or "").strip()
    out_dir = Path(out).expanduser() if out else default_out_dir(root)
    return out_dir / "test-gap-map.json"


def _valid_test_gap_map_payload(payload: object) -> bool:
    return (
        isinstance(payload, dict)
        and isinstance(payload.get("summary"), dict)
        and isinstance(payload.get("items"), list)
    )


def _read_test_gap_map_artifact(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if _valid_test_gap_map_payload(payload) else None


def _test_gap_map_exit(payload: dict) -> int:
    return SUCCESS if payload.get("mode") == "compiler-confirmed" else WARNING


def _build_test_gap_map_payload(args: Namespace, root: Path, top: int, target: str, include_low: bool) -> tuple[dict | None, dict[str, str] | None, int]:
    sources, _test_files = find_solidity_files(root)
    if not sources:
        print(f"Error: no Solidity files found in {args.repo}.")
        print("Next: run inside a Solidity/Foundry repository or try a bundled demo:")
        print("  arkheionx demo --copy amm-swap ./arkheionx-demo")
        print("  arkheionx test-gap-map ./arkheionx-demo")
        return None, None, FAILED

    try:
        review_map = build_review_map(root, top=top, target=target, include_low_confidence=include_low)
    except ValueError as exc:
        print(f"error: could not resolve target `{exc}`. Run `arkheionx review-map {args.repo}` to list review targets.")
        return None, None, FAILED

    payload = build_test_gap_map(review_map)
    artifacts: dict[str, str] = {}
    if not bool(getattr(args, "no_write", False)):
        out_json = _test_gap_map_artifact_path(args, root)
        out_dir = out_json.parent
        try:
            written = write_artifacts(review_map, out_dir)
        except OSError as exc:
            print(f"error: could not write artifacts to {out_dir}: {exc}")
            return None, None, FAILED
        artifacts = {name: _rel_display(path, root) for name, path in written.items()}
    return payload, artifacts, _test_gap_map_exit(payload)


def test_gap_map_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED

    top = getattr(args, "top", 5)
    top = 5 if top is None else int(top)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED

    target = str(getattr(args, "target", "") or "").strip()
    include_low = bool(getattr(args, "include_low_confidence", False))
    artifact_path = _test_gap_map_artifact_path(args, root)
    can_read_existing = artifact_path.is_file() and not target and not include_low

    payload: dict | None
    artifacts: dict[str, str] = {}
    source = "built from review-map"
    if can_read_existing:
        payload = _read_test_gap_map_artifact(artifact_path)
        if payload is None:
            print(f"error: could not read Test Gap Map artifact: {artifact_path}")
            return FAILED
        source = f"existing artifact ({_rel_display(str(artifact_path), root)})"
        exit_code = _test_gap_map_exit(payload)
    else:
        payload, built_artifacts, exit_code = _build_test_gap_map_payload(args, root, top, target, include_low)
        if payload is None:
            return exit_code
        artifacts = built_artifacts or {}
        if bool(getattr(args, "no_write", False)):
            source = "in-memory review-map build (--no-write)"
        elif artifacts:
            source = f"built from review-map; wrote {_rel_display(str(_test_gap_map_artifact_path(args, root).parent), root)}"

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return exit_code

    text = render_test_gap_map_cli(payload, args.repo, top=top, source=source)
    if artifacts and "test-gap-map.md" in artifacts:
        text += f"\nArtifacts\n  {artifacts['test-gap-map.md']}\n  {artifacts.get('test-gap-map.json', '')}\n"
    _print_report(text)
    return exit_code


# --------------------------------------------------------------------------
# value-paths (v3.3.0 focused review-map view)
# --------------------------------------------------------------------------
def _value_paths_artifact_path(args: Namespace, root: Path) -> Path:
    out = str(getattr(args, "out", "") or "").strip()
    out_dir = Path(out).expanduser() if out else default_out_dir(root)
    return out_dir / "value-paths.json"


def _valid_value_paths_payload(payload: object) -> bool:
    if isinstance(payload, list):
        return True
    return isinstance(payload, dict) and isinstance(payload.get("value_paths"), list)


def _read_value_paths_artifact(path: Path) -> object | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if _valid_value_paths_payload(payload) else None


def _read_review_map_mode(out_dir: Path) -> str:
    try:
        payload = json.loads((out_dir / "review-map.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    return str(payload.get("mode", "")).strip() if isinstance(payload, dict) else ""


def _value_paths_exit(payload: object) -> int:
    if isinstance(payload, dict) and payload.get("mode") == "compiler-confirmed":
        return SUCCESS
    return WARNING


def _build_value_paths_payload(args: Namespace, root: Path, top: int, target: str, include_low: bool) -> tuple[object | None, dict[str, str] | None, int, str]:
    sources, _test_files = find_solidity_files(root)
    if not sources:
        print(f"Error: no Solidity files found in {args.repo}.")
        print("Next: run inside a Solidity/Foundry repository or try a bundled demo:")
        print("  arkheionx demo --copy lending-vault ./arkheionx-demo")
        print("  arkheionx value-paths ./arkheionx-demo")
        return None, None, FAILED, ""

    try:
        review_map = build_review_map(root, top=top, target=target, include_low_confidence=include_low)
    except ValueError as exc:
        print(f"error: could not resolve target `{exc}`. Run `arkheionx review-map {args.repo}` to list review targets.")
        return None, None, FAILED, ""

    payload = build_value_paths_payload(review_map)
    artifacts: dict[str, str] = {}
    if not bool(getattr(args, "no_write", False)):
        out_json = _value_paths_artifact_path(args, root)
        out_dir = out_json.parent
        try:
            written = write_artifacts(review_map, out_dir)
        except OSError as exc:
            print(f"error: could not write artifacts to {out_dir}: {exc}")
            return None, None, FAILED, ""
        artifacts = {name: _rel_display(path, root) for name, path in written.items()}
    return payload, artifacts, SUCCESS if status_of(review_map) == "ok" else WARNING, review_map.mode


def value_paths_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED

    top = getattr(args, "top", 5)
    top = 5 if top is None else int(top)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED

    target = str(getattr(args, "target", "") or "").strip()
    include_low = bool(getattr(args, "include_low_confidence", False))
    artifact_path = _value_paths_artifact_path(args, root)
    can_read_existing = artifact_path.is_file() and not target and not include_low

    payload: object | None
    artifacts: dict[str, str] = {}
    mode = ""
    source = "built from review-map"
    if can_read_existing:
        payload = _read_value_paths_artifact(artifact_path)
        if payload is None:
            print(f"error: could not read Value Paths artifact: {artifact_path}")
            return FAILED
        mode = _read_review_map_mode(artifact_path.parent)
        source = f"existing artifact ({_rel_display(str(artifact_path), root)})"
        exit_code = _value_paths_exit(payload)
    else:
        payload, built_artifacts, exit_code, mode = _build_value_paths_payload(args, root, top, target, include_low)
        if payload is None:
            return exit_code
        artifacts = built_artifacts or {}
        if bool(getattr(args, "no_write", False)):
            source = "in-memory review-map build (--no-write)"
        elif artifacts:
            source = f"built from review-map; wrote {_rel_display(str(_value_paths_artifact_path(args, root).parent), root)}"

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return exit_code

    text = render_value_paths_cli(payload, args.repo, top=top, source=source, mode=mode)
    if artifacts and "value-paths.json" in artifacts:
        text += f"\nArtifacts\n  {artifacts['value-paths.json']}\n"
    _print_report(text)
    return exit_code


# --------------------------------------------------------------------------
# assumptions (v3.3.0 focused review-map view)
# --------------------------------------------------------------------------
def _assumptions_artifact_path(args: Namespace, root: Path) -> Path:
    out = str(getattr(args, "out", "") or "").strip()
    out_dir = Path(out).expanduser() if out else default_out_dir(root)
    return out_dir / "assumptions.json"


def _valid_assumptions_payload(payload: object) -> bool:
    if isinstance(payload, list):
        return True
    return isinstance(payload, dict) and isinstance(payload.get("assumptions"), list)


def _read_assumptions_artifact(path: Path) -> object | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if _valid_assumptions_payload(payload) else None


def _assumptions_exit(payload: object) -> int:
    if isinstance(payload, dict) and payload.get("mode") == "compiler-confirmed":
        return SUCCESS
    return WARNING


def _build_assumptions_payload(args: Namespace, root: Path, top: int, target: str, include_low: bool) -> tuple[object | None, dict[str, str] | None, int, str]:
    sources, _test_files = find_solidity_files(root)
    if not sources:
        print(f"Error: no Solidity files found in {args.repo}.")
        print("Next: run inside a Solidity/Foundry repository or try a bundled demo:")
        print("  arkheionx demo --copy lending-vault ./arkheionx-demo")
        print("  arkheionx assumptions ./arkheionx-demo")
        return None, None, FAILED, ""

    try:
        review_map = build_review_map(root, top=top, target=target, include_low_confidence=include_low)
    except ValueError as exc:
        print(f"error: could not resolve target `{exc}`. Run `arkheionx review-map {args.repo}` to list review targets.")
        return None, None, FAILED, ""

    payload = build_assumptions_payload(review_map)
    artifacts: dict[str, str] = {}
    if not bool(getattr(args, "no_write", False)):
        out_json = _assumptions_artifact_path(args, root)
        out_dir = out_json.parent
        try:
            written = write_artifacts(review_map, out_dir)
        except OSError as exc:
            print(f"error: could not write artifacts to {out_dir}: {exc}")
            return None, None, FAILED, ""
        artifacts = {name: _rel_display(path, root) for name, path in written.items()}
    return payload, artifacts, SUCCESS if status_of(review_map) == "ok" else WARNING, review_map.mode


def assumptions_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED

    top = getattr(args, "top", 5)
    top = 5 if top is None else int(top)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED

    target = str(getattr(args, "target", "") or "").strip()
    include_low = bool(getattr(args, "include_low_confidence", False))
    artifact_path = _assumptions_artifact_path(args, root)
    can_read_existing = artifact_path.is_file() and not target and not include_low

    payload: object | None
    artifacts: dict[str, str] = {}
    mode = ""
    source = "built from review-map"
    if can_read_existing:
        payload = _read_assumptions_artifact(artifact_path)
        if payload is None:
            print(f"error: could not read Assumptions artifact: {artifact_path}")
            return FAILED
        mode = _read_review_map_mode(artifact_path.parent)
        source = f"existing artifact ({_rel_display(str(artifact_path), root)})"
        exit_code = _assumptions_exit(payload)
    else:
        payload, built_artifacts, exit_code, mode = _build_assumptions_payload(args, root, top, target, include_low)
        if payload is None:
            return exit_code
        artifacts = built_artifacts or {}
        if bool(getattr(args, "no_write", False)):
            source = "in-memory review-map build (--no-write)"
        elif artifacts:
            source = f"built from review-map; wrote {_rel_display(str(_assumptions_artifact_path(args, root).parent), root)}"

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return exit_code

    text = render_assumptions_cli(payload, args.repo, top=top, source=source, mode=mode)
    if artifacts and "assumptions.json" in artifacts:
        text += f"\nArtifacts\n  {artifacts['assumptions.json']}\n"
    _print_report(text)
    return exit_code


# --------------------------------------------------------------------------
# proof-plan (v3.3.0 focused review-map view)
# --------------------------------------------------------------------------
def _proof_plan_artifact_path(args: Namespace, root: Path) -> Path:
    out = str(getattr(args, "out", "") or "").strip()
    out_dir = Path(out).expanduser() if out else default_out_dir(root)
    return out_dir / "proof-plan.json"


def _valid_proof_plan_payload(payload: object) -> bool:
    if isinstance(payload, list):
        return True
    return isinstance(payload, dict) and isinstance(payload.get("proof_suggestions"), list)


def _read_proof_plan_artifact(path: Path) -> object | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if _valid_proof_plan_payload(payload) else None


def _proof_plan_exit(payload: object) -> int:
    if isinstance(payload, dict) and payload.get("mode") == "compiler-confirmed":
        return SUCCESS
    return WARNING


def _build_proof_plan_payload(args: Namespace, root: Path, top: int, target: str, include_low: bool) -> tuple[object | None, dict[str, str] | None, int, str]:
    sources, _test_files = find_solidity_files(root)
    if not sources:
        print(f"Error: no Solidity files found in {args.repo}.")
        print("Next: run inside a Solidity/Foundry repository or try a bundled demo:")
        print("  arkheionx demo --copy lending-vault ./arkheionx-demo")
        print("  arkheionx proof-plan ./arkheionx-demo")
        return None, None, FAILED, ""

    try:
        review_map = build_review_map(root, top=top, target=target, include_low_confidence=include_low)
    except ValueError as exc:
        print(f"error: could not resolve target `{exc}`. Run `arkheionx review-map {args.repo}` to list review targets.")
        return None, None, FAILED, ""

    payload = build_proof_plan_payload(review_map)
    artifacts: dict[str, str] = {}
    if not bool(getattr(args, "no_write", False)):
        out_json = _proof_plan_artifact_path(args, root)
        out_dir = out_json.parent
        try:
            written = write_artifacts(review_map, out_dir)
        except OSError as exc:
            print(f"error: could not write artifacts to {out_dir}: {exc}")
            return None, None, FAILED, ""
        artifacts = {name: _rel_display(path, root) for name, path in written.items()}
    return payload, artifacts, SUCCESS if status_of(review_map) == "ok" else WARNING, review_map.mode


def proof_plan_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED

    top = getattr(args, "top", 5)
    top = 5 if top is None else int(top)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED

    target = str(getattr(args, "target", "") or "").strip()
    include_low = bool(getattr(args, "include_low_confidence", False))
    artifact_path = _proof_plan_artifact_path(args, root)
    can_read_existing = artifact_path.is_file() and not target and not include_low

    payload: object | None
    artifacts: dict[str, str] = {}
    mode = ""
    source = "built from review-map"
    if can_read_existing:
        payload = _read_proof_plan_artifact(artifact_path)
        if payload is None:
            print(f"error: could not read Proof Plan artifact: {artifact_path}")
            return FAILED
        mode = _read_review_map_mode(artifact_path.parent)
        source = f"existing artifact ({_rel_display(str(artifact_path), root)})"
        exit_code = _proof_plan_exit(payload)
    else:
        payload, built_artifacts, exit_code, mode = _build_proof_plan_payload(args, root, top, target, include_low)
        if payload is None:
            return exit_code
        artifacts = built_artifacts or {}
        if bool(getattr(args, "no_write", False)):
            source = "in-memory review-map build (--no-write)"
        elif artifacts:
            source = f"built from review-map; wrote {_rel_display(str(_proof_plan_artifact_path(args, root).parent), root)}"

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return exit_code

    text = render_proof_plan_cli(payload, args.repo, top=top, source=source, mode=mode)
    if artifacts and "proof-plan.json" in artifacts:
        text += f"\nArtifacts\n  {artifacts['proof-plan.json']}\n"
    _print_report(text)
    return exit_code


# --------------------------------------------------------------------------
# evidence-links (v3.3.0 focused review-map view)
# --------------------------------------------------------------------------
def _evidence_links_artifact_path(args: Namespace, root: Path) -> Path:
    out = str(getattr(args, "out", "") or "").strip()
    out_dir = Path(out).expanduser() if out else default_out_dir(root)
    return out_dir / "evidence-links.json"


def _valid_evidence_links_payload(payload: object) -> bool:
    if isinstance(payload, list):
        return True
    return isinstance(payload, dict) and isinstance(payload.get("evidence_links"), list)


def _read_evidence_links_artifact(path: Path) -> object | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return payload if _valid_evidence_links_payload(payload) else None


def _evidence_links_exit(payload: object) -> int:
    if isinstance(payload, dict) and payload.get("mode") == "compiler-confirmed":
        return SUCCESS
    return WARNING


def _build_evidence_links_payload(args: Namespace, root: Path, top: int, target: str, include_low: bool) -> tuple[object | None, dict[str, str] | None, int, str]:
    sources, _test_files = find_solidity_files(root)
    if not sources:
        print(f"Error: no Solidity files found in {args.repo}.")
        print("Next: run inside a Solidity/Foundry repository or try a bundled demo:")
        print("  arkheionx demo --copy lending-vault ./arkheionx-demo")
        print("  arkheionx evidence-links ./arkheionx-demo")
        return None, None, FAILED, ""

    try:
        review_map = build_review_map(
            root,
            top=top,
            target=target,
            include_low_confidence=include_low,
            artifact_roots=_review_map_artifact_roots(args),
        )
    except ValueError as exc:
        print(f"error: could not resolve target `{exc}`. Run `arkheionx review-map {args.repo}` to list review targets.")
        return None, None, FAILED, ""

    payload = build_evidence_links_payload(review_map)
    artifacts: dict[str, str] = {}
    if not bool(getattr(args, "no_write", False)):
        out_json = _evidence_links_artifact_path(args, root)
        out_dir = out_json.parent
        try:
            written = write_artifacts(review_map, out_dir)
        except OSError as exc:
            print(f"error: could not write artifacts to {out_dir}: {exc}")
            return None, None, FAILED, ""
        artifacts = {name: _rel_display(path, root) for name, path in written.items()}
    return payload, artifacts, SUCCESS if status_of(review_map) == "ok" else WARNING, review_map.mode


def evidence_links_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED

    top = getattr(args, "top", 5)
    top = 5 if top is None else int(top)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED

    target = str(getattr(args, "target", "") or "").strip()
    include_low = bool(getattr(args, "include_low_confidence", False))
    artifact_path = _evidence_links_artifact_path(args, root)
    can_read_existing = artifact_path.is_file() and not target and not include_low

    payload: object | None
    artifacts: dict[str, str] = {}
    mode = ""
    source = "built from review-map"
    if can_read_existing:
        payload = _read_evidence_links_artifact(artifact_path)
        if payload is None:
            print(f"error: could not read Evidence Links artifact: {artifact_path}")
            return FAILED
        mode = _read_review_map_mode(artifact_path.parent)
        source = f"existing artifact ({_rel_display(str(artifact_path), root)})"
        exit_code = _evidence_links_exit(payload)
    else:
        payload, built_artifacts, exit_code, mode = _build_evidence_links_payload(args, root, top, target, include_low)
        if payload is None:
            return exit_code
        artifacts = built_artifacts or {}
        if bool(getattr(args, "no_write", False)):
            source = "in-memory review-map build (--no-write)"
        elif artifacts:
            source = f"built from review-map; wrote {_rel_display(str(_evidence_links_artifact_path(args, root).parent), root)}"

    if getattr(args, "json", False):
        print(json.dumps(payload, indent=2))
        return exit_code

    text = render_evidence_links_cli(payload, args.repo, top=top, source=source, mode=mode)
    if artifacts and "evidence-links.json" in artifacts:
        text += f"\nArtifacts\n  {artifacts['evidence-links.json']}\n"
    _print_report(text)
    return exit_code


def review_package_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED

    from arkheionx.review_package import build_review_package, build_review_package_result_dict

    strict = bool(getattr(args, "strict", False))
    result = build_review_package(
        root,
        output=(str(getattr(args, "output", "") or "").strip() or None),
        no_write=bool(getattr(args, "no_write", False)),
        strict=strict,
        include_unknown=not bool(getattr(args, "exclude_unknown", False)),
        copy_artifacts=not bool(getattr(args, "no_copy_artifacts", False)),
        export_format=str(getattr(args, "export", "") or "").strip(),
        export_output=(str(getattr(args, "export_output", "") or "").strip() or None),
        include_protocol_model=not bool(getattr(args, "no_protocol_model", False)),
    )
    exit_code = WARNING if (strict and (result.validation_status == "PACKAGE_INVALID" or result.errors)) else SUCCESS

    if getattr(args, "json", False):
        print(json.dumps(build_review_package_result_dict(result), indent=2))
        return exit_code

    lines = [
        "Review Package",
        f"  Repo: {args.repo}",
        f"  Validation status: {result.validation_status}",
        f"  Artifacts: {result.artifact_count}",
        f"  Manual review required: {result.manual_review_required}",
        f"  Ready for submission: {result.ready_for_submission}",
    ]
    if result.no_write:
        lines.append("  Dry run (--no-write): nothing written.")
        if result.export_requested:
            lines.append("  Export requested but skipped in --no-write mode.")
    else:
        lines.append(f"  Package: {result.package_root}")
        lines.append(f"  Manifest: {result.manifest_path}")
        lines.append(f"  Validation: {result.validation_path}")
        lines.append(f"  README: {result.readme_path}")
        if result.checksums_path:
            lines.append(f"  Checksums: {result.checksums_path}")
        if result.export_requested:
            if result.export_written:
                lines.append(f"  Export: {result.export_path} ({result.export_file_count} files)")
            else:
                lines.append(f"  Export blocked: {result.export_status or 'not created'}")
    if result.warnings:
        lines.append(f"  Warnings: {len(result.warnings)}")
    if result.errors:
        lines.append(f"  Errors: {len(result.errors)}")
    lines.append("  Local/static review guidance only. Not an audit; human review required.")
    if result.protocol_model_requested:
        if result.no_write:
            state = "built in memory" if result.protocol_model_id else "not available"
        else:
            state = "included" if result.protocol_model_included else "not available"
        lines.insert(len(lines) - 1, f"  Protocol model: {state}")
        if result.crossref_check_count:
            lines.insert(len(lines) - 1, f"  Cross-reference warnings: {result.crossref_warning_count}")
    _print_report("\n".join(lines))
    return exit_code


def _lv_error(message: str, code: int) -> int:
    """Print a clean local-validate error to stderr (no traceback) and return code."""
    print(f"error: {message}", file=sys.stderr)
    return code


def cmd_local_validate(args: Namespace) -> int:
    """Ingest a saved Foundry output file into local validation artifacts.

    Local/static only: reads a saved file, never runs ``forge``, spawns no
    subprocess, and requires no Foundry install. Manual review is required and
    ``ready_for_submission`` stays false.
    """
    from arkheionx import local_validation as lv

    repo_arg = str(getattr(args, "repo", "") or "")
    root = _resolve_root(repo_arg)
    if root is None:
        return _lv_error(f"not a directory: {repo_arg}", FAILED)

    input_arg = str(getattr(args, "input", "") or "")
    input_path = Path(input_arg).expanduser()
    if not input_path.is_file():
        return _lv_error(f"input file not found: {input_arg}", FAILED)
    try:
        text = input_path.read_text(encoding="utf-8")
    except OSError as exc:
        return _lv_error(f"cannot read input: {exc}", FAILED)

    fmt = str(getattr(args, "format", "auto") or "auto")
    tool = str(getattr(args, "tool", "foundry") or "foundry") or "foundry"
    no_write = bool(getattr(args, "no_write", False))
    try:
        if fmt == "foundry-text":
            parsed = lv.parse_foundry_text_output(text, tool=tool)
        elif fmt == "foundry-json":
            parsed = lv.parse_foundry_json_payload(json.loads(text), tool=tool)
        else:
            parsed = lv.parse_foundry_output(text, tool=tool)
    except json.JSONDecodeError:
        return _lv_error("input is not valid JSON (required by --format foundry-json)", FAILED)
    except ValueError as exc:
        return _lv_error(f"could not parse input: {exc}", FAILED)

    command_list = shlex.split(str(getattr(args, "command", "") or "")) or ["forge", "test", "--json"]
    repo_fp = lv.repo_fingerprint(str(root))
    try:
        build = lv.build_local_validation_from_parsed(parsed, repo_fingerprint=repo_fp, command=command_list)
    except ValueError as exc:
        return _lv_error(f"could not build local validation: {exc}", WARNING)

    write = None
    output_arg = str(getattr(args, "output", "") or "").strip()
    if not no_write:
        output_root = None
        if output_arg:
            candidate = Path(output_arg).expanduser()
            output_root = str(candidate if candidate.is_absolute() else (root / candidate))
        try:
            write = lv.write_local_validation_artifacts(build, repo_path=str(root), output_root=output_root)
        except ValueError as exc:
            return _lv_error(f"could not write artifacts: {exc}", FAILED)
        except OSError as exc:
            return _lv_error(f"write error: {exc}", WARNING)

    try:
        input_display = lv.safe_relative_to_repo(input_path, str(root))
    except ValueError:
        input_display = input_arg

    summary = build.summary
    out = {
        "command": "local-validate",
        "repo_path": repo_arg,
        "input_path": input_display,
        "input_format": parsed.source_format,
        "tool": tool,
        "no_write": no_write,
        "written": write is not None,
        "output_root": write.output_root if write else "",
        "summary_path": write.summary_path if write else "",
        "run_path": write.run_path if write else "",
        "artifacts_index_path": write.artifacts_index_path if write else "",
        "checksums_path": write.checksums_path if write else "",
        "total_tests": summary.total_tests,
        "passed_tests": summary.passed_tests,
        "failed_tests": summary.failed_tests,
        "skipped_tests": summary.skipped_tests,
        "errored_tests": summary.errored_tests,
        "unknown_tests": summary.unknown_tests,
        "validation_status": summary.status,
        "run_id": build.run.run_id,
        "summary_id": summary.summary_id,
        "test_result_count": len(build.test_results),
        "trace_receipt_count": len(build.trace_receipts),
        "artifact_count": int(write.metadata.get("artifact_count", len(write.artifact_ids))) if write else 0,
        "written_file_count": len(write.written_files) if write else 0,
        "manual_review_required": True,
        "ready_for_submission": False,
        "warnings": list(build.warnings),
        "errors": [],
    }

    if bool(getattr(args, "json", False)):
        print(json.dumps(out, indent=2))
        return SUCCESS

    lines = [
        "Local validation complete.",
        f"  Tool: {tool}",
        f"  Input: {input_display} ({parsed.source_format})",
        f"  Tests: {summary.total_tests} total, {summary.passed_tests} passed, "
        f"{summary.failed_tests} failed, {summary.skipped_tests} skipped, {summary.errored_tests} errored",
        f"  Status: {summary.status}",
        f"  Manual review required: {summary.manual_review_required}",
        f"  Ready for submission: {summary.ready_for_submission}",
        f"  Written: {write is not None}",
    ]
    if no_write:
        lines.append("  No-write: True (nothing written).")
    elif write:
        lines.append(f"  Output: {write.output_root}")
    if build.warnings:
        lines.append(f"  Warnings: {len(build.warnings)}")
    lines.append("  Local/static review guidance only. Not an audit; human review required.")
    _print_report("\n".join(lines))
    return SUCCESS


# --------------------------------------------------------------------------
# research memory (v4.1): agent-brief, hypothesis-log, case-study
# --------------------------------------------------------------------------
def _research_top(args: Namespace) -> int:
    top = getattr(args, "top", 10)
    return 10 if top is None else int(top)


def _research_out_dir(args: Namespace, root: Path) -> Path:
    out = str(getattr(args, "out", "") or "").strip()
    return Path(out).expanduser() if out else default_research_dir(root)


def _research_review_map(args: Namespace, root: Path, top: int):
    """Build a review map for a research command, or print an error and return None."""
    sources, test_files = find_solidity_files(root)
    if not sources:
        print(f"Error: no Solidity files found in {args.repo}.")
        print("Next: run inside a Solidity/Foundry repository or try a bundled demo:")
        print("  arkheionx demo --copy lending-vault ./arkheionx-demo")
        print(f"  arkheionx {getattr(args, 'command', 'agent-brief')} ./arkheionx-demo")
        return None, 0, 0
    include_low = bool(getattr(args, "include_low_confidence", False))
    try:
        review_map = build_review_map(root, top=top, include_low_confidence=include_low)
    except ValueError as exc:
        print(f"error: could not resolve `{exc}`. Run `arkheionx review-map {args.repo}` first.")
        return None, 0, 0
    return review_map, len(sources), len(test_files)


def agent_brief_command(args: Namespace) -> int:
    """Generate an AI-agent-ready review brief from the review map (v4.1)."""
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    top = _research_top(args)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED
    review_map, n_sources, n_tests = _research_review_map(args, root, top)
    if review_map is None:
        return FAILED

    data = build_agent_brief_from_review_map(review_map, root, source_files=n_sources, test_files=n_tests)
    exit_code = SUCCESS if status_of(review_map) == "ok" else WARNING

    if getattr(args, "json", False):
        print(json.dumps(data, indent=2))
        return exit_code

    text = render_agent_brief_cli(data, args.repo)
    if not bool(getattr(args, "no_write", False)):
        out_dir = _research_out_dir(args, root)
        try:
            written = write_agent_brief(data, out_dir)
        except OSError as exc:
            print(f"error: could not write artifacts to {out_dir}: {exc}")
            return FAILED
        rel = {name: _rel_display(path, root) for name, path in written.items()}
        text += f"\nArtifacts\n  {rel['agent-brief.md']}\n  {rel['agent-brief.json']}\n"
    _print_report(text)
    return exit_code


def hypothesis_log_command(args: Namespace) -> int:
    """Generate a structured hypothesis log / rejected-finding memory (v4.1)."""
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    top = _research_top(args)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED
    review_map, _n_sources, _n_tests = _research_review_map(args, root, top)
    if review_map is None:
        return FAILED

    data = build_hypothesis_log_from_review_map(review_map, root)
    exit_code = SUCCESS if status_of(review_map) == "ok" else WARNING

    if getattr(args, "json", False):
        print(json.dumps(data, indent=2))
        return exit_code

    text = render_hypothesis_log_cli(data, args.repo, top=top)
    if not bool(getattr(args, "no_write", False)):
        out_dir = _research_out_dir(args, root)
        try:
            written = write_hypothesis_log(data, out_dir)
        except OSError as exc:
            print(f"error: could not write artifacts to {out_dir}: {exc}")
            return FAILED
        rel = {name: _rel_display(path, root) for name, path in written.items()}
        text += f"\nArtifacts\n  {rel['hypotheses.md']}\n  {rel['hypotheses.json']}\n"
    _print_report(text)
    return exit_code


def _load_existing_hypotheses(from_dir: Path) -> list[dict] | None:
    """Load hypotheses (with human-recorded statuses) from a hypotheses.json log."""
    path = from_dir / "hypotheses.json"
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if isinstance(payload, dict) and isinstance(payload.get("hypotheses"), list):
        return payload["hypotheses"]
    return None


def case_study_command(args: Namespace) -> int:
    """Generate a sanitized case-study / research-session report (v4.1)."""
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    top = _research_top(args)
    if top <= 0:
        print("error: --top must be a positive integer.")
        return FAILED
    review_map, _n_sources, _n_tests = _research_review_map(args, root, top)
    if review_map is None:
        return FAILED

    existing: list[dict] | None = None
    from_dir = str(getattr(args, "from_dir", "") or "").strip()
    if from_dir:
        existing = _load_existing_hypotheses(Path(from_dir).expanduser())
        if existing is None:
            print(f"error: could not read hypotheses.json under: {from_dir}")
            print("Next: run `arkheionx hypothesis-log` to create it, or omit --from.")
            return FAILED

    data = build_case_study_from_review_map(review_map, root, existing_hypotheses=existing)
    exit_code = SUCCESS if status_of(review_map) == "ok" else WARNING

    if getattr(args, "json", False):
        print(json.dumps(data, indent=2))
        return exit_code

    from arkheionx.research import render_case_study_md

    text = render_case_study_cli(data, args.repo)
    if not bool(getattr(args, "no_write", False)):
        out = str(getattr(args, "out", "") or "").strip()
        try:
            if out and out.lower().endswith(".md"):
                # Write a single Markdown case study to the chosen file path.
                md_path = Path(out).expanduser()
                md_path.parent.mkdir(parents=True, exist_ok=True)
                md_path.write_text(render_case_study_md(data), encoding="utf-8")
                text += f"\nArtifacts\n  {_rel_display(str(md_path), root)}\n"
            else:
                out_dir = _research_out_dir(args, root)
                written = write_case_study(data, out_dir)
                rel = {name: _rel_display(path, root) for name, path in written.items()}
                text += f"\nArtifacts\n  {rel['case-study.md']}\n  {rel['case-study.json']}\n"
        except OSError as exc:
            print(f"error: could not write case study: {exc}")
            return FAILED
    _print_report(text)
    return exit_code
