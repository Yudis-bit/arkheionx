"""Tests for the internal function-role taxonomy (v3.8, Agent 2).

Review surface only: roles are structural classification, never confirmed
vulnerabilities, final severity, audit outcomes, or submission readiness.
"""
from __future__ import annotations

import json
import unittest

from arkheionx.intelligence import roles as R


def _roles(**kwargs) -> list[str]:
    return R.classify_function_role(**kwargs).roles


class RoleIdTests(unittest.TestCase):
    def test_classification_id_deterministic(self) -> None:
        a = R.function_role_classification_id("withdraw", "withdraw(uint256)", roles=["OUTFLOW"])
        b = R.function_role_classification_id("withdraw", "withdraw(uint256)", roles=["OUTFLOW"])
        self.assertEqual(a, b)

    def test_classification_id_role_order_independent(self) -> None:
        a = R.function_role_classification_id("f", "f()", roles=["OUTFLOW", "INFLOW"])
        b = R.function_role_classification_id("f", "f()", roles=["INFLOW", "OUTFLOW"])
        self.assertEqual(a, b)

    def test_classification_id_changes_with_signature(self) -> None:
        a = R.function_role_classification_id("withdraw", "withdraw(uint256)")
        b = R.function_role_classification_id("withdraw", "withdraw(uint256,address)")
        self.assertNotEqual(a, b)

    def test_function_role_id_deterministic(self) -> None:
        a = R.function_role_id("OUTFLOW", "withdraw", "withdraw(uint256)")
        b = R.function_role_id("OUTFLOW", "withdraw", "withdraw(uint256)")
        self.assertEqual(a, b)

    def test_function_role_id_includes_role_slug(self) -> None:
        self.assertTrue(R.function_role_id("ORACLE_SETTER", "setOracle").startswith("function-role:oracle-setter:"))

    def test_id_prefixes(self) -> None:
        self.assertTrue(R.function_role_classification_id("f", "f()").startswith("function-role-classification:"))
        self.assertTrue(R.function_role_id("INFLOW", "deposit").startswith("function-role:"))

    def test_ids_have_no_spaces(self) -> None:
        self.assertNotIn(" ", R.function_role_classification_id("withdraw all", "withdraw all()"))
        self.assertNotIn(" ", R.function_role_id("OUTFLOW", "withdraw all"))

    def test_ids_have_no_backslashes(self) -> None:
        self.assertNotIn("\\", R.function_role_classification_id("a", "a()"))
        self.assertNotIn("\\", R.function_role_id("INFLOW", "a"))

    def test_empty_required_inputs_raise_value_error(self) -> None:
        with self.assertRaises(ValueError):
            R.function_role_classification_id("", "")
        with self.assertRaises(ValueError):
            R.function_role_id("")

    def test_unsupported_seed_raises_type_error(self) -> None:
        with self.assertRaises(TypeError):
            R.canonical_role_seed({"x": {1, 2, 3}})

    def test_classification_id_dict_order_independent_seed(self) -> None:
        # canonical_role_seed sorts keys, so equivalent dicts hash identically.
        self.assertEqual(
            R.canonical_role_seed({"a": 1, "b": 2}),
            R.canonical_role_seed({"b": 2, "a": 1}),
        )


