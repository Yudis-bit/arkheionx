"""DeFi economic entity models and detection rules (Layer 2).

Recognizes economic objects (Asset, Share, Loan, Debt, Collateral, Tranche,
Lender, Borrower, Deposit, Refund, Fee, Vault, Adapter, OraclePrice, ...) from
the semantic map, rather than treating everything as an undifferentiated
variable. Generic: detection is name/shape driven, never protocol-specific.
"""
from __future__ import annotations

import dataclasses
import re
from dataclasses import dataclass, field

LOW, MEDIUM, HIGH = "LOW", "MEDIUM", "HIGH"

# Entity types.
ASSET = "Asset"
TOKEN = "Token"
SHARE = "Share"
VAULT = "Vault"
LOAN = "Loan"
DEBT = "Debt"
COLLATERAL = "Collateral"
POSITION = "Position"
DEPOSIT = "Deposit"
WITHDRAWAL = "Withdrawal"
CLAIM = "Claim"
LENDER = "Lender"
BORROWER = "Borrower"
TRANCHE = "Tranche"
PRINCIPAL = "Principal"
INTEREST = "Interest"
REPAYMENT = "Repayment"
PREPAYMENT = "Prepayment"
REFUND = "Refund"
FEE = "Fee"
REWARD = "Reward"
ORACLE_PRICE = "OraclePrice"
EXCHANGE_RATE = "ExchangeRate"
ADAPTER = "Adapter"
ROUTER = "Router"
WRAPPER = "Wrapper"
REDEMPTION = "Redemption"
QUEUE = "Queue"
GOVERNANCE_POWER = "GovernancePower"
CROSS_CHAIN_SUPPLY = "CrossChainSupply"

# Value direction for an entity (relative to the protocol).
DIR_IN = "in"
DIR_OUT = "out"
DIR_IN_OUT = "in_out"
DIR_INTERNAL = "internal"
DIR_NONE = "none"

# Baseline value direction per entity type.
_DIRECTION = {
    ASSET: DIR_IN_OUT, TOKEN: DIR_IN_OUT, SHARE: DIR_INTERNAL, VAULT: DIR_IN_OUT,
    LOAN: DIR_INTERNAL, DEBT: DIR_INTERNAL, COLLATERAL: DIR_INTERNAL, POSITION: DIR_INTERNAL,
    DEPOSIT: DIR_IN, WITHDRAWAL: DIR_OUT, CLAIM: DIR_OUT, LENDER: DIR_NONE, BORROWER: DIR_NONE,
    TRANCHE: DIR_INTERNAL, PRINCIPAL: DIR_INTERNAL, INTEREST: DIR_INTERNAL, REPAYMENT: DIR_IN,
    PREPAYMENT: DIR_IN, REFUND: DIR_OUT, FEE: DIR_OUT, REWARD: DIR_OUT, ORACLE_PRICE: DIR_NONE,
    EXCHANGE_RATE: DIR_NONE, ADAPTER: DIR_IN_OUT, ROUTER: DIR_IN_OUT, WRAPPER: DIR_INTERNAL,
    REDEMPTION: DIR_OUT, QUEUE: DIR_INTERNAL, GOVERNANCE_POWER: DIR_NONE,
    CROSS_CHAIN_SUPPLY: DIR_IN_OUT,
}

# Ordered detection rules: (compiled regex on lowercased symbol, entity_type).
# Specific patterns first so e.g. "totalAssets" maps to ExchangeRate not Asset.
def _rx(p):
    return re.compile(p)

DETECTION_RULES = [
    (_rx(r"converttoassets|converttoshares|exchangerate|pricepershare|getrate"), EXCHANGE_RATE),
    (_rx(r"totalassets"), EXCHANGE_RATE),
    (_rx(r"totalsupply|totalshares|^shares?$|sharesof|mintedshares|shareprice"), SHARE),
    (_rx(r"\bshare"), SHARE),
    (_rx(r"vault"), VAULT),
    (_rx(r"tranche"), TRANCHE),
    (_rx(r"principal"), PRINCIPAL),
    (_rx(r"interest|apr|apy"), INTEREST),
    (_rx(r"prepay"), PREPAYMENT),
    (_rx(r"repay|repayment"), REPAYMENT),
    (_rx(r"refund"), REFUND),
    (_rx(r"\bfee|fees\b|feebps"), FEE),
    (_rx(r"reward"), REWARD),
    (_rx(r"collateral"), COLLATERAL),
    (_rx(r"debt|owed|liability"), DEBT),
    (_rx(r"loan"), LOAN),
    (_rx(r"lender"), LENDER),
    (_rx(r"borrower"), BORROWER),
    (_rx(r"borrow"), BORROWER),
    (_rx(r"redeem|redemption"), REDEMPTION),
    (_rx(r"withdraw"), WITHDRAWAL),
    (_rx(r"deposit"), DEPOSIT),
    (_rx(r"claim"), CLAIM),
    (_rx(r"position"), POSITION),
    (_rx(r"oracle|latestanswer|getprice|pricefeed|\bprice\b"), ORACLE_PRICE),
    (_rx(r"swap|exactinput|exactoutput|aggregator|dexrouter"), ADAPTER),
    (_rx(r"adapter"), ADAPTER),
    (_rx(r"router"), ROUTER),
    (_rx(r"wrapper|unwrap|\bwrap\b"), WRAPPER),
    (_rx(r"queue|pending|epoch"), QUEUE),
    (_rx(r"vote|voting|governance|proposal|quorum|delegate"), GOVERNANCE_POWER),
    (_rx(r"bridge|crosschain|lockbox|peer|endpoint|lzreceive|_lzsend|mintandburn"), CROSS_CHAIN_SUPPLY),
    (_rx(r"\basset\b|underlying"), ASSET),
    (_rx(r"\btoken\b|erc20"), TOKEN),
]


@dataclass
class DefiEntity:
    name: str = ""
    entity_type: str = ""
    source_symbols: list = field(default_factory=list)  # {kind,name,contract,line}
    related_contracts: list = field(default_factory=list)
    value_direction: str = DIR_NONE
    confidence: str = MEDIUM
    evidence_lines: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return dataclasses.asdict(self)


@dataclass
class DefiEntityMap:
    root: str = ""
    entities: list = field(default_factory=list)

    def by_type(self, entity_type: str):
        for e in self.entities:
            if e.entity_type == entity_type:
                return e
        return None

    def types(self) -> set:
        return {e.entity_type for e in self.entities}

    def to_dict(self) -> dict:
        return {
            "schema_version": "v10-defi-entities",
            "root": self.root,
            "entity_count": len(self.entities),
            "entities": [e.to_dict() for e in self.entities],
        }
