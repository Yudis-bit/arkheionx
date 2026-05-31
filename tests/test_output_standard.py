import json
import unittest
from pathlib import Path

from arkheionx.flow.mermaid import render_mermaid
from arkheionx.protocol.detector import analyze
from arkheionx.protocol.model import to_dict
from arkheionx.protocol.render import build_json

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURE = REPO_ROOT / "examples" / "oracle-staking-fixture"
SCHEMAS = REPO_ROOT / "schemas"


def _required(schema_name: str) -> list[str]:
    schema = json.loads((SCHEMAS / schema_name).read_text(encoding="utf-8"))
    return schema.get("required", [])


class OutputStandardSchemaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.analysis = analyze(FIXTURE)

    def test_protocol_map_required_keys_present(self) -> None:
        payload = build_json(self.analysis, {}, [])
        for key in _required("protocol-map.schema.json"):
            self.assertIn(key, payload)

    def test_money_flow_required_keys_present(self) -> None:
        flow = to_dict(self.analysis.money_flow)
        for key in _required("value-flow.schema.json"):
            self.assertIn(key, flow)

    def test_hunt_report_required_keys_present(self) -> None:
        payload = build_json(self.analysis, {}, [])
        self.assertIn("hunter_targets", payload)
        for target in payload["hunter_targets"]:
            for key in ["rank", "target_id", "score", "priority", "evidence_level"]:
                self.assertIn(key, target)

    def test_evidence_levels_are_valid_enum(self) -> None:
        valid = {"HEURISTIC", "COMPILER_CONFIRMED", "EXECUTION_CONFIRMED", "REPORT_READY"}
        self.assertIn(self.analysis.snapshot.evidence_level, valid)
        for fr in self.analysis.functions:
            self.assertIn(fr.evidence_level, valid)

    def test_mermaid_artifact_round_trips(self) -> None:
        mermaid = render_mermaid(self.analysis.money_flow)
        self.assertTrue(mermaid.strip().startswith("flowchart"))

    def test_schemas_are_valid_json(self) -> None:
        for schema in SCHEMAS.glob("*.schema.json"):
            json.loads(schema.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
