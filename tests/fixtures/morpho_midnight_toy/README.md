# morpho_midnight_toy (synthetic fixture)

A small, fully synthetic fixed-maturity credit market used to exercise the
Arkheionx v7.5 **Morpho Midnight protocol lens** in tests.

**This is not Morpho source.** Every contract is invented (`CreditMarket`,
`OfferBook`, `PeripheryBundler`, `MarketGate`, `MockLoanToken`) and uses generic
credit-market vocabulary (maturity, credit/debt units, loss factor, offers, group
budgets, target/cap periphery, gates, fees) only so the lens extractor and the
evidence classifier have realistic domain symbols to find.

The `test/` files are illustrative fixture tests for the static evidence
classifier. They are never executed by the Python suite, assert nothing about any
real protocol, and prove no safety. `scope.md` is a synthetic scope note.

Run the lens against it locally:

```bash
arkheionx lens-pack tests/fixtures/morpho_midnight_toy \
  --lens morpho-midnight \
  --scope-file tests/fixtures/morpho_midnight_toy/scope.md \
  --out .arkheionx/lens-pack
```

Everything produced is a local/static planning artifact. It is not a finding, not
a severity, and not a confirmed vulnerability. Human review is required.
