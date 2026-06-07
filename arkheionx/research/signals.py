"""Static signal detection for the v4.1 research surface engine.

Local/static only. No compiler, RPC, Foundry, or network. These helpers scan
Solidity source text for review-relevant signals (authorization, periphery/core
interaction, behavior-mismatch) and attribute each match to an enclosing
function with an honest ``file:line`` reference.

Every signal is a *review prompt*, never a finding. All test suggestions are
local-test directions, never live steps.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# --- Match modes ----------------------------------------------------------
WORD = "word"     # match a standalone identifier token (case-insensitive)
SUBSTR = "substr"  # match a substring anywhere on the line (case-insensitive)

_IDENT_RE = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_STRING_RE = re.compile(r'"([^"\\]*(?:\\.[^"\\]*)*)"')
_LOOP_RE = re.compile(r"\b(?:for|while)\b\s*\(")
_TRY_RE = re.compile(r"\btry\b")
_CATCH_RE = re.compile(r"\bcatch\b")
_LOWLEVEL_RE = re.compile(r"\.(?:call|delegatecall|staticcall)\s*[\({]")
_MEMBER_CALL_RE = re.compile(r"\b([A-Za-z_][A-Za-z0-9_]*)\s*\.\s*([A-Za-z_][A-Za-z0-9_]*)\s*\(")
_REQUIRE_RE = re.compile(r"\brequire\s*\(")

# Value/token primitives that are not, by themselves, a periphery/core call.
_VALUE_PRIMITIVE_METHODS = {
    "transfer", "transferfrom", "approve", "balanceof", "allowance",
    "mint", "burn", "safetransfer", "safetransferfrom", "deposit", "withdraw",
}
# Receiver identifiers that denote a token/value handle rather than a core peer.
_VALUE_PRIMITIVE_RECEIVERS = {"asset", "token", "weth", "erc20", "ierc20"}


@dataclass(frozen=True)
class SignalSpec:
    """One detectable signal: how to match it and why a reviewer cares."""

    name: str
    kind: str
    patterns: tuple[str, ...]
    mode: str
    why: str
    tests: tuple[str, ...] = field(default_factory=tuple)


# --- Authorization signal specs (Phase 5) ---------------------------------
# Generic detection only. Never hardcoded to any specific protocol.
AUTH_SIGNAL_SPECS: tuple[SignalSpec, ...] = (
    SignalSpec(
        "ecrecover", "signature", ("ecrecover",), SUBSTR,
        "Raw signature recovery. Confirm the recovered signer is the expected "
        "party and is bound to the message, nonce, and domain.",
        ("wrong signer is rejected", "a zero-address recovery is rejected",
         "the same signature cannot authorize a different message"),
    ),
    SignalSpec(
        "ECDSA", "signature", ("ecdsa",), SUBSTR,
        "ECDSA signature verification. Confirm signer binding and malleability "
        "handling for the recovered signer.",
        ("wrong signer is rejected", "a tampered signature is rejected"),
    ),
    SignalSpec(
        "EIP712", "domain", ("eip712", "hashtypeddata", "domainseparator", "verifyingcontract"), SUBSTR,
        "EIP-712 typed-data authorization. Confirm the domain (chain id, "
        "verifying contract, name/version) is bound into the signed digest.",
        ("a signature for a different domain is rejected",
         "a signature for a different verifying contract is rejected",
         "a signature for a different chain id is rejected"),
    ),
    SignalSpec(
        "chainid", "domain", ("chainid",), WORD,
        "Chain-id binding. Confirm a signature cannot be replayed across chains.",
        ("a signature for a different chain id is rejected",),
    ),
    SignalSpec(
        "nonce", "replay", ("nonce",), WORD,
        "Nonce-based replay protection. Confirm a used nonce cannot be reused.",
        ("replay with a used nonce is rejected",
         "nonce increments exactly once per authorized action"),
    ),
    SignalSpec(
        "deadline", "replay", ("deadline",), WORD,
        "Deadline / expiry check. Confirm an expired authorization is rejected.",
        ("an expired deadline is rejected", "a boundary deadline behaves as documented"),
    ),
    SignalSpec(
        "permit", "signature", ("permit",), WORD,
        "Permit-style signed approval. Confirm the approval is bound to the "
        "intended spender, amount, nonce, and deadline.",
        ("a permit cannot be replayed", "a permit for a different spender is rejected"),
    ),
    SignalSpec(
        "signature", "signature", ("signature", "signer", "digest"), WORD,
        "Signature authorization surface. Confirm the signed payload binds the "
        "signer to the exact action being authorized.",
        ("a signature for a different action/order is rejected",
         "wrong signer is rejected"),
    ),
    SignalSpec(
        "MerkleProof", "merkle", ("merkleproof",), SUBSTR,
        "Merkle proof verification. Confirm the leaf encodes every field needed "
        "to bind the proof to the intended claim and root.",
        ("a proof for a different leaf is rejected",
         "a proof against a different root is rejected",
         "a malformed / wrong-length proof is rejected"),
    ),
    SignalSpec(
        "merkle-root", "merkle", ("root", "leaf"), WORD,
        "Merkle root/leaf binding. Confirm the leaf binds all claim fields and "
        "the root is the one in force.",
        ("a leaf missing a bound field is rejected",
         "a proof against a stale root is rejected"),
    ),
    SignalSpec(
        "proof", "merkle", ("proof",), WORD,
        "Proof input. Confirm proof shape/length is validated and bound to the "
        "intended leaf and root.",
        ("a malformed / wrong-length proof is rejected",),
    ),
    SignalSpec(
        "ratifier", "access-control", ("ratifier", "gate"), WORD,
        "Ratifier / gate authorization. Confirm only an intended caller passes "
        "the gate and the gate cannot be bypassed via an alternate path.",
        ("an un-gated caller is rejected", "an alternate entry path is also gated"),
    ),
    SignalSpec(
        "authorization", "access-control", ("authorization", "isauthorized", "setauthorization"), SUBSTR,
        "Explicit authorization mapping. Confirm authorization is bound to the "
        "intended (operator, account) pair and cannot be set by the wrong party.",
        ("an unauthorized operator is rejected",
         "authorization for one account does not apply to another"),
    ),
    SignalSpec(
        "delegate", "access-control", ("delegate",), WORD,
        "Delegation. Confirm a delegate's powers are scoped and revocable.",
        ("a revoked delegate is rejected", "a delegate cannot exceed scope"),
    ),
    SignalSpec(
        "role", "access-control", ("role", "onlyrole", "accesscontrol", "hasrole", "grantrole"), SUBSTR,
        "Role-based access control. Confirm each role-gated function rejects "
        "callers without the role and role admin is bounded.",
        ("a caller without the role is rejected",
         "role admin cannot be escalated by an unprivileged caller"),
    ),
    SignalSpec(
        "ownable", "access-control", ("ownable", "onlyowner"), SUBSTR,
        "Owner-gated control surface. Confirm owner-only functions reject "
        "non-owners and ownership transfer is bounded.",
        ("a non-owner caller is rejected",
         "ownership transfer cannot be hijacked"),
    ),
)

# --- Periphery / core signal specs (Phase 6) ------------------------------
PERIPHERY_KEYWORD_SPECS: tuple[SignalSpec, ...] = (
    SignalSpec("router", "periphery", ("router",), SUBSTR,
               "Router-style periphery. Confirm routed calls match direct-call accounting.", ()),
    SignalSpec("bundle", "periphery", ("bundle", "bundler"), SUBSTR,
               "Bundle periphery. Confirm a malformed or failing item does not corrupt the batch.", ()),
    SignalSpec("multicall", "periphery", ("multicall",), SUBSTR,
               "Multicall periphery. Confirm per-call accounting and failure handling.", ()),
    SignalSpec("zap", "periphery", ("zap",), WORD,
               "Zap periphery. Confirm composed steps match direct-call accounting.", ()),
    SignalSpec("periphery", "periphery", ("periphery",), SUBSTR,
               "Declared periphery. Confirm periphery calls match direct core calls.", ()),
    SignalSpec("adapter", "periphery", ("adapter",), SUBSTR,
               "Adapter. Confirm the adapter preserves core accounting and trust.", ()),
    SignalSpec("callback", "callback", ("callback", "oncallback"), SUBSTR,
               "Callback surface. Confirm callback caller/state assumptions hold.", ()),
    SignalSpec("hook", "callback", ("hook",), WORD,
               "Hook surface. Confirm hook ordering and reentrancy assumptions.", ()),
    SignalSpec("erc-callback", "callback", ("onerc721received", "onerc1155received", "onerc"), SUBSTR,
               "Token-receiver callback. Confirm reentrancy and caller assumptions.", ()),
    SignalSpec("executor", "periphery", ("executor", "execute"), SUBSTR,
               "Executor surface. Confirm executed operations match direct calls.", ()),
    SignalSpec("manager", "periphery", ("manager",), SUBSTR,
               "Manager facade. Confirm managed calls match direct core accounting.", ()),
    SignalSpec("facade", "periphery", ("facade",), SUBSTR,
               "Facade. Confirm facade calls match direct core accounting.", ()),
    SignalSpec("batch", "periphery", ("batch",), WORD,
               "Batch surface. Confirm a failing item does not corrupt the batch.", ()),
)

# --- Behavior-mismatch comment/string words (Phase 7) ---------------------
BEHAVIOR_WORD_SPECS: tuple[SignalSpec, ...] = (
    SignalSpec("skip", "partial-failure", ("skip",), WORD,
               "Documented skip behavior. Confirm the skip path is actually reached "
               "before any earlier revert.",
               ("a malformed item is skipped (not reverted) if that is the documented behavior",)),
    SignalSpec("ignore", "partial-failure", ("ignore",), WORD,
               "Documented ignore behavior. Confirm ignored conditions cannot be reached "
               "via an earlier revert.", ()),
    SignalSpec("continue", "partial-failure", ("continue",), WORD,
               "Continue-on-error behavior. Confirm the loop continues as documented.", ()),
    SignalSpec("best-effort", "partial-failure", ("best effort", "best-effort"), SUBSTR,
               "Best-effort behavior. Confirm partial success matches documentation.", ()),
    SignalSpec("partial", "partial-failure", ("partial",), WORD,
               "Partial-execution behavior. Confirm partial results are accounted correctly.", ()),
    SignalSpec("optional", "partial-failure", ("optional",), WORD,
               "Optional-step behavior. Confirm an omitted optional step is handled.", ()),
    SignalSpec("fallback", "fallback", ("fallback",), WORD,
               "Fallback path. Confirm the fallback cannot be reached unintentionally.", ()),
    SignalSpec("recover", "fallback", ("recover", "tolerate"), WORD,
               "Recovery/tolerance behavior. Confirm recovery matches documentation.", ()),
    SignalSpec("malformed", "input", ("malformed",), WORD,
               "Documented malformed-input handling. Confirm malformed input reaches the "
               "documented handler rather than an earlier revert.",
               ("a malformed input is handled as documented, not reverted earlier",)),
    SignalSpec("invalid", "input", ("invalid",), WORD,
               "Documented invalid-input handling. Confirm invalid input is handled as documented.", ()),
    SignalSpec("revert", "revert-behavior", ("revert", "reverting", "reverts"), WORD,
               "Documented revert behavior. Confirm the actual revert point matches the "
               "documented one (no earlier revert before a documented skip/handler).",
               ("the revert happens exactly where documented",)),
)


def identifier_tokens(line: str) -> set[str]:
    """Lowercased identifier tokens on a line (for WORD-mode matching)."""
    return {tok.lower() for tok in _IDENT_RE.findall(line)}


def _line_matches(line: str, tokens: set[str], spec: SignalSpec) -> bool:
    low = line.lower()
    if spec.mode == WORD:
        return any(p in tokens for p in spec.patterns)
    return any(p in low for p in spec.patterns)


def comment_string_text(lines: list[str]) -> list[str]:
    """For each line, the concatenated comment + string-literal text.

    Tracks ``/* ... */`` block state across lines. Used so behavior-mismatch
    word signals fire on documentation/strings, not arbitrary code tokens.
    """
    result: list[str] = []
    in_block = False
    for raw in lines:
        parts: list[str] = []
        s = raw
        while s:
            if in_block:
                end = s.find("*/")
                if end == -1:
                    parts.append(s)
                    s = ""
                else:
                    parts.append(s[:end])
                    s = s[end + 2:]
                    in_block = False
                continue
            start_block = s.find("/*")
            line_comment = s.find("//")
            if start_block != -1 and (line_comment == -1 or start_block < line_comment):
                parts.extend(_STRING_RE.findall(s[:start_block]))
                s = s[start_block + 2:]
                in_block = True
            elif line_comment != -1:
                parts.extend(_STRING_RE.findall(s[:line_comment]))
                parts.append(s[line_comment + 2:])
                s = ""
            else:
                parts.extend(_STRING_RE.findall(s))
                s = ""
        result.append(" ".join(p for p in parts if p.strip()))
    return result


def strip_comments_strings(lines: list[str]) -> list[str]:
    """For each line, the code text with comments and string contents removed.

    The complement of :func:`comment_string_text`. Used so authorization and
    code-pattern signals fire on actual code, not on prose in doc comments or
    on words inside string literals. Tracks ``/* ... */`` block state.
    """
    out: list[str] = []
    in_block = False
    for raw in lines:
        s = raw
        buf: list[str] = []
        while s:
            if in_block:
                end = s.find("*/")
                if end == -1:
                    s = ""
                else:
                    s = s[end + 2:]
                    in_block = False
                continue
            candidates: list[tuple[int, str]] = []
            for pos, kind in ((s.find("/*"), "block"), (s.find("//"), "line"), (s.find('"'), "str")):
                if pos != -1:
                    candidates.append((pos, kind))
            if not candidates:
                buf.append(s)
                s = ""
                continue
            pos, kind = min(candidates, key=lambda x: x[0])
            buf.append(s[:pos])
            if kind == "line":
                s = ""
            elif kind == "block":
                s = s[pos + 2:]
                in_block = True
            else:
                match = _STRING_RE.match(s, pos)
                s = s[match.end():] if match else ""
        out.append("".join(buf))
    return out


@dataclass
class FunctionSpan:
    """A function's [start, end) line span within one source file."""

    display_id: str
    contract: str
    name: str
    start: int
    end: int


