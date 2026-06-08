"""Data model for the v7 Scope-Aware Orchestration + Evidence Judge layer.

v4 maps value flow. v5 prioritizes likely blind spots. v6 classifies evidence and
unresolved interactions. v7 turns a contest/audit/program scope note into review
lanes, scope tasks, evidence requirements, and report filters.

Everything here is heuristic and local/static. A review lane is a planning
artifact, not a finding. A scope task is a research instruction, not an exploit
instruction. Evidence quality is not vulnerability validity. Candidate-with-evidence
is not a confirmed vulnerability. Task priority is not severity. Human review is
required for every conclusion.
"""
from __future__ import annotations

from dataclasses import dataclass, field

SCHEMA_VERSION = "1.0.0"

# --- Artifact kinds -------------------------------------------------------
KIND_SCOPE_MAP = "scope-map"
KIND_SCOPE_LANES = "scope-lanes"
KIND_SCOPE_TASKS = "scope-tasks"
KIND_SCOPE_PACK_MANIFEST = "scope-pack-manifest"
KIND_EVIDENCE_JUDGE = "evidence-judge"
KIND_REPORT_FILTER = "report-filter"

# --- Priority (heuristic review order, never severity) --------------------
PRIORITY_VERY_HIGH = "very-high"
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_MONITOR = "monitor"
PRIORITIES = (PRIORITY_VERY_HIGH, PRIORITY_HIGH, PRIORITY_MEDIUM, PRIORITY_MONITOR)
_PRIORITY_ORDER = {PRIORITY_VERY_HIGH: 0, PRIORITY_HIGH: 1, PRIORITY_MEDIUM: 2, PRIORITY_MONITOR: 3}

# --- Evidence quality labels (exactly six) --------------------------------
QUALITY_STRONG = "strong"
QUALITY_MEDIUM = "medium"
QUALITY_WEAK = "weak"
QUALITY_INVALID = "invalid"
QUALITY_INSUFFICIENT = "insufficient"
QUALITY_UNKNOWN = "unknown"
EVIDENCE_QUALITIES = (
    QUALITY_STRONG, QUALITY_MEDIUM, QUALITY_WEAK,
    QUALITY_INVALID, QUALITY_INSUFFICIENT, QUALITY_UNKNOWN,
)

# --- Judgment labels (exactly eleven) -------------------------------------
JUDGE_REJECTED_STRONG = "rejected-with-strong-evidence"
JUDGE_REJECTED_MEDIUM = "rejected-with-medium-evidence"
JUDGE_CANDIDATE = "candidate-with-evidence"
JUDGE_INSUFFICIENT = "insufficient-evidence"
JUDGE_INVALID = "invalid-test"
JUDGE_LIKELY_KNOWN = "likely-known-issue"
JUDGE_LIKELY_ACCEPTED = "likely-accepted-risk"
JUDGE_LIKELY_TRUSTED_ROLE = "likely-trusted-role-assumption"
JUDGE_LIKELY_OUT_OF_SCOPE = "likely-out-of-scope"
JUDGE_LIKELY_LOW_ONLY = "likely-low-only"
JUDGE_NEEDS_HUMAN = "needs-human-review"
JUDGMENTS = (
    JUDGE_REJECTED_STRONG, JUDGE_REJECTED_MEDIUM, JUDGE_CANDIDATE, JUDGE_INSUFFICIENT,
    JUDGE_INVALID, JUDGE_LIKELY_KNOWN, JUDGE_LIKELY_ACCEPTED, JUDGE_LIKELY_TRUSTED_ROLE,
    JUDGE_LIKELY_OUT_OF_SCOPE, JUDGE_LIKELY_LOW_ONLY, JUDGE_NEEDS_HUMAN,
)

