"""CLI handlers for the Foundry-style Arkheionx workbench.

Commands: doctor, open, map, flow, hunt, prove. Output is compact by default;
`--full`/`--show-all`/`--json`/`--mermaid` expand it. Exit codes:
0 = ok (compiler/execution confirmed), 1 = heuristic-only warning, 2 = failure.
"""
from __future__ import annotations

import json
import platform
import shutil
import subprocess
from argparse import Namespace
from pathlib import Path

from arkheionx.artifacts import ArtifactWriter
from arkheionx.cli import exit_codes
from arkheionx.core.safety import LOCAL_ONLY_DISCLAIMER
from arkheionx.flow.mermaid import render_mermaid
from arkheionx.flow.render import render_flow
from arkheionx.hunt.render import render_hunt
from arkheionx.hunt.test_suggestions import suggest_tests
from arkheionx.proof.generator import generate_scaffold, harness_name
from arkheionx.proof.model import ProofArtifact
from arkheionx.protocol import foundry as foundry_mod
from arkheionx.protocol.detector import analyze
from arkheionx.protocol.model import COMPILER_CONFIRMED, HEURISTIC, to_dict
from arkheionx.protocol.render import build_json, foundry_header, render_map, render_open
from arkheionx.protocol.semantic_adapter import find_solidity_files
from arkheionx.rules.registry import list_rule_packs

SUCCESS = exit_codes.SUCCESS          # 0
WARNING = exit_codes.RUNTIME_ERROR    # 1 (heuristic-only / usable warning)
FAILED = exit_codes.INVALID_ARGUMENTS # 2 (cannot complete)


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
    analysis = _run_analysis(args, root)
    if getattr(args, "json", False):
        print(json.dumps(build_json(analysis, {}, [f"arkheionx map {args.repo}"]), indent=2))
        return _exit_for(analysis)
    print(render_open(analysis, args.repo))
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
    print(render_map(analysis, args.repo, artifacts, full=bool(getattr(args, "full", False))))
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
    print(render_flow(analysis, args.repo, artifacts, full=bool(getattr(args, "full", False))))
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
    print(render_hunt(analysis, args.repo, int(getattr(args, "top", 10) or 10), artifacts, full=bool(getattr(args, "full", False))))
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


def prove_command(args: Namespace) -> int:
    root = _resolve_root(args.repo)
    if root is None:
        print(f"error: not a directory: {args.repo}")
        return FAILED
    target = str(getattr(args, "target", "") or "").strip()
    if not target:
        print("error: --target Contract.function is required for prove")
        return FAILED
    analysis = _run_analysis(args, root)

    matches = _resolve_target(analysis.all_functions, target)
    if not matches:
        print(f"error: could not resolve target `{target}`. Run `arkheionx map {args.repo}` or `arkheionx hunt {args.repo}` to list targets.")
        return FAILED
    if len({(m.contract_name, m.function_name) for m in matches}) > 1:
        print(f"Target is ambiguous. Choose one:\n")
        for i, m in enumerate(sorted(matches, key=lambda x: x.contract_name), 1):
            print(f"{i}. {m.display_id}")
        print("\nThen run, for example:")
        first = sorted(matches, key=lambda x: x.contract_name)[0]
        print(f"arkheionx prove {args.repo} --target {first.display_id}")
        return FAILED
    match = matches[0]

    tests, invariants = suggest_tests(match)
    scaffold = generate_scaffold(match.contract_name, match.function_name, tests, invariants)
    harness = harness_name(match.contract_name, match.function_name)
    writer = _writer(args)
    safe = match.display_id.replace(".", "_").replace("/", "_")
    proof = ProofArtifact(
        target_id=match.stable_id or match.display_id,
        status="scaffolded",
        tests_generated=len(tests) + len(invariants),
        evidence_level=HEURISTIC,
        remaining_manual=[
            "Deploy the target contract and mocks in setUp().",
            "Replace each vm.skip(true) with a real arrange/act/assert.",
            "Run forge test to reach EXECUTION_CONFIRMED.",
        ],
    )
    foundry_status = foundry_mod.detect_foundry(root)
    proof.foundry_available = foundry_status.forge_available

    run = bool(getattr(args, "run", False))
    do_build = bool(getattr(args, "build", False)) or run
    if do_build and foundry_status.status == foundry_mod.AVAILABLE_NOT_BUILT:
        status, output = foundry_mod.build_and_confirm(root)
        proof.build_status = status.status
        if status.status == foundry_mod.BUILD_PASSED:
            proof.evidence_level = COMPILER_CONFIRMED
        if not getattr(args, "no_artifacts", False):
            writer.write_text(f"proof/{safe}/foundry-build.txt", output or "(no output)")
    else:
        proof.build_status = "not_attempted" if foundry_status.forge_available else "no_foundry"

    # Honesty: a skip-only scaffold is never EXECUTION_CONFIRMED.
    scaffold_executable = "vm.skip(true)" not in scaffold
    run_note = ""
    if run and not scaffold_executable:
        run_note = "Scaffold contains vm.skip(true)/TODOs; not executed as proof."

    if not getattr(args, "no_artifacts", False):
        proof.files.append(str(writer.write_text(f"proof/{safe}/generated-test.sol", scaffold)))
        proof.files.append(str(writer.write_text(f"proof/{safe}/proof.json", json.dumps(to_dict(proof), indent=2))))

    if getattr(args, "json", False):
        print(json.dumps(to_dict(proof), indent=2))
        return WARNING

    print(f"ARKHEIONX PROVE")
    print(f"Target: {match.qualified_id}")
    print(f"Status: {proof.status}")
    print(f"Mode: {'compiler-confirmed' if proof.evidence_level == COMPILER_CONFIRMED else 'heuristic'}")
    print(f"Foundry: {foundry_header(foundry_status)}")
    print("")
    print("Generated")
    for f in proof.files:
        print(f"  {f}")
    print("")
    print("Proof")
    if run_note:
        print(f"  {run_note}")
    print("  Not executed. Scaffold contains TODOs.")
    print(f"  Evidence level: {proof.evidence_level}")
    print("")
    print("Next")
    print("  Complete the TODOs, then run:")
    print(f"  forge test --match-contract {harness} -vvvv")
    print(f"  or: arkheionx prove {args.repo} --target {match.display_id} --run")
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


