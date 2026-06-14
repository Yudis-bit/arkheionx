"""War-run orchestrator (Layer 10) — ties every layer together.

Pipeline: scope -> semantic map -> DeFi entities -> state transitions ->
invariants -> attack candidates -> memory/dedup -> economic severity gate ->
ranking -> PoC skeletons -> fork plan -> artifacts.

Local/static. No RPC by default. No report. Fork support is a plan only.
"""
from __future__ import annotations

from pathlib import Path

from arkheionx.semantic import build_semantic_map
from arkheionx.semantic import renderer as sem_render
from arkheionx.defi import build_defi_entities
from arkheionx.defi import renderer as defi_render
from arkheionx.state import build_transitions
from arkheionx.state import renderer as state_render
from arkheionx.invariants import build_invariants
from arkheionx.invariants import renderer as inv_render
from arkheionx.attack import build_candidates, ranking
from arkheionx.attack import graph as attack_graph
from arkheionx.attack import renderer as attack_render
from arkheionx.pocgen import build_skeletons
from arkheionx.pocgen import renderer as poc_render
from arkheionx.severity import apply_gate
from arkheionx.severity import renderer as sev_render
from arkheionx.forklab import build_fork_plan
from arkheionx.forklab import renderer as fork_render
from arkheionx.forklab import secret_redaction
from arkheionx.memory import MemoryStore, duplicate_classifier
from arkheionx.memory import renderer as mem_render

from . import renderer as war_render
from .scope import load_scope

# Forbidden outcome terms (mirror the hunter guard; never overclaim).
_FORBIDDEN = ("VALID_BUG", "CONFIRMED_VULNERABILITY", "SUBMIT_NOW", "GUARANTEED_HIGH",
              "GUARANTEED_CRITICAL", "EXPLOIT_READY", "AUTO_SUBMITTED")


class WarRunError(Exception):
    pass


def default_out_dir(target: Path) -> Path:
    return Path(target) / ".arkheionx" / "war-run"


def _guard(texts):
    blob = "\n".join(texts)
    for term in _FORBIDDEN:
        if term in blob:
            raise WarRunError(f"war-run guard: forbidden outcome term emitted: {term}")
    warnings = secret_redaction.scan(blob)
    return warnings