# --- Report-candidate classifications (exactly ten) -----------------------
CLASS_POTENTIALLY_REPORTABLE = "potentially-reportable"
CLASS_NEEDS_MORE_EVIDENCE = "needs-more-evidence"
CLASS_LIKELY_KNOWN = "likely-known-issue"
CLASS_LIKELY_ACCEPTED = "likely-accepted-risk"
CLASS_LIKELY_TRUSTED_ROLE = "likely-trusted-role-assumption"
CLASS_LIKELY_OUT_OF_SCOPE = "likely-out-of-scope"
CLASS_LIKELY_LOW_ONLY = "likely-low-only"
CLASS_DUPLICATE_PRONE = "duplicate-prone"
CLASS_NOT_A_FINDING = "not-a-finding"
CLASS_NEEDS_HUMAN = "needs-human-review"
CLASSIFICATIONS = (
    CLASS_POTENTIALLY_REPORTABLE, CLASS_NEEDS_MORE_EVIDENCE, CLASS_LIKELY_KNOWN,
    CLASS_LIKELY_ACCEPTED, CLASS_LIKELY_TRUSTED_ROLE, CLASS_LIKELY_OUT_OF_SCOPE,
    CLASS_LIKELY_LOW_ONLY, CLASS_DUPLICATE_PRONE, CLASS_NOT_A_FINDING, CLASS_NEEDS_HUMAN,
)


def priority_rank(label: str) -> int:
    return _PRIORITY_ORDER.get(label, 4)


# --------------------------------------------------------------------------
# Canonical generic review lanes (LANE-01 .. LANE-14)
# --------------------------------------------------------------------------
@dataclass(frozen=True)
class LaneDef:
    lane_id: str
    lane_name: str
    slug: str
    keywords: tuple[str, ...]
    why_it_matters: str
    what_can_be_valid: str
    what_is_likely_invalid: str
    known_accepted_to_avoid: str
    first_hypotheses: tuple[str, ...]
    required_evidence: tuple[str, ...]
    stop_condition: str
    task_categories: tuple[str, ...]


# Task category keys (used to instantiate concrete tasks for a lane).
TC_AUTH_BYPASS = "authorization-bypass"
TC_REPLAY = "replay-nonce-deadline"
TC_SIG_BINDING = "signature-purpose-binding"
TC_ORACLE = "oracle-stale-deviation-decimals"
TC_SHARE_PRICE = "share-price-inflation-deflation"
TC_VIRTUAL_ACCT = "virtual-accounting-desync"
TC_REWARDS = "rewards-vesting-mismatch"
TC_WITHDRAW_AMOUNT = "withdrawal-amount-mismatch"
TC_CLAIM_OWNERSHIP = "transferable-claim-ownership-edge"
TC_COMPLIANCE = "compliance-bypass"
TC_CROSSCHAIN = "cross-chain-stuck-refund-quarantine-edge"
TC_ADAPTER_AMOUNT = "adapter-amount-mismatch"
TC_CALL_ORDERING = "external-call-ordering"
TC_LOOP_GRIEF = "unbounded-loop-griefing"
TC_ADMIN_BOUNDARY = "admin-role-boundary-exceedance"
TC_ERC_COMPLIANCE = "erc-standard-compliance-medium-high-only"
TC_FEE_SLIPPAGE = "fee-slippage-mismatch-user-loss"
TC_PREVIEW_ACTUAL = "preview-vs-actual-execution-mismatch"
TC_BURN_CLAIM = "burn-to-claim-mismatch"
TC_CAPACITY_DEBT = "capacity-debt-accounting-mismatch"
TC_BLOCKLIST_TIMING = "blocklist-freeze-timing-interaction"

TASK_CATEGORIES = (
    TC_AUTH_BYPASS, TC_REPLAY, TC_SIG_BINDING, TC_ORACLE, TC_SHARE_PRICE, TC_VIRTUAL_ACCT,
    TC_REWARDS, TC_WITHDRAW_AMOUNT, TC_CLAIM_OWNERSHIP, TC_COMPLIANCE, TC_CROSSCHAIN,
    TC_ADAPTER_AMOUNT, TC_CALL_ORDERING, TC_LOOP_GRIEF, TC_ADMIN_BOUNDARY, TC_ERC_COMPLIANCE,
    TC_FEE_SLIPPAGE, TC_PREVIEW_ACTUAL, TC_BURN_CLAIM, TC_CAPACITY_DEBT, TC_BLOCKLIST_TIMING,
)

_COMMON_INVALID = (
    "The test does not call the target function.",
    "The test has no assertion, or only asserts that the call did not revert.",
    "The test mocks away the actual risk instead of exercising it.",
    "The test relies on a trusted-role mistake that the scope marks invalid.",
    "The test reproduces a known or accepted issue from the scope.",
)