def doctor_command(args: Namespace) -> int:
    repo = getattr(args, "repo", ".") or "."
    root = _resolve_root(repo) or Path.cwd()
    foundry_status = foundry_mod.detect_foundry(root, with_version=True)
    try:
        analysis = analyze(root, use_foundry=False, top=10)
        sources, _tests = find_solidity_files(root)
        active = analysis.snapshot.contracts_analyzed
        hidden = sum(analysis.hidden_counts.values())
        usable = True
    except Exception as exc:  # package/parse failure
        print("ARKHEIONX DOCTOR\nStatus: failed\n")
        print(f"error: {exc}")
        return FAILED

    status = "ok" if foundry_status.status in {foundry_mod.AVAILABLE_NOT_BUILT, foundry_mod.BUILD_PASSED} else "warning"
    print("ARKHEIONX DOCTOR")
    print(f"Status: {status}")
    print("")
    print("Core")
    print(f"  Arkheionx: ok {__import__('arkheionx').__version__}")
    print(f"  Python: ok {platform.python_version()}")
    git = _git_info(root)
    if git:
        print(f"  Git: {git}")
    print("")
    print("Foundry")
    print(f"  foundry.toml: {'present' if foundry_status.has_foundry_toml else 'missing'}")
    print(f"  forge: {foundry_status.forge_version or 'missing'}")
    print(f"  status: {foundry_header(foundry_status)}")
    print(f"  mode: {'compiler-capable' if foundry_status.forge_available and foundry_status.has_foundry_toml else 'heuristic only'}")
    print("")
    print("Project")
    print(f"  Solidity files: {len(sources)}")
    print(f"  Active source contracts: {active}")
    print(f"  Hidden by default: {hidden}")
    import os
    print(f"  Artifacts dir writable: {'yes' if os.access(root, os.W_OK) else 'no'}")
    print("")
    print(f"Rule packs: {len(list_rule_packs())}")
    print(LOCAL_ONLY_DISCLAIMER)
    print("")
    print("Next")
    if foundry_status.has_foundry_toml and foundry_status.forge_available:
        print("  Run `arkheionx map .` then `arkheionx hunt .` to start. Use --build for compiler-confirmed results.")
    elif not foundry_status.has_foundry_toml:
        print("  Not a Foundry project here. Run inside a Foundry project for compiler-confirmed results.")
    else:
        print("  Install Foundry (forge) for compiler-confirmed results.")
    return SUCCESS