_COMMENT_PREFIXES = ("///", "//", "/*", "*", "*/")


def _absorb_comment_block(start: int, lower_bound: int, lines: list[str]) -> int:
    """Move a function's start up to include the doc-comment block directly above it.

    A doc comment immediately preceding a function belongs to that function, not
    the previous one. Absorbs only contiguous comment lines (no blank gap), and
    never crosses ``lower_bound`` (the previous function's declaration line).
    """
    absorbed = start
    j = start - 1  # 1-based line directly above the declaration
    while j > lower_bound and 1 <= j <= len(lines):
        text = lines[j - 1].strip()
        if text.startswith(_COMMENT_PREFIXES) or text.endswith("*/"):
            absorbed = j
            j -= 1
        else:
            break
    return absorbed


def function_spans(functions: list, file_path: str, lines: list[str] | None = None) -> list[FunctionSpan]:
    """Build line spans for functions declared in ``file_path``.

    ``functions`` are review-map FunctionSurface objects. Each carries a 1-based
    start ``line``; a function's span ends where the next function (by start
    line) begins. When ``lines`` is provided, a function's span start absorbs the
    contiguous doc-comment block directly above its declaration. Functions with
    an unknown line (0) are skipped.
    """
    here = [f for f in functions if f.path == file_path and f.line > 0]
    here.sort(key=lambda f: f.line)
    starts: list[int] = []
    for idx, fs in enumerate(here):
        prev_decl = here[idx - 1].line if idx > 0 else 0
        start = _absorb_comment_block(fs.line, prev_decl, lines) if lines else fs.line
        starts.append(start)
    spans: list[FunctionSpan] = []
    for idx, fs in enumerate(here):
        end = starts[idx + 1] if idx + 1 < len(here) else 10 ** 9
        spans.append(FunctionSpan(fs.display_id, fs.contract, fs.name, starts[idx], end))
    return spans