def run_war_run(target, *, scope_file=None, out_dir=None, max_candidates=10,
                gen_poc=True, allow_fork_plan=True, memory_dir=None,
                write=True, asset_decimals=0):
    target = Path(target).expanduser()
    if not target.exists():
        raise WarRunError(f"target not found: {target}")
    out = Path(out_dir).expanduser() if out_dir else default_out_dir(target)

    scope = load_scope(scope_file)

    # 1-5: semantic -> entities -> transitions -> invariants
    smap = build_semantic_map(target, include_paths=scope.in_scope_paths or None)
    emap = build_defi_entities(smap)
    tmap = build_transitions(smap, emap)
    invset = build_invariants(smap, emap, tmap)

    # 6: attack candidates
    graph = build_candidates(smap, emap, tmap, invset)

    # 7: memory / dedup (before gate so duplicates can be killed)
    store = MemoryStore(memory_dir) if memory_dir else None
    if store is not None or scope.present:
        duplicate_classifier.annotate(graph, store, scope.as_context() if scope.present else None)

    # 8: economic severity gate
    context = {"asset_decimals": asset_decimals} if asset_decimals else {}
    verdicts = apply_gate(graph, scope=scope.as_context() if scope.present else None,
                          context=context)

    # 9: rank (after gate, so severity informs ranking), then truncate
    ranking.rank(graph)
    if max_candidates and len(graph.candidates) > max_candidates:
        graph.candidates = graph.candidates[:max_candidates]
    verdicts = [v for v in verdicts if v.candidate_id in {c.id for c in graph.candidates}]

    # 10: PoC skeletons for top candidates
    skeletons = build_skeletons(graph, smap, top_n=min(5, max_candidates)) if gen_poc else []

    # 11: fork plan when needed
    fork_reqs = build_fork_plan(graph, smap, scope.as_context() if scope.present else None) \
        if allow_fork_plan else []

    # --- assemble artifacts ------------------------------------------------
    contents = {}   # name -> text
    jsons = {}      # name -> dict
    contents["01-scope-map.md"] = war_render.scope_map_md(scope, smap)
    jsons["02-semantic-map.json"] = sem_render.semantic_map_json(smap)
    contents["02-semantic-map.md"] = sem_render.semantic_summary_md(smap)
    jsons["03-call-graph.json"] = sem_render.call_graph_json(smap)
    jsons["04-storage-access-map.json"] = sem_render.storage_access_json(smap)
    jsons["05-defi-entities.json"] = defi_render.entities_json(emap)
    contents["05-defi-entities.md"] = defi_render.entities_md(emap)
    jsons["06-state-transitions.json"] = state_render.transitions_json(tmap)
    contents["06-state-transitions.md"] = state_render.transitions_md(tmap)
    contents["07-invariants.md"] = inv_render.invariants_md(invset)
    jsons["08-invariants.json"] = inv_render.invariants_json(invset)
    jsons["09-attack-graph.json"] = attack_graph.attack_graph_json(graph)
    contents["09-attack-graph.md"] = attack_graph.attack_graph_md(graph)
    contents["10-candidate-ranking.md"] = attack_render.candidate_ranking_md(graph)
    contents["12-fork-plan.md"] = fork_render.fork_plan_md(fork_reqs)
    jsons["fork-requirements.json"] = fork_render.fork_requirements_json(fork_reqs)
    contents["13-economic-severity.md"] = sev_render.severity_md(verdicts)
    jsons["economic-severity.json"] = sev_render.severity_json(verdicts)
    contents["14-dedup-scope-risk.md"] = mem_render.dedup_scope_md(graph)

    poc_files = poc_render.skeleton_files(skeletons)
    poc_readme = poc_render.skeletons_readme(skeletons)

    artifact_paths = (list(contents.keys()) + list(jsons.keys())
                      + [f"11-poc-skeletons/{n}" for n in poc_files]
                      + ["11-poc-skeletons/README.md", "triage.json", "manifest.json"])

    counts = {
        "entities": len(emap.entities), "transitions": len(tmap.transitions),
        "invariants": len(invset.invariants), "suspicious_invariants": len(invset.suspicious()),
        "candidates": len(graph.candidates), "skeletons": len(skeletons),
        "fork_required": len(fork_reqs),
    }
    triage = war_render.triage_json(str(target), scope, smap, emap, tmap, invset, graph,
                                    verdicts, fork_reqs, artifact_paths)
    manifest = war_render.manifest_json(str(target), artifact_paths, counts)

    # safety guard + secret scan over everything we will write
    import json as _json
    all_text = list(contents.values()) + [poc_readme] + list(poc_files.values()) \
        + [_json.dumps(j) for j in jsons.values()] + [_json.dumps(triage), _json.dumps(manifest)]
    secret_warnings = _guard(all_text)
    if secret_warnings:
        manifest["secret_warnings"] = secret_warnings
        triage["secret_warnings"] = secret_warnings

    written = {}
    if write:
        out.mkdir(parents=True, exist_ok=True)
        for name, text in contents.items():
            (out / name).write_text(text, encoding="utf-8")
            written[name] = str(out / name)
        for name, payload in jsons.items():
            (out / name).write_text(_json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            written[name] = str(out / name)
        poc_dir = out / "11-poc-skeletons"
        poc_dir.mkdir(parents=True, exist_ok=True)
        for name, text in poc_files.items():
            (poc_dir / name).write_text(text, encoding="utf-8")
        (poc_dir / "README.md").write_text(poc_readme, encoding="utf-8")
        (out / "triage.json").write_text(_json.dumps(triage, indent=2) + "\n", encoding="utf-8")
        (out / "manifest.json").write_text(_json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    console = war_render.console_lines(str(target), smap, emap, tmap, invset, graph,
                                       str(out), write)

    return {
        "out_dir": str(out), "contents": contents, "jsons": jsons,
        "poc_files": poc_files, "poc_readme": poc_readme,
        "triage": triage, "manifest": manifest, "counts": counts,
        "console": console, "artifact_paths": artifact_paths, "written": written,
        "smap": smap, "emap": emap, "tmap": tmap, "invset": invset, "graph": graph,
        "verdicts": verdicts, "fork_reqs": fork_reqs, "skeletons": skeletons, "scope": scope,
    }