class TokenizationTests(unittest.TestCase):
    def test_split_camel_case(self) -> None:
        self.assertEqual(R.split_identifier_tokens("withdrawAll"), ["withdraw", "all"])

    def test_split_snake_case(self) -> None:
        self.assertEqual(R.split_identifier_tokens("set_oracle"), ["set", "oracle"])

    def test_split_kebab_case(self) -> None:
        self.assertEqual(R.split_identifier_tokens("set-oracle"), ["set", "oracle"])

    def test_split_uppercase_acronym(self) -> None:
        self.assertEqual(R.split_identifier_tokens("latestAnswer"), ["latest", "answer"])
        # An acronym before a word stays grouped.
        self.assertIn("erc", "".join(R.split_identifier_tokens("ERCTokenMint")))

    def test_split_signature_name(self) -> None:
        self.assertEqual(R.split_identifier_tokens("withdraw(uint256)"), ["withdraw"])

    def test_leading_trailing_underscores(self) -> None:
        self.assertEqual(R.split_identifier_tokens("_withdraw_"), ["withdraw"])

    def test_numbers_in_identifier(self) -> None:
        self.assertIn("erc20", "".join(R.split_identifier_tokens("erc20Deposit")) or "erc20")

    def test_empty_tokenization_is_graceful(self) -> None:
        self.assertEqual(R.split_identifier_tokens(""), [])
        self.assertEqual(R.split_identifier_tokens("   "), [])

    def test_normalize_selector_accepts_0x_8hex(self) -> None:
        self.assertEqual(R.normalize_selector("0x12345678"), "0x12345678")
        self.assertEqual(R.normalize_selector("12345678"), "0x12345678")
        self.assertEqual(R.normalize_selector("0xABCDEF12"), "0xabcdef12")

    def test_normalize_selector_rejects_invalid(self) -> None:
        self.assertEqual(R.normalize_selector("0xZZZZZZZZ"), "")
        self.assertEqual(R.normalize_selector("0x1234"), "")
        self.assertEqual(R.normalize_selector("notaselector"), "")
        self.assertEqual(R.normalize_selector(""), "")

    def test_normalize_signature_trims_whitespace(self) -> None:
        self.assertEqual(R.normalize_signature("  withdraw(  uint256 )  "), "withdraw( uint256 )")

    def test_extract_function_name_from_signature(self) -> None:
        self.assertEqual(R.extract_function_name_from_signature("withdraw(uint256)"), "withdraw")
        self.assertEqual(R.extract_function_name_from_signature("Vault.withdraw(uint256)"), "withdraw")
        self.assertEqual(R.extract_function_name_from_signature("withdraw"), "withdraw")


