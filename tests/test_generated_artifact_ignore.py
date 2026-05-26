import importlib.util
import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCANNER = REPO_ROOT / "scripts" / "pre_audit_scan.py"


def load_scanner_module():
    spec = importlib.util.spec_from_file_location("pre_audit_scan", SCANNER)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    sys.modules["pre_audit_scan"] = module
    spec.loader.exec_module(module)
    return module


def write_fake_repo(root: Path) -> None:
    (root / "src").mkdir(parents=True)
    (root / "test").mkdir(parents=True)
    (root / "reports").mkdir(parents=True)
    (root / "foundry.toml").write_text(
        '[profile.default]\nsrc = "src"\ntest = "test"\n',
        encoding="utf-8",
    )
    (root / "src" / "ToyVault.sol").write_text(
        textwrap.dedent(
            """
            // SPDX-License-Identifier: MIT
            pragma solidity ^0.8.20;

            interface AggregatorV3Interface {
                function latestRoundData()
                    external
                    view
                    returns (uint80, int256, uint256, uint256, uint80);
            }

            contract ToyVault {
                AggregatorV3Interface public priceFeed;
                address public owner;
                mapping(address => uint256) public balanceOf;
                uint256 public totalAssets;
                uint256 public rewardPerTokenStored;

                modifier onlyOwner() {
                    require(msg.sender == owner, "owner");
                    _;
                }

                constructor(AggregatorV3Interface feed) {
                    owner = msg.sender;
                    priceFeed = feed;
                }

                function setOracle(AggregatorV3Interface feed) external onlyOwner {
                    priceFeed = feed;
                }

                function deposit(uint256 assets) external {
                    balanceOf[msg.sender] += assets;
                    totalAssets += assets;
                }

                function withdraw(uint256 assets) external {
                    balanceOf[msg.sender] -= assets;
                    totalAssets -= assets;
                    payable(msg.sender).call{value: 0}("");
                }

                function latestPrice() external view returns (int256) {
                    (, int256 answer,,,) = priceFeed.latestRoundData();
                    return answer;
                }

                function claimReward() external {
                    rewardPerTokenStored += 1;
                }
            }
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (root / "test" / "ToyVault.t.sol").write_text(
        textwrap.dedent(
            """
            // SPDX-License-Identifier: MIT
            pragma solidity ^0.8.20;

            contract ToyVaultTest {
                function testSmoke() public {
                    assert(true);
                }
            }
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (root / "reports" / "v092-repeat-scan.json").write_text(
        '{"tool": "Arkheionx Pre-Audit Scanner", "note": "old generated report"}\n',
        encoding="utf-8",
    )


def run_scan(root: Path, stem: str) -> dict:
    reports = root / "reports"
    json_path = reports / f"{stem}-pre-audit-report.json"
    subprocess.run(
        [
            "python3",
            str(SCANNER),
            "--root",
            str(root),
            "--protocol-type",
            "auto",
            "--output",
            str(reports / f"{stem}-pre-audit-report.md"),
            "--json-output",
            str(json_path),
            "--issue-plan-output",
            str(reports / f"{stem}-issue-plan.json"),
            "--issue-checklist-output",
            str(reports / f"{stem}-issue-checklist.md"),
        ],
        cwd=REPO_ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    return json.loads(json_path.read_text(encoding="utf-8"))


class GeneratedArtifactIgnoreTests(unittest.TestCase):
    def test_generated_artifact_path_and_marker_detection(self) -> None:
        scanner = load_scanner_module()
        root = Path("/tmp/example")
        self.assertTrue(scanner.is_generated_artifact_path(root / "reports" / "toy-pre-audit-report.md", root))
        self.assertTrue(
            scanner.is_arkheionx_generated_artifact(
                root / "reports" / "custom-name.md",
                root,
                "# Arkheionx Pre-Audit Readiness Report\n",
            )
        )

    def test_repeated_scan_ignores_previous_generated_outputs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "fake-defi"
            root.mkdir()
            write_fake_repo(root)

            first = run_scan(root, "first")
            second = run_scan(root, "repeat")

        self.assertEqual(first["score"], second["score"])
        self.assertEqual(
            {finding["id"] for finding in first["findings"]},
            {finding["id"] for finding in second["findings"]},
        )
        scan_sources = second["scan_sources"]
        self.assertGreater(scan_sources["generated_artifacts_ignored"], 0)
        ignored = "\n".join(scan_sources["ignored_generated_artifact_paths"])
        self.assertIn("reports/first-pre-audit-report.md", ignored)
        self.assertIn("reports/first-pre-audit-report.json", ignored)
        self.assertIn("reports/first-issue-plan.json", ignored)
        self.assertIn("reports/v092-repeat-scan.json", ignored)
        self.assertFalse(
            [
                item
                for item in second.get("negative_evidence", [])
                if str(item.get("file", "")).startswith("reports/")
                or "Arkheionx Pre-Audit Readiness Report" in str(item.get("snippet", ""))
                or "ARK-" in str(item.get("snippet", ""))
            ]
        )
        self.assertTrue(second["files_scanned"]["solidity_sources"])
        self.assertTrue(second["files_scanned"]["solidity_tests"])


if __name__ == "__main__":
    unittest.main()
