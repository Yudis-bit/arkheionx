"""Target-resolution hardening for the protocol intelligence model (v3.5, Agent 7).

Pins exact-only resolution semantics: function_id, then alias value, then
display_name, then signature; empty/missing/ambiguous returns ''. No fuzzy,
substring, or case-insensitive matching, and duplicate display names or shared
aliases never overlink.
"""
from __future__ import annotations

import unittest

from arkheionx.intelligence import build

resolve = build.resolve_function_id_by_alias

STABLE = "src/Vault.sol:Vault.withdraw(uint256)#L10-L20"


def _model(*functions: dict):
    return build.build_protocol_model_from_review_map({"functions": list(functions)}, "/repo")


def _fn(contract="Vault", name="withdraw", signature="withdraw(uint256)", **extra) -> dict:
    return {"contract": contract, "name": name, "signature": signature, "path": f"src/{contract}.sol", **extra}


class ExactResolutionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = _model(_fn(stable_id=STABLE))
        self.fid = self.model.functions[0].function_id

    def test_exact_function_id(self) -> None:
        self.assertEqual(resolve(self.model, self.fid), self.fid)

    def test_exact_legacy_alias(self) -> None:
        self.assertIn(STABLE, self.model.functions[0].aliases.values())
        self.assertEqual(resolve(self.model, STABLE), self.fid)

    def test_exact_display_name(self) -> None:
        self.assertEqual(resolve(self.model, "Vault.withdraw"), self.fid)

    def test_exact_signature(self) -> None:
        self.assertEqual(resolve(self.model, "withdraw(uint256)"), self.fid)


class EmptyAndMissingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = _model(_fn())

    def test_empty_returns_empty(self) -> None:
        self.assertEqual(resolve(self.model, ""), "")

    def test_missing_returns_empty(self) -> None:
        self.assertEqual(resolve(self.model, "Ghost.missing"), "")


class NoFuzzyMatchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.model = _model(_fn())

    def test_substring_does_not_match(self) -> None:
        self.assertEqual(resolve(self.model, "withdraw"), "")  # substring of display/signature

    def test_similar_but_non_exact_does_not_match(self) -> None:
        self.assertEqual(resolve(self.model, "Vault.withdraw "), "")  # trailing space
        self.assertEqual(resolve(self.model, "Vault.withdraw2"), "")

    def test_matching_is_case_sensitive(self) -> None:
        self.assertEqual(resolve(self.model, "vault.withdraw"), "")
        self.assertEqual(resolve(self.model, "VAULT.WITHDRAW"), "")


class NoOverlinkTests(unittest.TestCase):
    def test_duplicate_display_name_returns_empty(self) -> None:
        # Same contract+function name in two files -> one display, two function_ids.
        model = build.build_protocol_model_from_review_map(
            {"functions": [
                {"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)", "path": "a/Vault.sol"},
                {"contract": "Vault", "name": "withdraw", "signature": "withdraw(uint256)", "path": "b/Vault.sol"},
            ]}, "/repo")
        self.assertEqual(len({f.function_id for f in model.functions}), 2)
        self.assertEqual(resolve(model, "Vault.withdraw"), "")

    def test_shared_legacy_alias_returns_empty(self) -> None:
        model = _model(_fn(contract="A", name="f", signature="g()", stable_id="DUP"),
                       _fn(contract="B", name="h", signature="k()", stable_id="DUP"))
        self.assertEqual(resolve(model, "DUP"), "")

    def test_same_name_different_contract_does_not_overlink(self) -> None:
        model = _model(_fn(contract="A", name="f", signature="f()"),
                       _fn(contract="B", name="f", signature="f()"))
        a_fid = next(f.function_id for f in model.functions if f.contract_id == model.functions[0].contract_id)
        self.assertEqual(resolve(model, "A.f"), a_fid)
        self.assertEqual(resolve(model, "f"), "")  # bare name is ambiguous/substring -> empty
        self.assertNotEqual(resolve(model, "A.f"), resolve(model, "B.f"))


if __name__ == "__main__":
    unittest.main()