def function_at_line(spans: list[FunctionSpan], line_no: int) -> FunctionSpan | None:
    """The function whose span contains ``line_no`` (1-based), or None."""
    chosen: FunctionSpan | None = None
    for span in spans:
        if span.start <= line_no < span.end:
            chosen = span
    return chosen


@dataclass
class Match:
    """One signal hit with an honest source reference and function attribution."""

    signal: str
    kind: str
    line: int
    contract: str
    function: str
    why: str
    tests: tuple[str, ...]


def scan_auth(lines: list[str], spans: list[FunctionSpan], default_contract: str) -> list[Match]:
    """Detect authorization signals in code (comments/strings stripped)."""
    code = strip_comments_strings(lines)
    matches: list[Match] = []
    for idx, line in enumerate(code, 1):
        if not line.strip():
            continue
        tokens = identifier_tokens(line)
        for spec in AUTH_SIGNAL_SPECS:
            if _line_matches(line, tokens, spec):
                span = function_at_line(spans, idx)
                matches.append(Match(
                    spec.name, spec.kind, idx,
                    span.contract if span else default_contract,
                    span.name if span else "",
                    spec.why, spec.tests,
                ))
    return matches


def scan_behavior(lines: list[str], spans: list[FunctionSpan], default_contract: str) -> list[Match]:
    """Detect behavior-mismatch signals in comments/strings + code patterns."""
    cs_text = comment_string_text(lines)
    matches: list[Match] = []
    for idx, line in enumerate(lines, 1):
        doc = cs_text[idx - 1]
        if doc:
            tokens = identifier_tokens(doc)
            for spec in BEHAVIOR_WORD_SPECS:
                if _line_matches(doc, tokens, spec):
                    span = function_at_line(spans, idx)
                    matches.append(Match(
                        spec.name, spec.kind, idx,
                        span.contract if span else default_contract,
                        span.name if span else "",
                        spec.why, spec.tests,
                    ))
    return matches


