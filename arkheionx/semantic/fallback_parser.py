"""Fallback Solidity parser (the primary semantic extraction path).

No compiler required. Uses line-preserving comment/string blanking plus
brace/paren matching to recover contracts, inheritance, state variables,
structs/enums/events/modifiers, and functions with their semantic effects
(internal/external calls, storage reads/writes, events, transfers, low-level
calls, calldata field access, msg.sender/value use, role gates).

Every fact is best-effort and carries a confidence. Precision is preferred over
recall: a missed effect is acceptable, a fabricated one is not.
"""
from __future__ import annotations

import re

from . import models as M

# ---------------------------------------------------------------------------
# Line-preserving comment + string blanking.
# ---------------------------------------------------------------------------

def blank_noise(text: str) -> str:
    """Blank comments and string literals, preserving every newline and length.

    This keeps byte/line offsets identical to the original so reported line
    numbers stay accurate while braces/keywords inside comments or strings can
    no longer confuse the scanners.
    """
    out = list(text)
    n = len(text)
    i = 0
    state = None  # None | "line" | "block" | "str" | "char"
    quote = ""
    while i < n:
        ch = text[i]
        nxt = text[i + 1] if i + 1 < n else ""
        if state is None:
            if ch == "/" and nxt == "/":
                state = "line"
                out[i] = " "; out[i + 1] = " "; i += 2; continue
            if ch == "/" and nxt == "*":
                state = "block"
                out[i] = " "; out[i + 1] = " "; i += 2; continue
            if ch == '"' or ch == "'":
                state = "str"; quote = ch
                i += 1; continue  # keep the opening quote
            i += 1; continue
        if state == "line":
            if ch == "\n":
                state = None
            else:
                out[i] = " "
            i += 1; continue
        if state == "block":
            if ch == "*" and nxt == "/":
                out[i] = " "; out[i + 1] = " "; state = None; i += 2; continue
            if ch != "\n":
                out[i] = " "
            i += 1; continue
        if state == "str":
            if ch == "\\":
                if i + 1 < n and text[i + 1] != "\n":
                    out[i + 1] = " "
                i += 2; continue
            if ch == quote:
                state = None
                i += 1; continue  # keep the closing quote
            if ch != "\n":
                out[i] = " "
            i += 1; continue
    return "".join(out)


def line_of(text: str, index: int) -> int:
    return text.count("\n", 0, max(0, index)) + 1


def match_delim(text: str, start: int, open_ch: str, close_ch: str) -> int:
    """Return index of the delimiter that closes the one at ``start``, or len(text)."""
    depth = 0
    n = len(text)
    i = start
    while i < n:
        c = text[i]
        if c == open_ch:
            depth += 1
        elif c == close_ch:
            depth -= 1
            if depth == 0:
                return i
        i += 1
    return n


# ---------------------------------------------------------------------------
# Regexes (run on blanked text).
# ---------------------------------------------------------------------------
_CONTRACT_RE = re.compile(
    r"\b(?:(abstract)\s+)?(contract|interface|library)\s+([A-Za-z_]\w*)\s*"
    r"(is\b[^{]*)?\{",
    re.DOTALL,
)
_FUNC_RE = re.compile(r"\b(function|constructor|modifier)\b(?:\s+([A-Za-z_]\w*))?\s*\(")
_VIS_RE = re.compile(r"\b(public|external|internal|private)\b")
_MUT_RE = re.compile(r"\b(view|pure|payable)\b")
_RETURNS_RE = re.compile(r"\breturns\b")
_STRUCT_RE = re.compile(r"\bstruct\s+([A-Za-z_]\w*)\s*\{")
_ENUM_RE = re.compile(r"\benum\s+([A-Za-z_]\w*)\s*\{")
_EVENT_RE = re.compile(r"\bevent\s+([A-Za-z_]\w*)\s*\(")
_ERROR_RE = re.compile(r"\berror\s+([A-Za-z_]\w*)\s*\(")

_STATEVAR_RE = re.compile(
    r"(?P<type>mapping\s*\(.*?\)\s*(?:\[\s*\])*|[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)?\s*(?:\[[^\]]*\])*)\s+"
    r"(?P<mods>(?:public|private|internal|constant|immutable|override(?:\([^)]*\))?)\s+)*"
    r"(?P<name>[A-Za-z_]\w*)\s*(?:=|;)",
    re.DOTALL,
)
_TYPE_KEYWORDS = {
    "return", "returns", "emit", "require", "assert", "revert", "if", "for",
    "while", "else", "using", "pragma", "import", "function", "modifier",
    "constructor", "struct", "enum", "event", "error", "contract", "interface",
    "library", "is", "new", "delete", "unchecked", "do", "try", "catch", "assembly",
}