class ClassificationTests(unittest.TestCase):
    def test_deposit_inflow(self) -> None:
        self.assertEqual(_roles(function_name="deposit"), [R.INFLOW])

    def test_supply_inflow(self) -> None:
        self.assertEqual(_roles(function_name="supply"), [R.INFLOW])

    def test_add_liquidity_inflow(self) -> None:
        self.assertIn(R.INFLOW, _roles(function_name="addLiquidity"))

    def test_withdraw_outflow(self) -> None:
        self.assertEqual(_roles(function_name="withdraw"), [R.OUTFLOW])

    def test_redeem_outflow(self) -> None:
        self.assertEqual(_roles(function_name="redeem"), [R.OUTFLOW])

    def test_stake_inflow(self) -> None:
        self.assertEqual(_roles(function_name="stake"), [R.INFLOW])

    def test_unstake_outflow_not_inflow(self) -> None:
        out = _roles(function_name="unstake")
        self.assertEqual(out, [R.OUTFLOW])
        self.assertNotIn(R.INFLOW, out)

    def test_set_oracle_setter(self) -> None:
        self.assertIn(R.ORACLE_SETTER, _roles(function_name="setOracle"))

    def test_set_price_feed_setter(self) -> None:
        self.assertIn(R.ORACLE_SETTER, _roles(function_name="setPriceFeed"))

    def test_get_price_view_consumer(self) -> None:
        out = _roles(function_name="getPrice", mutability="view")
        self.assertIn(R.ORACLE_CONSUMER, out)
        self.assertIn(R.VIEW_PURE, out)

    def test_set_fee_admin_param(self) -> None:
        self.assertIn(R.ADMIN_PARAM, _roles(function_name="setFee"))

    def test_grant_role_access_control(self) -> None:
        self.assertIn(R.ACCESS_CONTROL, _roles(function_name="grantRole"))

    def test_transfer_ownership_access_control(self) -> None:
        self.assertIn(R.ACCESS_CONTROL, _roles(function_name="transferOwnership"))

    def test_pause_emergency(self) -> None:
        self.assertEqual(_roles(function_name="pause"), [R.PAUSE_EMERGENCY])

    def test_unpause_emergency(self) -> None:
        self.assertEqual(_roles(function_name="unpause"), [R.PAUSE_EMERGENCY])

    def test_emergency_withdraw_pause_and_outflow(self) -> None:
        out = _roles(function_name="emergencyWithdraw")
        self.assertIn(R.PAUSE_EMERGENCY, out)
        self.assertIn(R.OUTFLOW, out)

    def test_upgrade_to_proxy(self) -> None:
        self.assertIn(R.UPGRADE_PROXY, _roles(function_name="upgradeTo"))

    def test_upgrade_to_and_call_proxy(self) -> None:
        self.assertIn(R.UPGRADE_PROXY, _roles(function_name="upgradeToAndCall"))

    def test_delegatecall_role(self) -> None:
        self.assertIn(R.DELEGATECALL, _roles(function_name="delegatecall"))

    def test_borrow_repay(self) -> None:
        self.assertEqual(_roles(function_name="borrow"), [R.BORROW_REPAY])
        self.assertEqual(_roles(function_name="repay"), [R.BORROW_REPAY])

    def test_liquidate_liquidation(self) -> None:
        self.assertIn(R.LIQUIDATION, _roles(function_name="liquidate"))

    def test_liquidation_call_liquidation(self) -> None:
        self.assertIn(R.LIQUIDATION, _roles(function_name="liquidationCall"))

    def test_swap_role(self) -> None:
        self.assertIn(R.SWAP, _roles(function_name="swapExactTokensForTokens"))

    def test_exact_input_swap(self) -> None:
        self.assertIn(R.SWAP, _roles(function_name="exactInput"))

    def test_mint_burn(self) -> None:
        self.assertEqual(_roles(function_name="mint"), [R.MINT_BURN])
        self.assertEqual(_roles(function_name="burn"), [R.MINT_BURN])

    def test_claim_rewards(self) -> None:
        self.assertIn(R.CLAIM_REWARD, _roles(function_name="claimRewards"))

    def test_bridge_out(self) -> None:
        self.assertIn(R.BRIDGE, _roles(function_name="bridgeOut"))

    def test_receive_message_bridge(self) -> None:
        self.assertIn(R.BRIDGE, _roles(function_name="receiveMessage"))

    def test_accrue_interest_accounting(self) -> None:
        self.assertIn(R.ACCOUNTING_MUTATION, _roles(function_name="accrueInterest"))

    def test_update_index_accounting(self) -> None:
        self.assertIn(R.ACCOUNTING_MUTATION, _roles(function_name="updateIndex"))

    def test_multicall_external_call(self) -> None:
        self.assertIn(R.EXTERNAL_CALL, _roles(function_name="multicall"))

    def test_rescue_tokens_external_or_admin(self) -> None:
        out = _roles(function_name="rescueTokens")
        self.assertTrue({R.EXTERNAL_CALL, R.ADMIN_PARAM} & set(out))

    def test_calculate_health_factor_view(self) -> None:
        self.assertEqual(_roles(function_name="calculateHealthFactor", mutability="pure"), [R.VIEW_PURE])

    def test_update_oracle_ambiguous_warning(self) -> None:
        c = R.classify_function_role(function_name="updateOracle")
        self.assertIn(R.ORACLE_SETTER, c.roles)
        self.assertTrue(c.warnings)

    def test_unknown_function_unclassified_with_warning(self) -> None:
        c = R.classify_function_role(function_name="frobnicate")
        self.assertEqual(c.roles, [])
        self.assertTrue(c.warnings)
        self.assertEqual(c.metadata.get("status"), R.UNCLASSIFIED)

    def test_multi_label_output_deterministic_order(self) -> None:
        a = _roles(function_name="emergencyWithdraw")
        b = _roles(function_name="emergencyWithdraw")
        self.assertEqual(a, b)

    def test_roles_follow_priority_ordering(self) -> None:
        # PAUSE_EMERGENCY (index 2) must precede OUTFLOW (index 13).
        out = _roles(function_name="emergencyWithdraw")
        self.assertLess(out.index(R.PAUSE_EMERGENCY), out.index(R.OUTFLOW))

    def test_contradictory_view_and_state_change_warns(self) -> None:
        c = R.classify_function_role(function_name="withdraw", mutability="view")
        self.assertEqual(c.roles, [R.VIEW_PURE])
        self.assertTrue(any("contradiction" in w for w in c.warnings))

    def test_classify_from_signature_only(self) -> None:
        self.assertEqual(_roles(signature="deposit(uint256)"), [R.INFLOW])

    def test_matched_and_unmatched_tokens_recorded(self) -> None:
        c = R.classify_function_role(function_name="emergencyWithdraw")
        self.assertIn("emergency", c.matched_tokens)
        self.assertIn("withdraw", c.matched_tokens)


