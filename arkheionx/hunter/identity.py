"""Universal program-identity / scope-map engine for hunter mode.

Infers *what the target is* from local input only (scope note, addresses, known/audit
corpus, repo contract names). Nothing about any specific company, protocol, chain, or
bounty is hardcoded — the identity is read out of the provided files. The engine also
flags scope collisions (two products, two versions, a chain mismatch, an out-of-scope
address) so a researcher does not waste time on the wrong surface.

Read-only and local: it never fetches a remote bounty page.
"""
from __future__ import annotations

import re

from . import models as M

# Generic platform *categories* (not a specific target). Detecting "this looks like a
# contest vs a continuous bounty" is generic program-structure information.
_PLATFORM_WORDS = (
    "immunefi", "hackerone", "hackenproof", "code4rena", "sherlock", "cantina",
    "hats finance", "hats.finance", "bugcrowd", "remedy", "audit contest",
    "bug bounty",
)
_REPO_RE = re.compile(r"https?://(?:www\.)?(?:github\.com|gitlab\.com|bitbucket\.org)/[^\s)\"']+", re.IGNORECASE)
_URL_RE = re.compile(r"https?://[^\s)\"']+", re.IGNORECASE)
_VERSION_RE = re.compile(r"\b[vV](\d+)(?:\.\d+)*\b")
_SEV_WORDS = ("critical", "high", "medium", "low", "informational")
_POC_MARKERS = ("proof of concept", "proof-of-concept", "poc required", "runnable poc",
                "coded poc", "working poc", "poc is required")
_TRUSTED_WORDS = ("owner", "admin", "governance", "guardian", "operator", "keeper",
                  "timelock", "multisig", "privileged", "trusted role", "trusted-role")
_TESTNET_WORDS = ("testnet", "goerli", "sepolia", "holesky", "rinkeby", "mumbai")


def _section_lines(text: str, header_markers: tuple) -> list:
    """Collect lines that fall under any heading containing a marker word."""
    out: list = []
    active = False
    for raw in text.splitlines():
        line = raw.rstrip()
        low = line.lower()
        if line.lstrip().startswith("#") or re.match(r"^\s*[-*]?\s*\*\*", line):
            active = any(m in low for m in header_markers)
            continue
        if active:
            stripped = line.strip(" \t#-*>").strip()
            if stripped:
                out.append(stripped)
    return out


def _keyword_terms(lines: list) -> list:
    terms: set = set()
    for line in lines:
        for tok in re.findall(r"`([^`]+)`", line):
            terms.add(tok.strip())
        for tok in re.findall(r"\b([A-Z][A-Za-z0-9]{2,})\b", line):
            terms.add(tok)
    return sorted(t for t in terms if len(t) >= 3)[:40]


def _field_after(text: str, label: str) -> str:
    for raw in text.splitlines():
        low = raw.lower()
        if label in low:
            after = raw.split(":", 1)[1].strip() if ":" in raw else ""
            if after:
                return after.strip(" *_`").strip()[:120]
    return ""


def _detect_version_collision(text: str) -> bool:
    """Two or more distinct major versions referenced near product-ish words."""
    majors = {m.group(1) for m in _VERSION_RE.finditer(text)}
    if len(majors) >= 2:
        return True
    # "v1/v2", "version 1 and version 2" style.
    worded = set(re.findall(r"version\s+(\d+)", text.lower()))
    return len(worded) >= 2


def _detect_product_collision(text: str) -> bool:
    """Heuristic: scope mentions two separate programs/products explicitly."""
    low = text.lower()
    signals = 0
    if low.count("bounty program") + low.count("separate program") >= 2:
        signals += 1
    if "two products" in low or "multiple products" in low or "separate products" in low:
        signals += 1
    # Two distinct "Product:" / "Program:" declarations.
    decls = re.findall(r"(?im)^\s*(?:product|program)\s*:\s*(.+)$", text)
    distinct = {d.strip().lower() for d in decls if d.strip()}
    if len(distinct) >= 2:
        signals += 1
    return signals >= 1