LANE_DEFS: tuple[LaneDef, ...] = (
    LaneDef(
        "LANE-01", "Mint / Redeem / Value Flow", "mint-redeem-value-flow",
        ("mint", "redeem", "deposit", "withdraw", "issue", "burn", "value entry", "value exit", "value-in", "value-out"),
        "Mint and redeem are the primary value entry and exit paths; an accounting or authorization gap here moves user funds.",
        "A caller mints or redeems more value than entitled, or accounting desyncs from backing on a value path.",
        "A pure happy-path mint/redeem with no rounding edge, or a path gated only by a trusted role acting honestly.",
        "Known rounding dust the sponsor already documents, and trusted-minter assumptions the scope marks valid.",
        ("Can a caller redeem more backing than they minted (round-trip conservation)?",
         "Does a 6-decimal vs 18-decimal conversion let mint/redeem overstate value?"),
        ("pre/post balance and supply delta on both legs", "round-trip conservation at first/last/dust amounts"),
        "Mint then redeem conserves backing for first, last, and dust amounts, or fails in a documented way.",
        (TC_WITHDRAW_AMOUNT, TC_VIRTUAL_ACCT, TC_FEE_SLIPPAGE),
    ),
    LaneDef(
        "LANE-02", "Vault / Share Accounting", "vault-share-accounting",
        ("vault", "share", "asset", "erc4626", "convertto", "preview", "totalassets", "totalsupply", "exchange rate"),
        "Share/asset conversion governs every depositor's value; rounding or donation skew silently transfers value between users.",
        "A donation or first-deposit inflates share price so a later depositor loses value, or preview disagrees with execution.",
        "A single nominal deposit amount with no rounding or donation edge.",
        "First-deposit rounding the sponsor documents as accepted, if the scope says so.",
        ("Can a first-deposit/donation inflate share price and steal a later depositor's value?",
         "Does previewDeposit/previewRedeem equal the realised amount at the same state?"),
        ("first-deposit / donation case", "preview vs realised comparison", "rounding direction at first/last/dust"),
        "A donation cannot let an attacker capture later depositors' value, and preview equals realised execution.",
        (TC_SHARE_PRICE, TC_PREVIEW_ACTUAL, TC_VIRTUAL_ACCT),
    ),
    LaneDef(
        "LANE-03", "Rewards / Vesting", "rewards-vesting",
        ("reward", "vest", "vesting", "distribut", "accrue", "yield", "emission", "stake"),
        "Reward and vesting math controls how much value each participant can claim; an accrual bug overpays from the pool.",
        "A participant claims more than accrued, or a vesting schedule releases early or double-counts.",
        "A claim test with no reconciliation against accrued yield or the reward pool.",
        "Reward dust and rounding the sponsor accepts; trusted distributor cadence assumptions if marked valid.",
        ("Can a participant claim more reward than accrued for their stake and time?",
         "Can vesting be re-triggered or double-claimed across a schedule boundary?"),
        ("pre/post reward pool delta", "claim vs accrued reconciliation", "double-claim negative path"),
        "Total claims never exceed funded/accrued rewards, and a schedule cannot be double-claimed.",
        (TC_REWARDS, TC_BURN_CLAIM, TC_CALL_ORDERING),
    ),
    LaneDef(
        "LANE-04", "Withdrawal Queue / Claim NFT", "withdrawal-queue-claim-nft",
        ("queue", "claim", "withdrawalnft", "claimnft", "ticket", "request", "settle", "express", "fulfill"),
        "A withdrawal queue or claim NFT records a deferred right to value; a mismatch lets a holder over-claim or double-claim.",
        "A claim pays more than funded, a consumed claim is claimed twice, or a transferred claim NFT mis-binds ownership.",
        "A claim test that never marks the claim consumed or never checks a second claim reverts.",
        "Queue ordering or delay windows the sponsor documents as intended.",
        ("Can a holder claim more than the queue funded for them?",
         "Can a transferred claim NFT be claimed by both the old and new owner?"),
        ("total claims vs funded amount", "consumed-flag / second-claim revert", "claim-NFT ownership binding"),
        "The queue cannot pay more than funded and a consumed or transferred claim cannot be claimed twice.",
        (TC_WITHDRAW_AMOUNT, TC_CLAIM_OWNERSHIP, TC_BURN_CLAIM, TC_CAPACITY_DEBT),
    ),
    LaneDef(
        "LANE-05", "Oracle / Pricing / Decimals", "oracle-pricing-decimals",
        ("oracle", "price", "latestrounddata", "decimals", "stale", "deviation", "sequencer", "feed", "valuation", "rate"),
        "Price, staleness, deviation, and decimal conversion feed solvency math; a bad input overstates assets or collateral.",
        "A stale, zero, deviated, or wrong-decimals price makes accounting overstate value or skip a guard.",
        "A single nominal price with no stale/zero/deviation/decimals edge.",
        "Feed latency the sponsor documents as accepted; trusted off-chain oracle operator assumptions if marked valid.",
        ("Does a stale or zero price let accounting overstate assets or pass a solvency check?",
         "Does a 6-to-18 decimal conversion mis-scale the valuation?"),
        ("zero / stale / deviated price cases", "decimals conversion boundary", "sequencer-uptime gate if present"),
        "Zero, stale, deviated, and wrong-decimals prices behave as documented at the boundary.",
        (TC_ORACLE, TC_SHARE_PRICE, TC_CAPACITY_DEBT),
    ),
    LaneDef(
        "LANE-06", "Authorization / Signatures / Replay", "authorization-signatures-replay",
        ("onlyowner", "role", "auth", "permit", "ecrecover", "eip712", "signature", "signed", "nonce", "deadline", "replay", "chainid"),
        "Authorization, signature binding, and replay protection gate every privileged or signed action; a gap lets the wrong caller act.",
        "An unauthorized caller drives a gated path, or a signature is replayed, reused cross-chain, or rebound to new fields.",
        "A positive-path test that never checks the unauthorized caller or replayed signature reverts.",
        "Trusted signer/role behaviour the scope explicitly marks valid; documented permit edge cases.",
        ("Does an unauthorized caller revert on every gated path (negative path)?",
         "Can a signed message be replayed (used nonce), expired (deadline), or reused across chainId?"),
        ("unauthorized-caller negative path", "used-nonce replay rejected", "expired-deadline rejected", "signed-field mutation rejected"),
        "Every gated path rejects the unauthorized caller, and a replayed/expired/rebound signature is rejected.",
        (TC_AUTH_BYPASS, TC_REPLAY, TC_SIG_BINDING),
    ),
    LaneDef(
        "LANE-07", "Compliance / Freeze / Sanctions", "compliance-freeze-sanctions",
        ("compliance", "blocklist", "blacklist", "freeze", "frozen", "sanction", "allowlist", "kyc", "denylist"),
        "Compliance gates (blocklist/freeze/sanctions) must hold across every value path; a bypass moves value for a blocked party.",
        "A blocked or frozen party still sends or receives value through some path the gate does not cover.",
        "A blocklist test that checks only one party (sender) or only one contract.",
        "Compliance enforcement the sponsor documents as off-chain or out-of-scope, if the scope says so.",
        ("Can a blocked party still receive value through the vault, NFT, or bridge path?",
         "Is the freeze checked on both sender and recipient on every value path?"),
        ("blocklist gate on sender and recipient", "freeze enforced across token/vault/NFT/bridge", "timing of freeze vs in-flight claim"),
        "A blocked or frozen party cannot send or receive on any value path the scope marks in-scope.",
        (TC_COMPLIANCE, TC_BLOCKLIST_TIMING, TC_CALL_ORDERING),
    ),
    LaneDef(
        "LANE-08", "Cross-Chain / Adapter / Compose", "cross-chain-adapter-compose",
        ("crosschain", "cross-chain", "layerzero", "oft", "bridge", "compose", "lzreceive", "endpoint", "refund", "quarantine", "message"),
        "Cross-chain send/compose paths can strand value or desync state between chains; refund/quarantine edges are easy to get wrong.",
        "A cross-chain transfer is stuck without refund, double-credited, or a compose step desyncs compliance/accounting across chains.",
        "A test of only the happy send path with no failed-delivery, refund, or quarantine case.",
        "Bridge liveness and external messaging-layer trust the sponsor documents as accepted.",
        ("Can a failed cross-chain delivery strand value with no refund or quarantine path?",
         "Does a compose step let compliance or accounting desync between source and destination?"),
        ("failed-delivery refund/quarantine path", "no double-credit on retry", "compliance preserved across compose"),
        "A failed cross-chain step refunds or quarantines value and cannot double-credit or bypass compliance.",
        (TC_CROSSCHAIN, TC_COMPLIANCE, TC_CALL_ORDERING),
    ),
    LaneDef(
        "LANE-09", "External Integration / Adapter", "external-integration-adapter",
        ("adapter", "connector", "strategy", "integration", "aave", "compound", "external protocol", "farm", "wrapper"),
        "Adapters reconcile core accounting with an external protocol; a withdraw-amount or exchange-rate mismatch corrupts core state.",
        "An adapter reports or withdraws a different amount than core accounting expects, or a failed external call desyncs state.",
        "A test where the external protocol is fully mocked so the real reconciliation never runs.",
        "External protocol solvency/liveness the sponsor documents as a trusted dependency.",
        ("Does the adapter withdraw exactly what core accounting requested (strict amount)?",
         "Does a failed external mint/redeem leave core accounting consistent?"),
        ("adapter amount vs core request", "exchange-rate / decimals reconciliation", "failed external call atomicity"),
        "Adapter-reported and withdrawn amounts reconcile with core accounting, even on a failed external call.",
        (TC_ADAPTER_AMOUNT, TC_CAPACITY_DEBT, TC_CALL_ORDERING),
    ),
    LaneDef(
        "LANE-10", "Admin / Emergency / Upgrade", "admin-emergency-upgrade",
        ("admin", "owner", "setter", "pause", "emergency", "shutdown", "rescue", "sweep", "upgrade", "uups", "implementation", "timelock", "initialize"),
        "Admin, emergency, and upgrade controls define the trust model; a boundary that exceeds the documented power can move or trap value.",
        "An admin/emergency action moves value outside the documented flow, or an upgrade re-opens initialization or skips a timelock.",
        "A test of an admin action that never checks an unauthorized caller reverts or never checks the documented bound.",
        "Centralization the scope explicitly accepts; trusted admin actions the scope marks valid.",
        ("Does an admin/emergency function stay within its documented value-movement bound?",
         "Can an upgrade re-initialize state or bypass the documented timelock/role?"),
        ("unauthorized admin negative path", "emergency-effect scope bound", "initialize-once across upgrade"),
        "Admin/emergency/upgrade actions stay within the documented trust model and cannot re-open initialization.",
        (TC_ADMIN_BOUNDARY, TC_AUTH_BYPASS, TC_CALL_ORDERING),
    ),
    LaneDef(
        "LANE-11", "Periphery / Callback / Batch", "periphery-callback-batch",
        ("router", "periphery", "callback", "hook", "multicall", "batch", "bundle", "delegatecall", "flash", "reentr"),
        "Periphery routes, callbacks, and batch calls can bypass core invariants or observe mid-update state; equivalence is easy to assume.",
        "A periphery/batch path produces different core accounting than the direct call, or a callback re-enters mid-update.",
        "A test that exercises only the direct path and never compares it to the periphery/batch path.",
        "Documented periphery conveniences the sponsor marks equivalent by design.",
        ("Does the periphery/batch path produce the same core accounting as the direct call?",
         "Can a callback observe or mutate mid-update accounting (reentrancy)?"),
        ("periphery vs direct equivalence", "callback caller check", "reentrancy negative path"),
        "The periphery/batch path matches direct-call accounting and callbacks cannot observe mid-update state.",
        (TC_CALL_ORDERING, TC_PREVIEW_ACTUAL, TC_FEE_SLIPPAGE),
    ),
    LaneDef(
        "LANE-12", "Gas / Unbounded Loop / Griefing", "gas-unbounded-loop-griefing",
        ("loop", "for (", "while (", "array", "unbounded", "batch", "iterate", "gas", "length"),
        "An unbounded loop over user-growable data can be pushed past the block gas limit, bricking a path (a griefing/DoS impact).",
        "An attacker grows an array so a core path always reverts on gas, locking funds or blocking other users (Medium/High only).",
        "A loop test that uses a tiny fixed array and never grows it toward the gas limit.",
        "Array bounds the sponsor documents as gas-limited and accepted.",
        ("Can an attacker grow an iterated array until a core path reverts on gas?",
         "Does any value path depend on a loop with no upper bound?"),
        ("array growth toward gas limit", "core path still callable at scale", "impact is fund lock / DoS, not just cost"),
        "Every value-relevant loop is bounded or the unbounded case is shown to be Medium/High impact, not just gas cost.",
        (TC_LOOP_GRIEF, TC_CALL_ORDERING),
    ),
    LaneDef(
        "LANE-13", "ERC Standard Compliance", "erc-standard-compliance",
        ("erc20", "erc721", "erc1155", "erc4626", "erc2612", "standard", "interface", "spec", "compliant"),
        "An ERC standard deviation only matters for a contest when it causes Medium/High impact (value loss / lock), not a pure spec nit.",
        "A standard deviation (return value, hook, decimals, approval) causes a value-loss or fund-lock path, not just a spec mismatch.",
        "A test that flags a spec deviation with no Medium/High impact path attached.",
        "Spec deviations the sponsor documents as intentional and low-only.",
        ("Does an ERC deviation here create a value-loss or fund-lock path (not just a spec nit)?",
         "Does an integrator that follows the standard break against this implementation?"),
        ("standard behaviour vs implementation", "Medium/High impact path attached", "integrator-follows-spec negative case"),
        "Any ERC deviation is tied to a concrete Medium/High impact path, or it is documented as low-only and dropped.",
        (TC_ERC_COMPLIANCE, TC_PREVIEW_ACTUAL),
    ),
    LaneDef(
        "LANE-14", "Token Integration / Non-standard ERC20", "token-integration-nonstandard-erc20",
        ("safeerc20", "transfer", "transferfrom", "approve", "fee-on-transfer", "feeontransfer", "rebasing", "returnvalue", "usdt", "weth", "token"),
        "Non-standard ERC20 behaviour (missing return value, fee-on-transfer, rebasing, blocklist) breaks integrations that assume the standard.",
        "A non-standard token (no return value, fee-on-transfer, rebasing) makes accounting over/under-count or a path revert.",
        "A test that only uses a standard mock token and never exercises non-standard behaviour.",
        "Token quirks the sponsor documents as out-of-scope or accepted for the integrated token set.",
        ("Does a missing-return-value token (e.g. USDT-like) break a transfer path?",
         "Does a fee-on-transfer token make the vault over-credit shares?"),
        ("missing-return-value token", "fee-on-transfer accounting delta", "blocklist token on a value path"),
        "The integration handles the documented non-standard token behaviours, or the gap is shown to be Medium/High impact.",
        (TC_VIRTUAL_ACCT, TC_FEE_SLIPPAGE, TC_COMPLIANCE),
    ),
)