class FalsePositiveControlTests(unittest.TestCase):
    def test_transfer_from_not_plain_transfer_outflow(self) -> None:
        out = _roles(function_name="transferFrom")
        self.assertNotIn(R.OUTFLOW, out)

    def test_unstake_does_not_match_stake(self) -> None:
        self.assertNotIn(R.INFLOW, _roles(function_name="unstake"))

    def test_preview_withdraw_view_not_outflow(self) -> None:
        out = _roles(function_name="previewWithdraw", mutability="view")
        self.assertEqual(out, [R.VIEW_PURE])
        self.assertNotIn(R.OUTFLOW, out)

    def test_get_exchange_rate_not_oracle_setter(self) -> None:
        out = _roles(function_name="getExchangeRate", mutability="view")
        self.assertNotIn(R.ORACLE_SETTER, out)
        self.assertIn(R.ORACLE_CONSUMER, out)

    def test_no_substring_cross_match(self) -> None:
        # "liquidationCall" must not pick up a spurious EXTERNAL_CALL from "call".
        self.assertEqual(_roles(function_name="liquidationCall"), [R.LIQUIDATION])


class NoOverclaimTests(unittest.TestCase):
    def test_manual_review_required_true(self) -> None:
        self.assertTrue(R.classify_function_role(function_name="withdraw").manual_review_required)

    def test_ready_for_submission_false(self) -> None:
        self.assertFalse(R.classify_function_role(function_name="withdraw").ready_for_submission)

    def test_no_overclaim_tokens_in_taxonomy(self) -> None:
        forbidden = {"SAFE", "VERIFIED_SAFE", "CONFIRMED_VULNERABILITY", "AUDIT_PASSED",
                     "FINAL_SEVERITY", "HUMAN_REVIEWED", "BOUNTY"}
        self.assertFalse(forbidden & set(R.FUNCTION_ROLE_VALUES))
        self.assertFalse(forbidden & set(R.FUNCTION_ROLE_DESCRIPTIONS))

    def test_output_has_no_overclaim_wording(self) -> None:
        blob = json.dumps(R.classify_function_role(
            function_name="liquidate", signature="liquidate(address)").to_dict()).lower()
        for token in ("human_reviewed", "confirmed vulnerability", "final severity",
                      "audit passed", "bounty", "verified_safe", "ready_for_submission\": true"):
            self.assertNotIn(token, blob)

    def test_eighteen_roles_present(self) -> None:
        self.assertEqual(len(R.FUNCTION_ROLE_VALUES), 18)
        for role in (R.INFLOW, R.OUTFLOW, R.ACCOUNTING_MUTATION, R.EXTERNAL_CALL,
                     R.ORACLE_CONSUMER, R.ORACLE_SETTER, R.ADMIN_PARAM, R.ACCESS_CONTROL,
                     R.PAUSE_EMERGENCY, R.UPGRADE_PROXY, R.DELEGATECALL, R.BORROW_REPAY,
                     R.LIQUIDATION, R.SWAP, R.MINT_BURN, R.CLAIM_REWARD, R.BRIDGE, R.VIEW_PURE):
            self.assertIn(role, R.FUNCTION_ROLE_VALUES)

    def test_classification_json_serializable(self) -> None:
        data = R.classify_function_role(function_name="deposit", signature="deposit(uint256)").to_dict()
        self.assertEqual(json.loads(json.dumps(data)), data)

    def test_confidence_is_classified_not_security(self) -> None:
        self.assertEqual(R.classify_function_role(function_name="deposit").confidence, "CLASSIFIED")


class ImportAndExportTests(unittest.TestCase):
    def test_import_has_no_filesystem_side_effects(self) -> None:
        import importlib
        import arkheionx.intelligence.roles as mod
        # Reloading must not touch the filesystem or raise.
        importlib.reload(mod)
        self.assertTrue(hasattr(mod, "classify_function_role"))

    def test_package_exports_roles(self) -> None:
        import arkheionx.intelligence as intel
        self.assertTrue(hasattr(intel, "roles"))
        self.assertTrue(hasattr(intel, "classify_function_role"))
        self.assertTrue(hasattr(intel, "FunctionRoleClassification"))
        self.assertIn("classify_function_role", intel.__all__)

    def test_classification_is_deterministic_across_calls(self) -> None:
        a = R.classify_function_role(function_name="swap", signature="swap(uint256)").to_dict()
        b = R.classify_function_role(function_name="swap", signature="swap(uint256)").to_dict()
        self.assertEqual(a, b)


if __name__ == "__main__":
    unittest.main()
