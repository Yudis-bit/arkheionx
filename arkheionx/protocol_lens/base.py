"""The :class:`ProtocolLens` abstract base class.

A protocol lens is a declarative, local/static description of a protocol family:
its identity, the terms/symbols that locate it in a repository, its behavior
promises, economic invariants, temporal windows, periphery composition, and the
review lanes a reviewer should walk. The lens supplies *protocol-aware structure*;
the builders in this package combine it with the repository's review map and an
optional scope note to produce lanes, tasks, evidence maps, and report filters.

A lens encodes no line numbers and no specific known bug. It is a model, not a
finding. Concrete lenses (e.g. :mod:`arkheionx.protocol_lens.lenses.fixed_credit_market`)
subclass this and fill in the data.
"""
from __future__ import annotations

from abc import ABC, abstractmethod

from . import models as m


class ProtocolLens(ABC):
    """Declarative protocol-aware lens. Subclasses provide static lens content."""

    # ----- identity -------------------------------------------------------
    @abstractmethod
    def meta(self) -> m.ProtocolLensMeta:
        """Static identity/capability metadata for this lens."""

    @property
    def lens_id(self) -> str:
        return self.meta().lens_id

    @property
    def display_name(self) -> str:
        return self.meta().display_name

    # ----- extraction hints ----------------------------------------------
    @abstractmethod
    def extraction_groups(self) -> list[m.ExtractionGroup]:
        """Named groups of protocol terms/symbols the extractor searches for."""

    def periphery_function_names(self) -> list[str]:
        """Names of periphery/bundle functions the lens watches (may be empty)."""
        return []

    def value_flow_templates(self) -> list[m.ValueFlowPath]:
        """Generic value-flow paths this protocol family is expected to expose."""
        return []

    # ----- protocol-aware content ----------------------------------------
    @abstractmethod
    def behavior_promises(self) -> list[m.BehaviorPromise]:
        """The default behavior promises this protocol is expected to keep."""

    @abstractmethod
    def economic_invariants(self) -> list[m.EconomicInvariant]:
        """The default economic invariants this protocol must preserve."""

    @abstractmethod
    def review_lanes(self) -> list[m.LensLaneDef]:
        """The default review lanes (review order, never severity)."""

    def temporal_windows(self) -> list[m.TemporalWindow]:
        """Time/observation windows where intermediate state can be observed."""
        return []

    # ----- convenience lookups -------------------------------------------
    def all_term_to_group(self) -> dict[str, str]:
        """Map every extraction term (lowercased) -> its group id."""
        out: dict[str, str] = {}
        for grp in self.extraction_groups():
            for term in grp.terms:
                out[term.lower()] = grp.group_id
        return out

    def invariant_by_id(self) -> dict[str, m.EconomicInvariant]:
        return {inv.id: inv for inv in self.economic_invariants()}

    def promise_by_id(self) -> dict[str, m.BehaviorPromise]:
        return {p.id: p for p in self.behavior_promises()}

    def lane_by_id(self) -> dict[str, m.LensLaneDef]:
        return {ld.lane_id: ld for ld in self.review_lanes()}

    def to_model_dict(self) -> dict:
        """Serialize the static lens content (no repo binding) to a dict."""
        meta = self.meta()
        return {
            "schema_version": m.SCHEMA_VERSION,
            "lens_layer": m.LENS_LAYER,
            "lens": meta.to_dict(),
            "extraction_groups": [g.to_dict() for g in self.extraction_groups()],
            "behavior_promises": [p.to_dict() for p in self.behavior_promises()],
            "economic_invariants": [i.to_dict() for i in self.economic_invariants()],
            "temporal_windows": [t.to_dict() for t in self.temporal_windows()],
            "review_lanes": [ld.to_dict() for ld in self.review_lanes()],
            "periphery_function_names": list(self.periphery_function_names()),
            "value_flow_templates": [v.to_dict() for v in self.value_flow_templates()],
        }