LANE_BY_ID = {ld.lane_id: ld for ld in LANE_DEFS}
LANE_NAMES = tuple(ld.lane_name for ld in LANE_DEFS)


@dataclass
class ScopeData:
    """Structured rules parsed from a markdown scope note (or inferred)."""

    scope_file_used: bool = False
    scope_file_path: str = ""
    summary: str = ""
    in_scope: list[str] = field(default_factory=list)
    out_of_scope: list[str] = field(default_factory=list)
    severity_conditions: list[str] = field(default_factory=list)
    trusted_roles: list[str] = field(default_factory=list)
    trusted_integrations: list[str] = field(default_factory=list)
    known_issues: list[str] = field(default_factory=list)
    accepted_risks: list[str] = field(default_factory=list)
    prior_audit_notes: list[str] = field(default_factory=list)
    changed_since_audit: list[str] = field(default_factory=list)
    design_choices: list[str] = field(default_factory=list)
    invariants: list[str] = field(default_factory=list)
    off_chain_assumptions: list[str] = field(default_factory=list)
    admin_assumptions: list[str] = field(default_factory=list)
    external_dependency_assumptions: list[str] = field(default_factory=list)
    array_gas_limits: list[str] = field(default_factory=list)
    eip_expectations: list[str] = field(default_factory=list)
    compliance_expectations: list[str] = field(default_factory=list)
    focus_areas: list[str] = field(default_factory=list)
    invalid_patterns: list[str] = field(default_factory=list)
    low_only_patterns: list[str] = field(default_factory=list)
    report_candidate_requirements: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        from dataclasses import asdict

        return asdict(self)

    def haystack(self) -> str:
        """Lowercased blob of all scope text for keyword matching."""
        bits: list[str] = [self.summary]
        for name in (
            "in_scope", "focus_areas", "invariants", "compliance_expectations",
            "eip_expectations", "design_choices", "changed_since_audit",
        ):
            bits.extend(getattr(self, name))
        return "\n".join(bits).lower()
