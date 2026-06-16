"""Reachability Truth Engine for Arkheionx hunter mode (V9.1).

Answers a sharper question than "is this function external?":

    Who can call this function successfully?

Function *visibility* is not *reachability*. A public/external function can be
unreachable to an attacker because of a modifier gate, an inline ``msg.sender`` check,
a helper auth function, an AccessControl role, an inline-assembly ``sload`` role
getter, an authority contract, an allowlist mapping, or a proxy/initializer context.

This module separates three layers — visibility, gate evidence, and a final
reachability label — and is deliberately *conservative*: a public/external function
with an unresolved custom gate is **never** labeled ``UNPRIVILEGED_EXTERNAL``. Unknown
stays unknown.

Deterministic and safe: Python regex + balanced-brace scanning only. No compiler, no
Slither, no subprocess, no network, no randomness, no LLM. Heuristic and
line-preserving; a reachability label is a research lens, not a finding.

Nothing here is target-specific: no company, protocol, chain, repo, bounty, or
modifier name of any specific project is hardcoded. The role vocabulary is the generic
DeFi access-control vocabulary (owner/admin/oracle/operator/...).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

# ===========================================================================
# Confidence ladder
# ===========================================================================
HIGH = "HIGH"
MEDIUM = "MEDIUM"
LOW = "LOW"
UNKNOWN = "UNKNOWN"

# ===========================================================================
# Reachability labels (stable strings used in JSON + markdown)
# ===========================================================================
# Attacker-reachable.
UNPRIVILEGED_EXTERNAL = "UNPRIVILEGED_EXTERNAL"
UNPRIVILEGED_PUBLIC = "UNPRIVILEGED_PUBLIC"
FALLBACK_RECEIVE_UNPRIVILEGED = "FALLBACK_RECEIVE_UNPRIVILEGED"

# Trusted-role / owner / admin gated.
OWNER_GATED_EXTERNAL = "OWNER_GATED_EXTERNAL"
ADMIN_GATED_EXTERNAL = "ADMIN_GATED_EXTERNAL"
ORACLE_GATED_EXTERNAL = "ORACLE_GATED_EXTERNAL"
OPERATOR_GATED_EXTERNAL = "OPERATOR_GATED_EXTERNAL"
MINTER_GATED_EXTERNAL = "MINTER_GATED_EXTERNAL"
BURNER_GATED_EXTERNAL = "BURNER_GATED_EXTERNAL"
PAUSER_GATED_EXTERNAL = "PAUSER_GATED_EXTERNAL"
KEEPER_GATED_EXTERNAL = "KEEPER_GATED_EXTERNAL"
GUARDIAN_GATED_EXTERNAL = "GUARDIAN_GATED_EXTERNAL"
CONTROLLER_GATED_EXTERNAL = "CONTROLLER_GATED_EXTERNAL"
MANAGER_GATED_EXTERNAL = "MANAGER_GATED_EXTERNAL"
GOVERNANCE_GATED_EXTERNAL = "GOVERNANCE_GATED_EXTERNAL"
TREASURY_GATED_EXTERNAL = "TREASURY_GATED_EXTERNAL"
FEE_RECIPIENT_GATED_EXTERNAL = "FEE_RECIPIENT_GATED_EXTERNAL"
AUTHORITY_GATED_EXTERNAL = "AUTHORITY_GATED_EXTERNAL"
ACCESS_CONTROL_GATED_EXTERNAL = "ACCESS_CONTROL_GATED_EXTERNAL"
ROLE_GATED_EXTERNAL = "ROLE_GATED_EXTERNAL"
PROBABLY_ROLE_GATED_EXTERNAL = "PROBABLY_ROLE_GATED_EXTERNAL"
ALLOWLIST_GATED_EXTERNAL = "ALLOWLIST_GATED_EXTERNAL"
SENDER_WHITELIST_GATED_EXTERNAL = "SENDER_WHITELIST_GATED_EXTERNAL"

# Context gated.
PROXY_CONTEXT_EXTERNAL = "PROXY_CONTEXT_EXTERNAL"
INITIALIZER_CONTEXT_EXTERNAL = "INITIALIZER_CONTEXT_EXTERNAL"

# Unknown / unresolved.
UNKNOWN_MODIFIER_GATED_EXTERNAL = "UNKNOWN_MODIFIER_GATED_EXTERNAL"
UNKNOWN_AUTH_HELPER_GATED_EXTERNAL = "UNKNOWN_AUTH_HELPER_GATED_EXTERNAL"
UNKNOWN_REACHABILITY = "UNKNOWN_REACHABILITY"

# Internal / private / constructor.
INTERNAL_ONLY = "INTERNAL_ONLY"
PRIVATE_ONLY = "PRIVATE_ONLY"
CONSTRUCTOR_ONLY = "CONSTRUCTOR_ONLY"

# No value effect.
VIEW_ONLY_NO_VALUE_EFFECT = "VIEW_ONLY_NO_VALUE_EFFECT"
PURE_ONLY_NO_VALUE_EFFECT = "PURE_ONLY_NO_VALUE_EFFECT"

# ===========================================================================
# Decision classes (how a label feeds the decision policy)
# ===========================================================================
DC_ATTACKER_REACHABLE = "ATTACKER_REACHABLE"
DC_TRUSTED_ROLE_GATED = "TRUSTED_ROLE_GATED"
DC_UNKNOWN_GATED = "UNKNOWN_GATED"
DC_CONTEXT_GATED = "CONTEXT_GATED"
DC_NO_VALUE_EFFECT = "NO_VALUE_EFFECT"
DC_INTERNAL = "INTERNAL"

ATTACKER_REACHABLE_LABELS = frozenset({
    UNPRIVILEGED_EXTERNAL, UNPRIVILEGED_PUBLIC, FALLBACK_RECEIVE_UNPRIVILEGED,
})
TRUSTED_ROLE_GATED_LABELS = frozenset({
    OWNER_GATED_EXTERNAL, ADMIN_GATED_EXTERNAL, ORACLE_GATED_EXTERNAL,
    OPERATOR_GATED_EXTERNAL, MINTER_GATED_EXTERNAL, BURNER_GATED_EXTERNAL,
    PAUSER_GATED_EXTERNAL, KEEPER_GATED_EXTERNAL, GUARDIAN_GATED_EXTERNAL,
    CONTROLLER_GATED_EXTERNAL, MANAGER_GATED_EXTERNAL, GOVERNANCE_GATED_EXTERNAL,
    TREASURY_GATED_EXTERNAL, FEE_RECIPIENT_GATED_EXTERNAL, AUTHORITY_GATED_EXTERNAL,
    ACCESS_CONTROL_GATED_EXTERNAL, ROLE_GATED_EXTERNAL, PROBABLY_ROLE_GATED_EXTERNAL,
    ALLOWLIST_GATED_EXTERNAL, SENDER_WHITELIST_GATED_EXTERNAL,
})
UNKNOWN_GATED_LABELS = frozenset({
    UNKNOWN_MODIFIER_GATED_EXTERNAL, UNKNOWN_AUTH_HELPER_GATED_EXTERNAL,
    UNKNOWN_REACHABILITY,
})
CONTEXT_GATED_LABELS = frozenset({PROXY_CONTEXT_EXTERNAL, INITIALIZER_CONTEXT_EXTERNAL})
NO_VALUE_LABELS = frozenset({VIEW_ONLY_NO_VALUE_EFFECT, PURE_ONLY_NO_VALUE_EFFECT})
INTERNAL_LABELS = frozenset({INTERNAL_ONLY, PRIVATE_ONLY, CONSTRUCTOR_ONLY})

ALL_LABELS = (
    ATTACKER_REACHABLE_LABELS | TRUSTED_ROLE_GATED_LABELS | UNKNOWN_GATED_LABELS
    | CONTEXT_GATED_LABELS | NO_VALUE_LABELS | INTERNAL_LABELS
)


def is_attacker_reachable(label: str) -> bool:
    return label in ATTACKER_REACHABLE_LABELS


def is_trusted_role_gated(label: str) -> bool:
    return label in TRUSTED_ROLE_GATED_LABELS


def is_unknown_gated(label: str) -> bool:
    return label in UNKNOWN_GATED_LABELS


def is_context_gated(label: str) -> bool:
    return label in CONTEXT_GATED_LABELS


def is_non_value(label: str) -> bool:
    return label in NO_VALUE_LABELS


def is_internal(label: str) -> bool:
    return label in INTERNAL_LABELS


def decision_class(label: str) -> str:
    if is_attacker_reachable(label):
        return DC_ATTACKER_REACHABLE
    if is_trusted_role_gated(label):
        return DC_TRUSTED_ROLE_GATED
    if is_unknown_gated(label):
        return DC_UNKNOWN_GATED
    if is_context_gated(label):
        return DC_CONTEXT_GATED
    if is_non_value(label):
        return DC_NO_VALUE_EFFECT
    if is_internal(label):
        return DC_INTERNAL
    return DC_UNKNOWN_GATED


def decision_effect(label: str) -> str:
    """Human-readable decision effect for a reachability label."""
    dc = decision_class(label)
    return {
        DC_ATTACKER_REACHABLE: "ATTACKER_REACHABLE (eligible if material, fresh, in-scope, non-duplicate)",
        DC_TRUSTED_ROLE_GATED: "TRUSTED_ROLE_ONLY (KILL_TRUSTED_ROLE unless a separate authorization-bypass hypothesis exists)",
        DC_UNKNOWN_GATED: "PARK_REACHABILITY (who-can-call is unresolved; do not assume unprivileged)",
        DC_CONTEXT_GATED: "PARK_DEPLOYMENT / PARK_INITIALIZATION (needs deployment/initialization state)",
        DC_NO_VALUE_EFFECT: "KILL_NO_MATERIAL_IMPACT (no value effect unless it feeds another exploitable path)",
        DC_INTERNAL: "INTERNAL/PRIVATE/CONSTRUCTOR (not directly attacker-reachable)",
    }.get(dc, "PARK_REACHABILITY")


# ===========================================================================
# Evidence types (section 17 vocabulary)
# ===========================================================================
EV_MODIFIER_NAME_AUTH_LIKE = "MODIFIER_NAME_AUTH_LIKE"
EV_MODIFIER_BODY_MSG_SENDER_CHECK = "MODIFIER_BODY_MSG_SENDER_CHECK"
EV_DIRECT_BODY_MSG_SENDER_CHECK = "DIRECT_BODY_MSG_SENDER_CHECK"
EV_HELPER_MSG_SENDER_CHECK = "HELPER_MSG_SENDER_CHECK"
EV_ACCESS_CONTROL_HAS_ROLE = "ACCESS_CONTROL_HAS_ROLE"
EV_ACCESS_CONTROL_ONLY_ROLE = "ACCESS_CONTROL_ONLY_ROLE"
EV_ROLE_GETTER_PUBLIC_ADDRESS = "ROLE_GETTER_PUBLIC_ADDRESS"
EV_ROLE_GETTER_ASSEMBLY_SLOAD = "ROLE_GETTER_ASSEMBLY_SLOAD"
EV_AUTHORITY_CAN_CALL = "AUTHORITY_CAN_CALL"
EV_ALLOWLIST_MAPPING_CHECK = "ALLOWLIST_MAPPING_CHECK"
EV_NON_AUTH_MODIFIER_ONLY = "NON_AUTH_MODIFIER_ONLY"
EV_MIXED_AUTH_AND_NON_AUTH = "MIXED_AUTH_AND_NON_AUTH_MODIFIERS"
EV_INITIALIZER_CONTEXT_REQUIRES_DEPLOYMENT_STATE = "INITIALIZER_CONTEXT_REQUIRES_DEPLOYMENT_STATE"
EV_UNGUARDED_INITIALIZER_SETS_ROLE = "UNGUARDED_INITIALIZER_SETS_ROLE"
EV_INITIALIZER_MODIFIER = "INITIALIZER_MODIFIER"
EV_PROXY_CONTEXT_MODIFIER = "PROXY_CONTEXT_MODIFIER"
EV_UNKNOWN_CUSTOM_MODIFIER = "UNKNOWN_CUSTOM_MODIFIER"
EV_MODIFIER_CALL_GRAPH_CYCLE = "MODIFIER_CALL_GRAPH_CYCLE"
EV_PARSER_LIMITATION = "PARSER_LIMITATION"

# Warning vocabulary (section 25).
W_PARSER_LIMITATION = "REACHABILITY_PARSER_LIMITATION"
W_UNKNOWN_CUSTOM_MODIFIER = "UNKNOWN_CUSTOM_MODIFIER"
W_MODIFIER_CALL_GRAPH_CYCLE = "MODIFIER_CALL_GRAPH_CYCLE"
W_ROLE_GETTER_UNRESOLVED = "ROLE_GETTER_UNRESOLVED"
W_AUTH_HELPER_UNRESOLVED = "AUTH_HELPER_UNRESOLVED"
W_MIXED_AUTH_AND_NON_AUTH = "MIXED_AUTH_AND_NON_AUTH_MODIFIERS"
W_INITIALIZER_NEEDS_DEPLOYMENT = "INITIALIZER_CONTEXT_REQUIRES_DEPLOYMENT_STATE"
W_UNGUARDED_INITIALIZER = "UNGUARDED_INITIALIZER_SETS_ROLE"

MAX_HELPER_DEPTH = 4

# ===========================================================================
# Generic access-control vocabulary (no target-specific names)
# ===========================================================================
# Ordered (token, label, role_type). First substring hit wins, so more specific
# tokens come first (defaultadmin before admin).
_ROLE_TOKENS: tuple = (
    ("defaultadmin", ADMIN_GATED_EXTERNAL, "ADMIN"),
    ("superadmin", ADMIN_GATED_EXTERNAL, "ADMIN"),
    ("roleadmin", ADMIN_GATED_EXTERNAL, "ADMIN"),
    ("proxyadmin", ADMIN_GATED_EXTERNAL, "ADMIN"),
    ("admin", ADMIN_GATED_EXTERNAL, "ADMIN"),
    ("owner", OWNER_GATED_EXTERNAL, "OWNER"),
    ("oracle", ORACLE_GATED_EXTERNAL, "ORACLE"),
    ("operator", OPERATOR_GATED_EXTERNAL, "OPERATOR"),
    ("minter", MINTER_GATED_EXTERNAL, "MINTER"),
    ("burner", BURNER_GATED_EXTERNAL, "BURNER"),
    ("pauser", PAUSER_GATED_EXTERNAL, "PAUSER"),
    ("keeper", KEEPER_GATED_EXTERNAL, "KEEPER"),
    ("guardian", GUARDIAN_GATED_EXTERNAL, "GUARDIAN"),
    ("controller", CONTROLLER_GATED_EXTERNAL, "CONTROLLER"),
    ("manager", MANAGER_GATED_EXTERNAL, "MANAGER"),
    ("governor", GOVERNANCE_GATED_EXTERNAL, "GOVERNANCE"),
    ("governance", GOVERNANCE_GATED_EXTERNAL, "GOVERNANCE"),
    ("treasury", TREASURY_GATED_EXTERNAL, "TREASURY"),
    ("feerecipient", FEE_RECIPIENT_GATED_EXTERNAL, "FEE_RECIPIENT"),
    ("authority", AUTHORITY_GATED_EXTERNAL, "AUTHORITY"),
    ("authoriz", AUTHORITY_GATED_EXTERNAL, "AUTHORITY"),
    ("whitelist", ALLOWLIST_GATED_EXTERNAL, "ALLOWLIST"),
    ("allowlist", ALLOWLIST_GATED_EXTERNAL, "ALLOWLIST"),
    ("allowed", ALLOWLIST_GATED_EXTERNAL, "ALLOWLIST"),
    ("approved", ALLOWLIST_GATED_EXTERNAL, "ALLOWLIST"),
)

# Auth-name hints beyond explicit role tokens (used only for confidence MEDIUM).
_AUTH_NAME_HINTS = (
    "auth", "role", "permission", "access", "restricted", "privileged", "trusted",
    "whitelist", "allowlist", "allowed", "approved",
)

# Known non-auth modifiers: they constrain *state*, not the *caller*.
NON_AUTH_MODIFIERS = frozenset({
    "nonreentrant", "lock", "noreentrant", "whennotpaused", "whenpaused", "notpaused",
    "ifnotpaused", "nodelegatecall", "validamount", "validaddress", "notzero",
    "notnull", "streamexists", "campaignexists", "tokenexists", "deadlinenotexpired",
    "checkdeadline", "checkvalue", "notexpired", "notcanceled", "notvoided",
    "notdepleted", "notsettled", "validdeadline", "ensurenotpaused", "onlyinitializing",
})
INITIALIZER_MODIFIERS = frozenset({"initializer", "reinitializer", "oninitializing"})
PROXY_MODIFIERS = frozenset({"onlyproxy"})

# Function-call noise: not auth helpers (control flow + common builtins + sender accessors).
_CALL_NOISE = frozenset({
    "require", "revert", "assert", "if", "for", "while", "return", "emit", "do",
    "keccak256", "sha256", "sha3", "ripemd160", "ecrecover", "addmod", "mulmod",
    "abi", "address", "payable", "type", "new", "super", "selfdestruct", "blockhash",
    "gasleft", "sload", "sstore", "mload", "mstore", "msgsender", "_msgsender",
    "hasrole", "uint256", "uint", "int256", "bool", "bytes32", "string",
})


def classify_role_name(name: str):
    """Map a modifier / variable / getter name to (label, role_type) or (None, None)."""
    low = re.sub(r"[^a-z0-9]", "", (name or "").lower())
    for token, label, rtype in _ROLE_TOKENS:
        if token in low:
            return label, rtype
    return None, None


def classify_role_constant(const_name: str):
    """Map an AccessControl role constant (e.g. MINTER_ROLE) to (label, role_type)."""
    label, rtype = classify_role_name(const_name)
    if label is not None:
        return label, rtype
    return ROLE_GATED_EXTERNAL, "ROLE"


def _auth_like_name(name: str) -> bool:
    if classify_role_name(name)[0] is not None:
        return True
    low = re.sub(r"[^a-z0-9]", "", (name or "").lower())
    return any(h in low for h in _AUTH_NAME_HINTS)


# ===========================================================================
# Parsing utilities (regex + balanced-brace; line/column preserving)
# ===========================================================================
_CONTRACT_HEAD = re.compile(r"\b(?:abstract\s+)?(contract|library|interface)\s+([A-Za-z_]\w*)")
_FUNC_HEAD = re.compile(r"\bfunction\s+([A-Za-z_]\w*)\s*\(")
_MOD_HEAD = re.compile(r"\bmodifier\s+([A-Za-z_]\w*)")
_VIS_RE = re.compile(r"\b(external|public|internal|private)\b")
_MUT_RE = re.compile(r"\b(view|pure|payable)\b")
_NON_MODIFIER_KEYWORDS = frozenset({
    "external", "public", "internal", "private", "view", "pure", "payable",
    "virtual", "override", "returns", "memory", "storage", "calldata", "constant",
    "immutable", "keccak256", "abi",
})


def strip_comments(text: str) -> str:
    """Remove comments while preserving line and column positions."""
    def _blank_block(m: "re.Match") -> str:
        return re.sub(r"[^\n]", " ", m.group(0))

    text = re.sub(r"/\*.*?\*/", _blank_block, text, flags=re.DOTALL)
    text = re.sub(r"//[^\n]*", lambda m: " " * len(m.group(0)), text)
    return text


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, max(0, index)) + 1


def _match_delimited(text: str, open_idx: int, open_ch: str = "{", close_ch: str = "}"):
    """Return (inner_text, close_index) by matching ``open_ch``/``close_ch`` from ``open_idx``."""
    depth = 0
    i = open_idx
    n = len(text)
    while i < n:
        c = text[i]
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return text[open_idx + 1:i], i
        i += 1
    return text[open_idx + 1:], n


def _scan_header_tail(text: str, start: int):
    """From just after a param list, return (tail, index, kind) where kind is '{' or ';' or ''."""
    depth = 0
    i = start
    n = len(text)
    while i < n:
        c = text[i]
        if c in "([":
            depth += 1
        elif c in ")]":
            depth -= 1
        elif depth == 0 and c == "{":
            return text[start:i], i, "{"
        elif depth == 0 and c == ";":
            return text[start:i], i, ";"
        i += 1
    return text[start:n], n, ""


@dataclass
class ParsedContract:
    name: str
    kind: str
    start: int
    body_start: int
    end: int
    line: int


@dataclass
class ParsedFunction:
    name: str
    visibility: str
    mutability: str
    tail: str
    body: str
    has_body: bool
    start: int
    line: int


@dataclass
class ParsedModifier:
    name: str
    params: str
    body: str
    line: int


def find_contracts(text: str) -> list:
    out: list = []
    for m in _CONTRACT_HEAD.finditer(text):
        i = m.end()
        depth = 0
        n = len(text)
        brace = -1
        while i < n:
            c = text[i]
            if c in "([":
                depth += 1
            elif c in ")]":
                depth -= 1
            elif c == "{" and depth == 0:
                brace = i
                break
            elif c == ";" and depth == 0:
                break
            i += 1
        if brace == -1:
            continue
        _, end = _match_delimited(text, brace, "{", "}")
        out.append(ParsedContract(name=m.group(2), kind=m.group(1), start=m.start(),
                                  body_start=brace + 1, end=end, line=line_of(text, m.start())))
    return out


def find_functions(text: str) -> list:
    out: list = []
    for m in _FUNC_HEAD.finditer(text):
        params, pend = _match_delimited(text, m.end() - 1, "(", ")")
        tail, tend, kind = _scan_header_tail(text, pend + 1)
        body = ""
        if kind == "{":
            body, _ = _match_delimited(text, tend, "{", "}")
        vis_m = _VIS_RE.search(tail)
        mut_m = _MUT_RE.search(tail)
        out.append(ParsedFunction(
            name=m.group(1),
            visibility=vis_m.group(1) if vis_m else "public",
            mutability=mut_m.group(1) if mut_m else "",
            tail=tail, body=body, has_body=(kind == "{"),
            start=m.start(), line=line_of(text, m.start()),
        ))
    return out


def find_modifiers(text: str) -> list:
    out: list = []
    n = len(text)
    for m in _MOD_HEAD.finditer(text):
        i = m.end()
        while i < n and text[i].isspace():
            i += 1
        params = ""
        if i < n and text[i] == "(":
            params, pend = _match_delimited(text, i, "(", ")")
            i = pend + 1
        while i < n and text[i] not in "{;":
            i += 1
        body = ""
        if i < n and text[i] == "{":
            body, _ = _match_delimited(text, i, "{", "}")
        out.append(ParsedModifier(name=m.group(1), params=params, body=body, line=line_of(text, m.start())))
    return out


def extract_modifier_invocations(tail: str) -> list:
    """Return [(name, args)] modifier invocations from a function header tail."""
    t = re.sub(r"\breturns\s*\([^()]*\)", " ", tail)
    t = re.sub(r"\boverride\s*\([^()]*\)", " ", t)
    invs: list = []
    for m in re.finditer(r"([A-Za-z_]\w*)\s*(\([^()]*\))?", t):
        name = m.group(1)
        if not name or name in _NON_MODIFIER_KEYWORDS:
            continue
        invs.append((name, (m.group(2) or "").strip()))
    return invs


def find_called_helpers(body: str) -> list:
    out: list = []
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\(", body or ""):
        name = m.group(1)
        if name.lower() in _CALL_NOISE:
            continue
        if name not in out:
            out.append(name)
    return out


# ===========================================================================
# Auth detectors (operate on a single, comment-stripped body)
# ===========================================================================
_SENDER = r"(?:msg\s*\.\s*sender|_msgSender\s*\(\s*\)|tx\s*\.\s*origin)"
_SENDER_RHS = re.compile(_SENDER + r"\s*(==|!=)\s*([A-Za-z_]\w*)\s*(\(\s*\))?")
_SENDER_LHS = re.compile(r"([A-Za-z_]\w*)\s*(\(\s*\))?\s*(==|!=)\s*" + _SENDER)
_HAS_ROLE = re.compile(r"\b(?:hasRole|_checkRole|checkRole)\s*\(\s*([A-Za-z_]\w*)")
_NESTED_ROLE_MAP = re.compile(r"\broles?\b\s*\[[^\]]*\]\s*\[\s*(?:msg\s*\.\s*sender|_msgSender\s*\(\s*\))")
_ALLOWLIST_MAP = re.compile(
    r"\b(\w*(?:allow|white)list\w*|isAllowed|isWhitelisted|isApproved|allowed|approved|trusted|permissions?)"
    r"\s*\[\s*(?:msg\s*\.\s*sender|_msgSender\s*\(\s*\))", re.IGNORECASE)
_AUTHORITY = re.compile(r"\b(?:authority\s*\.\s*canCall|\.canCall|isAuthorized|requireAuth\w*)\s*\(", re.IGNORECASE)
_ASSEMBLY_SLOAD = re.compile(r"assembly\s*\{", re.IGNORECASE)


def detect_sender_auth(body: str) -> list:
    out: list = []
    for m in _SENDER_RHS.finditer(body or ""):
        out.append({"other": m.group(2), "op": m.group(1)})
    for m in _SENDER_LHS.finditer(body or ""):
        out.append({"other": m.group(1), "op": m.group(3)})
    return out


def detect_has_role(body: str) -> list:
    return [m.group(1) for m in _HAS_ROLE.finditer(body or "")]


def detect_allowlist(body: str) -> list:
    out: list = []
    if _NESTED_ROLE_MAP.search(body or ""):
        out.append({"label": ACCESS_CONTROL_GATED_EXTERNAL, "role_type": "ROLE",
                    "subject": "roles[..][msg.sender]", "detail": "role-mapping membership check",
                    "evidence_type": EV_ACCESS_CONTROL_HAS_ROLE})
    for m in _ALLOWLIST_MAP.finditer(body or ""):
        out.append({"label": ALLOWLIST_GATED_EXTERNAL, "role_type": "ALLOWLIST",
                    "subject": m.group(1), "detail": "sender allowlist/whitelist mapping check",
                    "evidence_type": EV_ALLOWLIST_MAPPING_CHECK})
    return out


def detect_authority_call(body: str) -> bool:
    return bool(_AUTHORITY.search(body or ""))


def detect_assembly_sload_getter(body: str) -> bool:
    b = body or ""
    if not _ASSEMBLY_SLOAD.search(b):
        return False
    asm_start = b.lower().find("assembly")
    return "sload" in b[asm_start:].lower()


def _returns_address(fn: ParsedFunction) -> bool:
    return "address" in (fn.tail or "")


# ===========================================================================
# Evidence + result dataclasses
# ===========================================================================
@dataclass
class ReachabilityEvidence:
    evidence_type: str
    subject: str = ""
    detail: str = ""
    confidence: str = UNKNOWN
    line: int | None = None

    def to_dict(self) -> dict:
        return {"evidence_type": self.evidence_type, "subject": self.subject,
                "detail": self.detail, "confidence": self.confidence, "line": self.line}


@dataclass
class FunctionReachability:
    function_name: str
    contract_name: str | None = None
    visibility: str = ""
    state_mutability: str | None = None
    modifiers: list[str] = field(default_factory=list)
    non_auth_modifiers: list = field(default_factory=list)
    final_label: str = UNKNOWN_REACHABILITY
    decision_class: str = DC_UNKNOWN_GATED
    confidence: str = UNKNOWN
    evidence: list = field(default_factory=list)       # ReachabilityEvidence
    warnings: list = field(default_factory=list)
    source_path: str = ""
    line: int = 0

    @property
    def surface(self) -> str:
        return f"{self.contract_name}.{self.function_name}" if self.contract_name else self.function_name

    @property
    def contract(self) -> str:
        """Backward-compatible accessor used by hunter render/integration code."""
        return self.contract_name or ""

    def evidence_types(self) -> list:
        return [e.evidence_type for e in self.evidence]

    def to_dict(self) -> dict:
        return {
            "function_name": self.function_name,
            "contract_name": self.contract_name,
            "contract": self.contract,
            "surface": self.surface,
            "visibility": self.visibility,
            "state_mutability": self.state_mutability,
            "modifiers": list(self.modifiers),
            "non_auth_modifiers": list(self.non_auth_modifiers),
            "final_reachability": self.final_label,
            "decision_class": self.decision_class,
            "decision_effect": decision_effect(self.final_label),
            "confidence": self.confidence,
            "evidence": [e.to_dict() for e in self.evidence],
            "evidence_types": self.evidence_types(),
            "warnings": list(self.warnings),
            "source_path": self.source_path,
            "line": self.line,
        }


@dataclass
class _Resolved:
    found: bool = False
    label: str = ""
    role_type: str = ""
    confidence: str = UNKNOWN
    evidence: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    cycle: bool = False
    unresolved: bool = False


@dataclass
class _ModResult:
    kind: str  # auth | name_auth | unknown | unknown_helper | non_auth | initializer | proxy
    name: str = ""
    label: str = ""
    role_type: str = ""
    confidence: str = UNKNOWN
    evidence: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


@dataclass
class ReachabilityIndex:
    modifiers: dict = field(default_factory=dict)   # name -> ParsedModifier
    functions: dict = field(default_factory=dict)   # name -> ParsedFunction


# Role-label specificity: prefer a named role over the generic buckets.
_LABEL_RANK = {
    PROBABLY_ROLE_GATED_EXTERNAL: 0, SENDER_WHITELIST_GATED_EXTERNAL: 1,
    AUTHORITY_GATED_EXTERNAL: 2, ALLOWLIST_GATED_EXTERNAL: 2,
    ROLE_GATED_EXTERNAL: 3, ACCESS_CONTROL_GATED_EXTERNAL: 4,
}


def _better(best, label, role_type, confidence):
    """Keep the more specific / higher-confidence resolved auth label."""
    cand = (label, role_type, confidence)
    if best is None:
        return cand
    rank = lambda lab: _LABEL_RANK.get(lab, 9)  # named roles rank highest (9)
    conf_rank = {HIGH: 3, MEDIUM: 2, LOW: 1, UNKNOWN: 0}
    if (rank(label), conf_rank.get(confidence, 0)) > (rank(best[0]), conf_rank.get(best[2], 0)):
        return cand
    return best


def _resolve_body(body: str, index: ReachabilityIndex, depth: int, seen: set, sender_tag: str) -> _Resolved:
    """Scan a modifier/helper body for a caller (auth) check, recursing into helpers."""
    res = _Resolved()
    best = None

    for f in detect_sender_auth(body):
        other = f.get("other") or ""
        label, rtype = classify_role_name(other)
        conf = HIGH if label is not None else MEDIUM
        if label is None:
            label, rtype = PROBABLY_ROLE_GATED_EXTERNAL, "UNKNOWN_ROLE"
        getter = index.functions.get(other)
        if getter is not None and getter.body:
            if detect_assembly_sload_getter(getter.body):
                res.evidence.append(ReachabilityEvidence(
                    EV_ROLE_GETTER_ASSEMBLY_SLOAD, other, f"role getter {other}() loads an address via inline assembly sload", HIGH, getter.line))
                glabel, grtype = classify_role_name(other)
                if glabel is not None:
                    label, rtype, conf = glabel, grtype, HIGH
            elif _returns_address(getter):
                res.evidence.append(ReachabilityEvidence(
                    EV_ROLE_GETTER_PUBLIC_ADDRESS, other, f"role getter {other}() returns a stored address", HIGH, getter.line))
        res.evidence.append(ReachabilityEvidence(
            sender_tag, other or "msg.sender", f"compares msg.sender to {other or 'a stored address'}", conf))
        best = _better(best, label, rtype, conf)

    for arg in detect_has_role(body):
        glabel, grtype = classify_role_constant(arg)
        res.evidence.append(ReachabilityEvidence(
            EV_ACCESS_CONTROL_HAS_ROLE, arg, f"AccessControl hasRole/_checkRole({arg}, msg.sender)", HIGH))
        best = _better(best, glabel, grtype, HIGH)

    for al in detect_allowlist(body):
        res.evidence.append(ReachabilityEvidence(
            al["evidence_type"], al["subject"], al["detail"], HIGH))
        best = _better(best, al["label"], al["role_type"], HIGH)

    if detect_authority_call(body):
        res.evidence.append(ReachabilityEvidence(
            EV_AUTHORITY_CAN_CALL, "authority", "authority.canCall / isAuthorized(msg.sender, ...)", MEDIUM))
        best = _better(best, AUTHORITY_GATED_EXTERNAL, "AUTHORITY", MEDIUM)

    helpers = find_called_helpers(body)
    if best is None and depth > 0:
        for helper in helpers:
            if helper in seen:
                res.warnings.append(W_MODIFIER_CALL_GRAPH_CYCLE)
                res.evidence.append(ReachabilityEvidence(
                    EV_MODIFIER_CALL_GRAPH_CYCLE, helper, "cycle detected in modifier/auth-helper call graph", UNKNOWN))
                res.cycle = True
                return res
            hfn = index.functions.get(helper)
            if hfn is None or not hfn.body:
                continue
            sub = _resolve_body(hfn.body, index, depth - 1, seen | {helper}, EV_HELPER_MSG_SENDER_CHECK)
            res.evidence.extend(sub.evidence)
            res.warnings.extend(sub.warnings)
            if sub.cycle:
                res.cycle = True
                return res
            if sub.unresolved:
                res.unresolved = True
                return res
            if sub.found:
                best = _better(best, sub.label, sub.role_type, sub.confidence)
    elif best is None and helpers:
        resolvable = [h for h in helpers if h in index.functions and index.functions[h].body]
        if resolvable:
            res.unresolved = True
            res.warnings.extend([W_AUTH_HELPER_UNRESOLVED, W_PARSER_LIMITATION])
            res.evidence.append(ReachabilityEvidence(
                EV_PARSER_LIMITATION, resolvable[0],
                f"auth-helper analysis reached the depth cap ({MAX_HELPER_DEPTH})", UNKNOWN))

    if best is not None:
        res.found, res.label, res.role_type, res.confidence = True, best[0], best[1], best[2]
    return res


def classify_modifier(name: str, args: str, index: ReachabilityIndex, depth: int = MAX_HELPER_DEPTH) -> _ModResult:
    low = name.lower()
    if low in NON_AUTH_MODIFIERS:
        return _ModResult("non_auth", name, evidence=[ReachabilityEvidence(
            EV_NON_AUTH_MODIFIER_ONLY, name, "known non-auth modifier (constrains state, not the caller)", HIGH)])
    if low in INITIALIZER_MODIFIERS:
        return _ModResult("initializer", name, evidence=[ReachabilityEvidence(
            EV_INITIALIZER_MODIFIER, name, "initializer/reinitializer — deployment/initialization context, not user auth", HIGH)])
    if low in PROXY_MODIFIERS:
        return _ModResult("proxy", name, evidence=[ReachabilityEvidence(
            EV_PROXY_CONTEXT_MODIFIER, name, "proxy-context modifier (delegatecall context), not user auth", MEDIUM)])

    mod = index.modifiers.get(name)
    arg_role = None
    if args:
        m = re.match(r"\(\s*([A-Za-z_]\w*)", args)
        if m:
            arg_role = m.group(1)
    is_only_role = (low == "onlyrole") or (mod is not None and (
        bool(detect_has_role(mod.body)) or bool(_NESTED_ROLE_MAP.search(mod.body or ""))))

    if mod is None:
        if is_only_role and arg_role:
            role_label, role_type = classify_role_constant(arg_role)
            return _ModResult(
                "name_auth", name, label=role_label, role_type=role_type,
                confidence=MEDIUM,
                evidence=[
                    ReachabilityEvidence(
                        EV_ACCESS_CONTROL_ONLY_ROLE, arg_role,
                        f"onlyRole({arg_role}); modifier declaration not found in scanned sources",
                        MEDIUM),
                    ReachabilityEvidence(
                        EV_PARSER_LIMITATION, name,
                        "modifier body unavailable for analysis", UNKNOWN),
                ],
                warnings=[W_PARSER_LIMITATION],
            )
        rn_label, rn_type = classify_role_name(name)
        if rn_label is not None or _auth_like_name(name):
            return _ModResult("name_auth", name, label=(rn_label or ROLE_GATED_EXTERNAL),
                              role_type=(rn_type or "ROLE"), confidence=MEDIUM,
                              evidence=[ReachabilityEvidence(EV_MODIFIER_NAME_AUTH_LIKE, name,
                                        "auth-like modifier name; declaration not found in scanned sources", MEDIUM)],
                              warnings=[W_PARSER_LIMITATION])
        return _ModResult("unknown", name, confidence=UNKNOWN,
                          evidence=[ReachabilityEvidence(EV_UNKNOWN_CUSTOM_MODIFIER, name,
                                    "custom modifier declaration not found in scanned sources", UNKNOWN),
                                    ReachabilityEvidence(EV_PARSER_LIMITATION, name,
                                    "modifier body unavailable for analysis", UNKNOWN)],
                          warnings=[W_UNKNOWN_CUSTOM_MODIFIER, W_PARSER_LIMITATION])

    res = _resolve_body(mod.body, index, depth, {name}, EV_MODIFIER_BODY_MSG_SENDER_CHECK)
    if res.cycle or res.unresolved:
        return _ModResult("unknown_helper", name, confidence=UNKNOWN,
                          evidence=res.evidence, warnings=res.warnings + [W_AUTH_HELPER_UNRESOLVED])
    if res.found:
        label, rtype, conf = res.label, res.role_type, res.confidence
        ev = list(res.evidence)
        if is_only_role and arg_role:
            rl_label, rl_type = classify_role_constant(arg_role)
            label, rtype, conf = rl_label, rl_type, HIGH
            ev.append(ReachabilityEvidence(EV_ACCESS_CONTROL_ONLY_ROLE, arg_role, f"onlyRole({arg_role})", HIGH))
        return _ModResult("auth", name, label=label, role_type=rtype, confidence=conf,
                          evidence=ev, warnings=res.warnings)

    # Body resolved but no caller check found.
    rn_label, rn_type = classify_role_name(name)
    if rn_label is not None or _auth_like_name(name):
        return _ModResult("name_auth", name, label=(rn_label or ROLE_GATED_EXTERNAL),
                          role_type=(rn_type or "ROLE"), confidence=MEDIUM,
                          evidence=res.evidence + [ReachabilityEvidence(EV_MODIFIER_NAME_AUTH_LIKE, name,
                                    "auth-like modifier name; body did not confirm a caller check", MEDIUM)],
                          warnings=res.warnings)
    helpers = find_called_helpers(mod.body)
    if helpers:
        return _ModResult("unknown", name, confidence=UNKNOWN,
                          evidence=res.evidence + [ReachabilityEvidence(EV_UNKNOWN_CUSTOM_MODIFIER, name,
                                    "modifier delegates to helper(s) with no resolved caller check: " + ", ".join(helpers), UNKNOWN)],
                          warnings=res.warnings + [W_UNKNOWN_CUSTOM_MODIFIER])
    return _ModResult("non_auth", name, evidence=res.evidence + [ReachabilityEvidence(
        EV_NON_AUTH_MODIFIER_ONLY, name, "modifier body checks state, not the caller", MEDIUM)],
        warnings=res.warnings)


_OWNER_WRITE_RE = re.compile(
    r"\b(_?(?:owner|admin|role|governance|governor|authority|operator|controller|manager|"
    r"oracle|guardian|keeper|minter|burner|pauser))\w*\s*=", re.IGNORECASE)


def classify_function_reachability(fn: ParsedFunction, contract: str, index: ReachabilityIndex) -> FunctionReachability:
    out = FunctionReachability(
        function_name=fn.name, contract_name=contract or None, visibility=fn.visibility,
        state_mutability=fn.mutability or "nonpayable", line=fn.line,
        modifiers=[n for n, _ in extract_modifier_invocations(fn.tail)],
    )

    if fn.visibility == "private":
        out.final_label, out.confidence, out.decision_class = PRIVATE_ONLY, HIGH, DC_INTERNAL
        return out
    if fn.visibility == "internal":
        out.final_label, out.confidence, out.decision_class = INTERNAL_ONLY, HIGH, DC_INTERNAL
        return out

    mod_results = [classify_modifier(n, a, index) for n, a in extract_modifier_invocations(fn.tail)]
    direct = _resolve_body(
        fn.body, index, MAX_HELPER_DEPTH, {fn.name}, EV_DIRECT_BODY_MSG_SENDER_CHECK)

    for r in mod_results:
        out.evidence.extend(r.evidence)
        out.warnings.extend(r.warnings)
    out.evidence.extend(direct.evidence)
    out.warnings.extend(direct.warnings)
    out.non_auth_modifiers = [r.name for r in mod_results if r.kind == "non_auth"]

    auth = [r for r in mod_results if r.kind == "auth"]
    if direct.found:
        auth.append(_ModResult("auth", fn.name, label=direct.label, role_type=direct.role_type,
                               confidence=direct.confidence, evidence=direct.evidence))
    name_auth = [r for r in mod_results if r.kind == "name_auth"]
    unknown = [r for r in mod_results if r.kind in ("unknown", "unknown_helper")]
    direct_unknown = direct.cycle or direct.unresolved
    has_initializer = any(r.kind == "initializer" for r in mod_results)
    has_proxy = any(r.kind == "proxy" for r in mod_results)

    if auth:
        best = None
        for r in auth:
            best = _better(best, r.label, r.role_type, r.confidence)
        out.final_label, out.confidence = best[0], best[2]
        if out.non_auth_modifiers:
            out.warnings.append(W_MIXED_AUTH_AND_NON_AUTH)
            out.evidence.append(ReachabilityEvidence(
                EV_MIXED_AUTH_AND_NON_AUTH, fn.name,
                "auth modifier dominates accompanying non-auth modifier(s)", HIGH, fn.line))
    elif name_auth:
        out.final_label, out.confidence = name_auth[0].label, MEDIUM
    elif unknown or direct_unknown:
        if direct_unknown or any(r.kind == "unknown_helper" for r in unknown):
            out.final_label = UNKNOWN_AUTH_HELPER_GATED_EXTERNAL
        else:
            out.final_label = UNKNOWN_MODIFIER_GATED_EXTERNAL
        out.confidence = UNKNOWN
    elif has_initializer:
        out.final_label, out.confidence = INITIALIZER_CONTEXT_EXTERNAL, MEDIUM
        out.warnings.append(W_INITIALIZER_NEEDS_DEPLOYMENT)
        out.evidence.append(ReachabilityEvidence(
            EV_INITIALIZER_CONTEXT_REQUIRES_DEPLOYMENT_STATE, fn.name,
            "initializer/reinitializer reachability depends on deployed initialization state",
            MEDIUM, fn.line))
    elif has_proxy:
        out.final_label, out.confidence = PROXY_CONTEXT_EXTERNAL, MEDIUM
    else:
        out.final_label = UNPRIVILEGED_EXTERNAL if fn.visibility == "external" else UNPRIVILEGED_PUBLIC
        out.confidence = HIGH

    # View/pure functions move no value (the gate, if any, still wins for "who can call").
    if fn.mutability in ("view", "pure") and out.final_label in (UNPRIVILEGED_EXTERNAL, UNPRIVILEGED_PUBLIC):
        out.final_label = VIEW_ONLY_NO_VALUE_EFFECT if fn.mutability == "view" else PURE_ONLY_NO_VALUE_EFFECT
        out.confidence = HIGH

    if _returns_address(fn) and detect_assembly_sload_getter(fn.body):
        out.evidence.append(ReachabilityEvidence(
            EV_ROLE_GETTER_ASSEMBLY_SLOAD, fn.name,
            f"public address getter {fn.name}() loads its value via inline assembly sload",
            HIGH, fn.line))
    elif _returns_address(fn) and classify_role_name(fn.name)[0] is not None:
        out.evidence.append(ReachabilityEvidence(
            EV_ROLE_GETTER_PUBLIC_ADDRESS, fn.name,
            f"public address getter {fn.name}() exposes a role address", MEDIUM, fn.line))

    # Unguarded initializer that sets a role/owner variable is itself the reachable surface.
    if out.final_label in (UNPRIVILEGED_EXTERNAL, UNPRIVILEGED_PUBLIC) and \
            re.match(r"(?i)(initialize|init|setup|__init)", fn.name) and _OWNER_WRITE_RE.search(fn.body or ""):
        out.warnings.append(W_UNGUARDED_INITIALIZER)
        out.evidence.append(ReachabilityEvidence(
            EV_UNGUARDED_INITIALIZER_SETS_ROLE, fn.name,
            "unguarded initializer-style function assigns an owner/admin/role variable (separate takeover hypothesis)", MEDIUM, fn.line))

    out.decision_class = decision_class(out.final_label)
    # De-duplicate warnings, preserve order.
    seen: set = set()
    out.warnings = [w for w in out.warnings if not (w in seen or seen.add(w))]
    return out


class ReachabilityMap:
    """A reachability classification for every parsed function definition in scope."""

    def __init__(self, functions: list, warnings: list | None = None):
        self.functions = functions
        self.warnings = warnings or []
        self._by_surface: dict = {}
        for fr in functions:
            self._by_surface[fr.surface.lower()] = fr
            self._by_surface.setdefault(fr.function_name.lower(), fr)

    def lookup(self, contract: str, function: str):
        if contract and function:
            hit = self._by_surface.get(f"{contract}.{function}".lower())
            if hit is not None:
                return hit
        if function:
            return self._by_surface.get(function.lower())
        return None

    def to_list(self) -> list:
        return [fr.to_dict() for fr in self.functions]

    def summary(self) -> dict:
        counts: dict = {}
        for fr in self.functions:
            counts[fr.decision_class] = counts.get(fr.decision_class, 0) + 1
        return {
            "functions_classified": len(self.functions),
            "by_decision_class": counts,
            "attacker_reachable": sum(1 for f in self.functions if is_attacker_reachable(f.final_label)),
            "trusted_role_gated": sum(1 for f in self.functions if is_trusted_role_gated(f.final_label)),
            "unknown_gated": sum(1 for f in self.functions if is_unknown_gated(f.final_label)),
            "context_gated": sum(1 for f in self.functions if is_context_gated(f.final_label)),
        }


def _build_index(file_texts: list) -> ReachabilityIndex:
    index = ReachabilityIndex()
    for _path, clean in file_texts:
        for mod in find_modifiers(clean):
            cur = index.modifiers.get(mod.name)
            if cur is None or (not cur.body and mod.body):
                index.modifiers[mod.name] = mod
        for fn in find_functions(clean):
            cur = index.functions.get(fn.name)
            if cur is None or (not cur.has_body and fn.has_body):
                index.functions[fn.name] = fn
    return index


def _contract_of(contracts: list, offset: int) -> str:
    best = ""
    best_span = None
    for c in contracts:
        if c.body_start <= offset < c.end:
            span = c.end - c.body_start
            if best_span is None or span < best_span:
                best, best_span = c.name, span
    return best


def build_reachability_map(sources: dict) -> ReachabilityMap:
    """Classify every function definition across the in-scope contract sources.

    ``sources`` maps contract name -> (path, raw_text), as produced by
    ``source_scan.load_contract_sources``. Multiple contracts may share one file; we
    de-duplicate by path, build a cross-file modifier/function index (so an inherited
    base modifier still resolves), then classify per contract.
    """
    by_path: dict = {}
    for _name, (path, text) in (sources or {}).items():
        if path and path not in by_path:
            by_path[path] = strip_comments(text)

    file_texts = list(by_path.items())
    index = _build_index(file_texts)

    functions: list = []
    seen_surfaces: set = set()
    for path, clean in file_texts:
        contracts = find_contracts(clean)
        for fn in find_functions(clean):
            if not fn.has_body:
                continue
            cname = _contract_of(contracts, fn.start)
            kind = next((c.kind for c in contracts if c.name == cname), "contract")
            if kind == "interface":
                continue  # interface declarations are not call surfaces
            key = f"{cname}.{fn.name}".lower()
            if key in seen_surfaces:
                continue
            seen_surfaces.add(key)
            fr = classify_function_reachability(fn, cname, index)
            fr.source_path = path
            functions.append(fr)
    return ReachabilityMap(functions)


def analyze_reachability(source_text: str) -> dict[str, FunctionReachability]:
    """Classify functions from one Solidity source string.

    The returned mapping is keyed by ``Contract.function`` when contract ownership can
    be resolved, otherwise by function name. It is a small public API for focused
    tests and callers that do not already have a hunter review-map source dictionary.
    """
    clean = strip_comments(source_text or "")
    index = _build_index([("<memory>", clean)])
    contracts = find_contracts(clean)
    out: dict[str, FunctionReachability] = {}
    for fn in find_functions(clean):
        cname = _contract_of(contracts, fn.start)
        kind = next((c.kind for c in contracts if c.name == cname), "contract")
        if kind == "interface" or not fn.has_body:
            continue
        fr = classify_function_reachability(fn, cname, index)
        out[fr.surface] = fr
    return out