_ROLE_MOD_HINT = re.compile(
    r"only|role|auth|admin|owner|govern|guardian|operator|keeper|manager|"
    r"controller|whenNotPaused|whenPaused|restricted|permission",
    re.IGNORECASE,
)
_ROLE_BODY_RE = re.compile(
    r"(hasRole|_checkRole|onlyRole|_onlyOwner|requireAuth|isAuthorized|"
    r"msg\.sender\s*==\s*(owner|admin|governance|guardian|operator|_owner))",
)


def _split_top_level(s: str, sep: str = ",") -> list:
    """Split ``s`` on ``sep`` at paren/bracket depth zero."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        if ch == sep and depth == 0:
            out.append("".join(cur).strip()); cur = []
        else:
            cur.append(ch)
    if "".join(cur).strip():
        out.append("".join(cur).strip())
    return out


def _parse_params(raw: str) -> list:
    params = []
    for piece in _split_top_level(raw):
        if not piece:
            continue
        toks = piece.split()
        location = ""
        for loc in ("calldata", "memory", "storage"):
            if loc in toks:
                location = loc
                toks = [t for t in toks if t != loc]
        name = ""
        ptype = piece
        if len(toks) >= 2:
            name = toks[-1]
            ptype = " ".join(toks[:-1])
        elif len(toks) == 1:
            ptype = toks[0]
        params.append(M.Parameter(name=name, type=ptype.strip(), location=location))
    return params


def _parse_returns(attrs: str) -> list:
    m = _RETURNS_RE.search(attrs)
    if not m:
        return []
    paren = attrs.find("(", m.end())
    if paren < 0:
        return []
    close = match_delim(attrs, paren, "(", ")")
    inner = attrs[paren + 1:close]
    return _parse_params(inner)


def _parse_modifiers(attrs: str) -> list:
    # Drop the returns(...) clause first.
    m = _RETURNS_RE.search(attrs)
    head = attrs[:m.start()] if m else attrs
    mods = []
    for tok in _split_top_level(head, sep=" "):
        tok = tok.strip()
        if not tok:
            continue
        base = tok.split("(")[0]
        if base in ("public", "external", "internal", "private", "view", "pure",
                    "payable", "virtual", "override", "returns", ""):
            continue
        if re.match(r"^[A-Za-z_]\w*", base):
            mods.append(base)
    return mods


class FunctionBody:
    """Side-table entry the cross-cutting engines use; not serialized."""

    __slots__ = ("qualified", "contract", "file", "name", "body", "body_start_line",
                 "calldata_params", "state_vars")

    def __init__(self, qualified, contract, file, name, body, body_start_line,
                 calldata_params, state_vars):
        self.qualified = qualified
        self.contract = contract
        self.file = file
        self.name = name
        self.body = body
        self.body_start_line = body_start_line
        self.calldata_params = calldata_params
        self.state_vars = state_vars


class ParseResult:
    def __init__(self):
        self.contracts = []   # ContractSemantic
        self.bodies = {}      # qualified_name -> FunctionBody
        self.warnings = []
        self.func_names_by_contract = {}  # contract -> set(names)


def _detect_statevars(residue: str, base_line: int) -> list:
    out = []
    for m in _STATEVAR_RE.finditer(residue):
        ptype = re.sub(r"\s+", " ", m.group("type")).strip()
        name = m.group("name")
        first = ptype.split("(")[0].split()[0] if ptype else ""
        if first in _TYPE_KEYWORDS or name in _TYPE_KEYWORDS:
            continue
        mods = (m.group("mods") or "")
        vis = "internal"
        for v in ("public", "private", "internal"):
            if re.search(r"\b" + v + r"\b", mods):
                vis = v
        out.append(M.StateVariable(
            name=name, type=ptype, visibility=vis,
            line=base_line + line_of(residue, m.start()) - 1,
            is_mapping=ptype.startswith("mapping"),
            is_array=ptype.endswith("[]") or bool(re.search(r"\[[^\]]*\]$", ptype)),
            constant=bool(re.search(r"\b(constant|immutable)\b", mods)),
        ))
    # De-dupe by name (first declaration wins).
    seen, uniq = set(), []
    for sv in out:
        if sv.name in seen:
            continue
        seen.add(sv.name)
        uniq.append(sv)
    return uniq


_ALIAS_RE = re.compile(r"\b([A-Za-z_]\w*)\s+storage\s+([A-Za-z_]\w*)\s*=\s*([A-Za-z_]\w*)")


def storage_alias_map(body: str, state_var_names) -> dict:
    """Map ``local -> state_var`` for ``T storage local = stateVar...`` aliases."""
    out = {}
    for m in _ALIAS_RE.finditer(body):
        local, src = m.group(2), m.group(3)
        if src in state_var_names:
            out[local] = src
    return out


_WRITE_OP = r"(?:=[^=]|[-+*/|&^%]=|\+\+|--)"


def _earliest_write(body: str, name: str, member_required: bool):
    esc = re.escape(name)
    if member_required:
        # Storage-pointer aliases: only member/index mutations count, never the
        # ``T storage d = stateVar`` binding itself.
        pats = (
            r"\b" + esc + r"\s*\[[^\]]*\]\s*(?:\.\s*[A-Za-z_]\w*\s*)?" + _WRITE_OP,
            r"\b" + esc + r"\s*\.\s*[A-Za-z_]\w*\s*(?:\[[^\]]*\])?\s*" + _WRITE_OP,
            r"\bdelete\s+" + esc + r"\s*[.\[]",
            r"\b" + esc + r"\s*\.\s*push\s*\(",
        )
    else:
        pats = (
            r"\b" + esc + r"\s*(?:\[[^\]]*\])*\s*(?:\.\s*[A-Za-z_]\w*\s*)?" + _WRITE_OP,
            r"\bdelete\s+" + esc + r"\b",
            r"\b" + esc + r"\s*(?:\[[^\]]*\])*\s*\.\s*push\s*\(",
        )
    best = None
    for p in pats:
        m = re.search(p, body)
        if m and (best is None or m.start() < best):
            best = m.start()
    return best


def write_offsets(body: str, state_var_names) -> dict:
    """Return ``state_var -> earliest write offset`` (alias-aware).

    Resolves storage-pointer aliases so ``d.active = false`` (where
    ``Deposit storage d = deposits[key]``) is attributed to ``deposits`` without
    mistaking the alias binding for a write. Misses are acceptable; fabricated
    writes are not.
    """
    offs = {}
    for sv in state_var_names:
        best = _earliest_write(body, sv, member_required=False)
        if best is not None:
            offs[sv] = best
    for local, sv in storage_alias_map(body, state_var_names).items():
        best = _earliest_write(body, local, member_required=True)
        if best is not None and (sv not in offs or best < offs[sv]):
            offs[sv] = best
    return offs


def _analyze_function_body(fn: M.FunctionSemantic, body: str, base_line: int,
                           state_var_names: set, calldata_param_names: set) -> None:
    # Storage writes (alias-aware) and reads.
    woffs = write_offsets(body, state_var_names)
    writes = set(woffs.keys())
    alias = storage_alias_map(body, state_var_names)
    alias_by_sv = {}
    for local, sv in alias.items():
        alias_by_sv.setdefault(sv, []).append(local)
    reads = set()
    for var in state_var_names:
        names = [var] + alias_by_sv.get(var, [])
        if any(re.search(r"\b" + re.escape(nm) + r"\b", body) for nm in names):
            reads.add(var)
    fn.storage_writes = sorted(writes)
    fn.storage_reads = sorted(reads - writes)

    # Events.
    fn.events_emitted = sorted({m.group(1) for m in re.finditer(r"\bemit\s+([A-Za-z_]\w*)\s*\(", body)})

    # Transfers.
    transfers = set()
    for m in re.finditer(r"\.\s*(safeTransferFrom|safeTransfer|transferFrom|transfer|sendValue|safeMint|mint|burn|burnFrom)\s*\(", body):
        transfers.add(m.group(1))
    if re.search(r"\.\s*call\s*\{\s*value", body):
        transfers.add("call{value}")
    fn.transfers = sorted(transfers)

    # Low-level calls.
    low = set()
    for kind in ("delegatecall", "staticcall", "call"):
        if re.search(r"\.\s*" + kind + r"\s*[({]", body):
            low.add(kind)
    fn.low_level_calls = sorted(low)

    # External / interface calls (member + cast-then-call).
    ext = set()
    for m in re.finditer(r"\b([A-Za-z_]\w*)\s*\.\s*([a-z_]\w*)\s*\(", body):
        ident, method = m.group(1), m.group(2)
        if ident in ("msg", "block", "tx", "abi", "address", "type", "super", "this", "string", "bytes"):
            continue
        if method in ("push", "pop", "length"):
            continue
        ext.add(f"{ident}.{method}")
    for m in re.finditer(r"\b([A-Z]\w*)\s*\([^;{}]*?\)\s*\.\s*([a-z_]\w*)\s*\(", body):
        ext.add(f"{m.group(1)}.{m.group(2)}")
    fn.external_calls = sorted(ext)

    # Internal calls (bare name() where name is not a keyword); resolved later.
    internal = set()
    for m in re.finditer(r"(^|[^.\w])([a-z_]\w*)\s*\(", body):
        name = m.group(2)
        if name in _TYPE_KEYWORDS or name in ("require", "assert", "revert", "emit",
                                              "keccak256", "sha256", "ecrecover", "abi",
                                              "return", "address", "payable", "selfdestruct"):
            continue
        if name == fn.name:
            continue
        internal.add(name)
    fn.internal_calls = sorted(internal)

    # Calldata field access (param.field, param[i].field, param[i]).
    cfields = set()
    for p in calldata_param_names:
        for m in re.finditer(re.escape(p) + r"\s*(\[[^\]]*\])?\s*\.\s*([A-Za-z_]\w*)", body):
            cfields.add(f"{p}{m.group(1) or ''}.{m.group(2)}")
        if re.search(re.escape(p) + r"\s*\[[^\]]*\]", body):
            cfields.add(f"{p}[]")
    fn.calldata_fields = sorted(cfields)

    # msg.sender / msg.value.
    fn.uses_msg_sender = bool(re.search(r"\bmsg\.sender\b", body))
    fn.uses_msg_value = bool(re.search(r"\bmsg\.value\b", body))

    # Role gates from modifiers + body.
    gates = [mod for mod in fn.modifiers if _ROLE_MOD_HINT.search(mod)]
    if _ROLE_BODY_RE.search(body):
        gates.append("require(role/owner)")
    fn.role_gates = sorted(set(gates))


def _parse_contract(name, kind, inherit_clause, body, body_start_line, file_rel,
                    result: ParseResult) -> M.ContractSemantic:
    inheritance = []
    if inherit_clause:
        clause = inherit_clause.split("is", 1)[-1]
        for base in _split_top_level(clause):
            base_name = base.split("(")[0].strip()
            if base_name:
                inheritance.append(base_name)

    structs = []
    for sm in _STRUCT_RE.finditer(body):
        sname = sm.group(1)
        ob = body.find("{", sm.start())
        fields = []
        if ob >= 0:
            ce = match_delim(body, ob, "{", "}")
            for stmt in body[ob + 1:ce].split(";"):
                toks = stmt.split()
                if len(toks) >= 2:
                    fields.append({"name": toks[-1], "type": " ".join(toks[:-1])})
        structs.append({"name": sname, "fields": fields})
    enums = [m.group(1) for m in _ENUM_RE.finditer(body)]
    events = [m.group(1) for m in _EVENT_RE.finditer(body)]
    modifiers_defined = []

    # Locate functions/modifiers; collect their body spans to compute residue.
    fns: list = []
    spans: list = []  # (start, end) of member bodies to blank for statevar residue
    for m in _FUNC_RE.finditer(body):
        keyword = m.group(1)
        fname = m.group(2) or ("constructor" if keyword == "constructor" else "")
        paren_open = body.find("(", m.start())
        paren_close = match_delim(body, paren_open, "(", ")")
        params_raw = body[paren_open + 1:paren_close]
        # attrs run from after params to the next top-level { or ;
        j = paren_close + 1
        depth = 0
        attrs_end = len(body)
        body_open = -1
        while j < len(body):
            c = body[j]
            if c == "(":
                depth += 1
            elif c == ")":
                depth -= 1
            elif depth == 0 and c == "{":
                attrs_end = j; body_open = j; break
            elif depth == 0 and c == ";":
                attrs_end = j; break
            j += 1
        attrs = body[paren_close + 1:attrs_end]
        if keyword == "modifier":
            if fname:
                modifiers_defined.append(fname)
            if body_open >= 0:
                spans.append((body_open, match_delim(body, body_open, "{", "}")))
            continue
        if not fname:
            continue
        vis_m = _VIS_RE.search(attrs)
        mut_m = _MUT_RE.search(attrs)
        fn = M.FunctionSemantic(
            contract=name, name=fname,
            visibility=(vis_m.group(1) if vis_m else ("internal" if keyword == "constructor" else "public")),
            mutability=(mut_m.group(1) if mut_m else ""),
            parameters=_parse_params(params_raw),
            returns=_parse_returns(attrs),
            modifiers=_parse_modifiers(attrs),
            line_start=body_start_line + line_of(body, m.start()) - 1,
            confidence=M.MEDIUM,
        )
        if body_open >= 0:
            close = match_delim(body, body_open, "{", "}")
            fn_body = body[body_open + 1:close]
            fn.line_end = body_start_line + line_of(body, close) - 1
            spans.append((body_open, close))
            fns.append((fn, fn_body, body_start_line + line_of(body, body_open) - 1))
        else:
            fn.line_end = fn.line_start
            fn.confidence = M.LOW
            fn.warnings.append("declaration only (no body)")
            fns.append((fn, "", fn.line_start))

    # Residue = contract body with member bodies blanked -> state variables.
    residue_chars = list(body)
    for s, e in spans:
        for k in range(s, min(e + 1, len(residue_chars))):
            if residue_chars[k] != "\n":
                residue_chars[k] = " "
    # Also blank struct/enum bodies.
    for rx in (_STRUCT_RE, _ENUM_RE):
        for m in rx.finditer(body):
            ob = body.find("{", m.start())
            if ob >= 0:
                ce = match_delim(body, ob, "{", "}")
                for k in range(ob, min(ce + 1, len(residue_chars))):
                    if residue_chars[k] != "\n":
                        residue_chars[k] = " "
    residue = "".join(residue_chars)
    state_vars = _detect_statevars(residue, body_start_line)
    state_var_names = {sv.name for sv in state_vars}

    func_names = {fn.name for fn, _, _ in fns}
    result.func_names_by_contract[name] = func_names

    final_fns = []
    for fn, fn_body, bstart in fns:
        calldata_param_names = {p.name for p in fn.parameters if p.location == "calldata" and p.name}
        if fn_body:
            _analyze_function_body(fn, fn_body, bstart, state_var_names, calldata_param_names)
        final_fns.append(fn)
        result.bodies[fn.qualified_name] = FunctionBody(
            qualified=fn.qualified_name, contract=name, file=file_rel, name=fn.name,
            body=fn_body, body_start_line=bstart,
            calldata_params=[p for p in fn.parameters if p.location == "calldata" and p.name],
            state_vars=state_vars,
        )

    kind_map = {"contract": M.KIND_CONTRACT, "interface": M.KIND_INTERFACE, "library": M.KIND_LIBRARY}
    csem = M.ContractSemantic(
        name=name, file=file_rel,
        line_start=body_start_line, line_end=body_start_line + line_of(body, len(body) - 1) - 1,
        kind=kind_map.get(kind, M.KIND_CONTRACT),
        inheritance=inheritance, state_variables=state_vars, functions=final_fns,
        modifiers=modifiers_defined, events=events, structs=structs, enums=enums,
        confidence=M.MEDIUM,
    )
    if kind == "interface":
        csem.kind = M.KIND_INTERFACE
    return csem


def parse_sources(sources: list) -> ParseResult:
    """Parse a list of ``SourceFile`` into a ``ParseResult`` (fallback mode)."""
    result = ParseResult()
    for sf in sources:
        blanked = blank_noise(sf.text)
        for m in _CONTRACT_RE.finditer(blanked):
            abstract, kind, cname, inherit = m.group(1), m.group(2), m.group(3), m.group(4)
            brace = blanked.find("{", m.start())
            if brace < 0:
                continue
            close = match_delim(blanked, brace, "{", "}")
            body = blanked[brace + 1:close]
            body_start_line = line_of(blanked, brace)
            csem = _parse_contract(cname, kind, inherit, body, body_start_line, sf.rel, result)
            if abstract:
                csem.kind = M.KIND_ABSTRACT
            result.contracts.append(csem)
    if not result.contracts:
        result.warnings.append("fallback parser found no contracts")
    return result
