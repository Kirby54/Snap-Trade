# Position sizing, units and limits

`plan.py` never places orders. Positive-price, linear-payoff instruments only:
not inverse contracts, options or arbitrary nonlinear derivatives. A valid
calculation does not establish a profitable setup or broker eligibility.

| Argument | Unit and meaning |
| --- | --- |
| `--entry`, `--sl`, `--tp` | Prices of the exact same instrument in quote currency |
| `--point-value` | Quote-currency value of one price point per unit/lot/contract |
| `--fx-rate` | Account-currency units per quote-currency unit; default 1 |
| `--account`, `--risk-amount`, `--max-notional` | Account currency |
| `--cost-per-unit` | Estimated round-trip cost per unit/lot/contract in account currency |
| `--qty-step`, `--min-qty` | Broker quantity step/minimum; no step means theoretical size |
| `--avg-candle` | Mean high-low range of 10–20 closed execution candles, in price points |
| `--min-candle-multiple` | Minimum stop / mean-range ratio, default 1.5, CLI minimum 1 |
| `--min-stop-pct` | Additional technical price-percent filter, default 0.05; not measured spread |
| `--open-price` | Hypothetical/observed opening price for cancellation checks; no automatic entry |

Screenshot mode requires `--avg-candle` and keeps the 1.5 multiple. Legacy
standalone calls without it remain supported but do not pass the screenshot
workflow. A small pivot buffer is separate from this minimum total distance.
If no structural stop meets the floor and R:R, abstain. The floor is a
provisional heuristic to test, not a guarantee that noise cannot hit a stop.

Confirm instrument specifications, account currency and conversion rate.
For a standard forex lot, 100000 is a multiplier only for a suitable quote
convention. Point, pip, tick and tick value are different. Index levels cannot
be copied directly onto a future/CFD contract.

Loss/unit = entry-stop distance × point value × conversion + round-trip costs.
Net gain/unit = entry-target distance × point value × conversion − costs.
`targets[].rr` is gross; `targets[].net_rr` is the checked net ratio.
Quantity respects risk and notional caps and rounds **down** to the supplied
step. Reject when the result cannot meet the broker minimum. `size.max_loss`
keeps its historical name but is an **estimated** stop loss, never a guarantee.
Futures notional is not broker margin. Short eligibility and borrow costs
are not verified by this arithmetic.

```bash
python3 skills/snap-and-trade/scripts/plan.py --side short --entry 8372 --sl 8390 --tp 8340 --avg-candle 10 --risk-amount 100 --point-value 1 --qty-step 1 --cost-per-unit 1
```

Opening at/beyond SL against the idea or at/beyond TP1 in its direction
cancels the plan. Between those bounds, wait for fresh confirmation and
recalculate with an actual entry. Quotes do not prove a session is open.
Fixed per-order fees, changing spread, gaps and slippage need explicit
assumptions; do not silently treat unknown costs as zero net costs. Over 2%
of supplied capital requires `--allow-high-risk` and an explicit user request.
Never set that flag or change a stop to force approval.