def build_program_identity(
    scope_text: str,
    address_parse: M.AddressParseResult,
    contract_names: list,
    corpus: list,
) -> M.ProgramIdentity:
    text = scope_text or ""
    low = text.lower()
    provided = bool(text.strip())

    program_name = _field_after(text, "program") or _field_after(text, "product")
    company = _field_after(text, "company") or _field_after(text, "organization")
    platform = next((w for w in _PLATFORM_WORDS if w in low), "")
    repo_urls = sorted(set(m.group(0).rstrip(".,);") for m in _REPO_RE.finditer(text)))[:10]
    all_urls = [u.rstrip(".,);") for u in _URL_RE.findall(text)]
    bounty_url = next((u for u in all_urls if any(p in u.lower() for p in
                       ("immunefi", "hackerone", "code4rena", "sherlock", "cantina", "bounty", "hats"))), "")
    known_issue_links = sorted(set(u for u in all_urls if any(k in u.lower() for k in
                              ("issues", "findings", "report", "audit"))))[:10]

    in_scope_keywords = _keyword_terms(_section_lines(text, ("in scope", "in-scope", "scope")))
    out_of_scope_keywords = _keyword_terms(_section_lines(text, ("out of scope", "out-of-scope", "exclud", "ineligible")))
    trusted_roles = sorted({w for w in _TRUSTED_WORDS if w in low})
    reward_severities = [s.upper() for s in _SEV_WORDS if s in low]
    poc_required = any(m in low for m in _POC_MARKERS)

    address_dicts = list(address_parse.addresses or [])
    chain_ids = list(address_parse.chain_ids or [])

    contract_families = sorted(set(
        (in_scope_keywords[:0]) + [c for c in (contract_names or []) if c]
    ))[:40]

    warnings: list = []
    notes: list = []

    # --- scope-collision detection (generic, evidence-based) ------------------
    if provided and _detect_version_collision(text):
        warnings.append(M.VERSION_COLLISION_WARNING)
        notes.append("Scope references two or more distinct versions; confirm which version is in scope.")
    if provided and _detect_product_collision(text):
        warnings.append(M.PRODUCT_COLLISION_WARNING)
        notes.append("Scope references more than one product/program; confirm the exact program.")

    # Address vs scope chain mismatch.
    if address_dicts and provided:
        networks = {(a.get("network") or "").lower() for a in address_dicts if a.get("network")}
        testnet_addr = {n for n in networks if n in _TESTNET_WORDS}
        scope_mentions_testnet = any(w in low for w in _TESTNET_WORDS)
        if testnet_addr and not scope_mentions_testnet:
            warnings.append(M.CHAIN_SCOPE_MISMATCH)
            notes.append(f"Addresses include testnet network(s) {sorted(testnet_addr)} not mentioned in scope; "
                         "a testnet address may be mis-treated as mainnet.")
        # Chain ids present in addresses but no chain mentioned anywhere in scope.
        if chain_ids and not re.search(r"\bchain\b|\bmainnet\b|\bnetwork\b", low):
            notes.append("Scope does not state a chain; address chain ids are taken as-is.")

    # Known corpus vs scope mismatch: corpus names a product/contract family that the
    # in-scope keywords never mention (older-version corpus is a classic trap).
    if provided and in_scope_keywords and corpus:
        corpus_text = " ".join(getattr(d, "lower", "") for d in corpus)[:200000]
        if corpus_text and not any(k.lower() in corpus_text for k in in_scope_keywords[:8] if len(k) >= 4):
            warnings.append(M.KNOWN_CORPUS_SCOPE_MISMATCH)
            notes.append("Known/audit corpus does not mention the in-scope contracts; it may be from a "
                         "different product or version.")

    if warnings:
        warnings = sorted(set(warnings))
        warnings.append(M.SCOPE_COLLISION_WARNING)
        warnings = sorted(set(warnings))

    # --- scope status / confidence -------------------------------------------
    if not provided:
        scope_status = M.SCOPE_MISSING
        confidence = M.LOW
        notes.append("No scope file provided; eligibility cannot be confirmed.")
    elif any(w in warnings for w in M.SCOPE_COLLISIONS):
        scope_status = M.SCOPE_COLLISION
        confidence = M.LOW
    else:
        score = 0
        score += 1 if reward_severities else 0
        score += 1 if (in_scope_keywords or contract_families) else 0
        score += 1 if out_of_scope_keywords else 0
        score += 1 if len(text) > 400 else 0
        if score >= 3:
            scope_status, confidence = M.SCOPE_OK, M.HIGH
        elif score >= 1:
            scope_status, confidence = M.SCOPE_PARTIAL, M.MEDIUM
        else:
            scope_status, confidence = M.SCOPE_PARTIAL, M.LOW

    return M.ProgramIdentity(
        program_name=program_name,
        company=company,
        platform=platform,
        bounty_url=bounty_url,
        repo_urls=repo_urls,
        contract_families=contract_families,
        addresses=[a.get("address", "") for a in address_dicts],
        chain_ids=chain_ids,
        in_scope_keywords=in_scope_keywords,
        out_of_scope_keywords=out_of_scope_keywords,
        trusted_roles=trusted_roles,
        known_issue_links=known_issue_links,
        reward_severities=reward_severities,
        poc_required=poc_required,
        scope_status=scope_status,
        scope_confidence=confidence,
        scope_warnings=warnings,
        notes=notes,
    )