@dataclass
class FunctionCode:
    """Code-pattern booleans computed over a function's body span."""

    has_try_catch: bool = False
    has_low_level_call: bool = False
    has_loop: bool = False
    has_require: bool = False
    has_require_in_loop: bool = False
    cross_contract_calls: tuple[str, ...] = field(default_factory=tuple)


def analyze_function_code(lines: list[str], span: FunctionSpan) -> FunctionCode:
    """Compute periphery/behavior code-pattern booleans for one function body.

    Comments and string literals are stripped first, so doc text that mentions
    ``try/catch`` or a member call does not produce a false code signal.
    """
    code = strip_comments_strings(lines)
    body = code[max(0, span.start - 1): min(len(code), span.end - 1)]
    text = "\n".join(body)
    has_try = bool(_TRY_RE.search(text)) and bool(_CATCH_RE.search(text))
    has_low = bool(_LOWLEVEL_RE.search(text))
    has_loop = bool(_LOOP_RE.search(text))
    has_require = bool(_REQUIRE_RE.search(text))
    targets: list[str] = []
    for recv, method in _MEMBER_CALL_RE.findall(text):
        if method.lower() in _VALUE_PRIMITIVE_METHODS:
            continue
        if recv.lower() in _VALUE_PRIMITIVE_RECEIVERS:
            continue
        if recv.lower() in {"this", "super", "abi", "address", "msg", "block", "tx", "type", "string", "bytes"}:
            continue
        targets.append(recv)
    # Require-in-loop: a require appears in a body that also loops (heuristic).
    has_require_in_loop = has_loop and has_require
    return FunctionCode(
        has_try_catch=has_try,
        has_low_level_call=has_low,
        has_loop=has_loop,
        has_require=has_require,
        has_require_in_loop=has_require_in_loop,
        cross_contract_calls=tuple(sorted(set(targets))),
    )
