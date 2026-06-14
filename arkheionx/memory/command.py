"""CLI command for the root-cause memory brain (Layer 9).

``arkheionx memory {add,list,classify,export}`` over the local file store under
``.arkheionx/memory/``. Local files only. The root-cause hash is semantic (invariant
family + function role + attacker category), so the same root cause on a different
pool dedupes the same. ``export`` redacts the private freeform ``notes`` field.
"""
from __future__ import annotations

import json
from types import SimpleNamespace

from . import duplicate_classifier, root_cause_hash as rch
from .models import MemoryEntry
from .store import MemoryStore

_DEFAULT_DIR = ".arkheionx/memory"
_CATEGORIES = ("findings", "killed", "parked", "out_of_scope")


def _store(args) -> MemoryStore:
    return MemoryStore(getattr(args, "memory_dir", "") or _DEFAULT_DIR)


def _category_for(status: str, explicit: str) -> str:
    if explicit:
        return explicit
    if status == "killed":
        return "killed"
    if status == "parked":
        return "parked"
    if status == "out_of_scope":
        return "out_of_scope"
    return "findings"


def _add(args) -> int:
    store = _store(args)
    role = args.function_role or rch.function_role(args.entry_function or "")
    entry = MemoryEntry(
        target=args.target or "", program=args.program or "", repo=args.repo or "",
        commit=args.commit or "", root_cause=args.root_cause or "",
        invariant_family=args.invariant_family or "", function_role=role,
        attacker_category=rch.attacker_category(args.attacker or ""),
        status=args.status or "unknown", finding_id=args.finding_id or "",
        severity=args.severity or "", notes=args.notes or "",
        do_not_resubmit=bool(args.do_not_resubmit),
    )
    category = _category_for(entry.status, args.category)
    store.add(category, entry, write=not args.no_write)
    if args.json:
        print(json.dumps({"added": entry.to_dict(), "category": category,
                          "memory_dir": str(store.base)}, indent=2))
    else:
        print(f"memory: added [{category}] family={entry.invariant_family or '-'} "
              f"hash={entry.root_cause_hash} status={entry.status} "
              f"do_not_resubmit={entry.do_not_resubmit}")
    return 0


def _list(args) -> int:
    store = _store(args)
    cats = [args.category] if args.category else list(_CATEGORIES)
    rows = [(cat, e) for cat in cats for e in store.load(cat)]
    if args.json:
        print(json.dumps([{"category": c, **e.to_dict()} for c, e in rows], indent=2))
        return 0
    if not rows:
        print("memory: (empty)")
        return 0
    for c, e in rows:
        print(f"[{c}] {e.root_cause_hash or '-'} {e.invariant_family or '-'} "
              f"role={e.function_role or '-'} status={e.status} "
              f"sev={e.severity or '-'} id={e.finding_id or '-'}")
    return 0


def _classify(args) -> int:
    store = _store(args)
    cand = SimpleNamespace(
        invariant_family=args.invariant_family or "",
        entry_function=args.entry_function or "",
        attacker_capability=args.attacker or "",
    )
    known = store.known_hashes()
    verdict = duplicate_classifier.classify_candidate(cand, known)
    comps = rch.components_for_candidate(cand)
    if args.json:
        print(json.dumps({"classification": verdict, **comps,
                          "known_count": len(known)}, indent=2))
    else:
        print(f"memory: {verdict} (hash={comps['root_cause_hash']}, "
              f"family={comps['invariant_family'] or '-'}, "
              f"role={comps['function_role']}, against {len(known)} known)")
    return 0


def _export(args) -> int:
    """Export the shareable semantic fingerprint; redact the private notes field."""
    store = _store(args)
    rows = []
    for e in store.all_entries():
        d = e.to_dict()
        d.pop("notes", None)  # never leak private freeform notes
        rows.append(d)
    print(json.dumps({"schema_version": "v10-memory-export", "entry_count": len(rows),
                      "redacted_fields": ["notes"], "entries": rows}, indent=2))
    return 0


def memory_command(args) -> int:
    sub = getattr(args, "memory_subcommand", None)
    dispatch = {"add": _add, "list": _list, "classify": _classify, "export": _export}
    fn = dispatch.get(sub)
    if fn is None:
        print("usage: arkheionx memory {add,list,classify,export} [...]")
        return 2
    return fn(args)
