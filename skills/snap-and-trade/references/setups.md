# Setups: structural entry, stop and targets

Every setup has a mirrored long/short form. Read only closed candles. All
setups must pass the same mandatory context, trigger and numerical checks.

A buffer beyond a pivot can be 10–25% of a recent mean candle range. That is
**only the buffer**, not the whole stop distance. Total entry-stop distance
must be at least 1.5 times the mean high-low range of 10–20 closed execution
candles. If that pushes the stop off defensible structure or makes net
reward/risk below 1.5, return NO TRADE. Do not force a trade by changing prices.

| Setup | Trigger and entry | Structural stop | Targets |
| --- | --- | --- | --- |
| Breakout / breakdown | Closed candle outside a repeatedly tested boundary; prefer a confirmed retest | Other side of the invalidating boundary/pivot, with buffer and volatility floor | Next visible level first, then next structure; projected range only if not blocked by nearer structure |
| Trend pullback | Return to visible support/resistance followed by a closed rejection | Beyond the pullback swing plus buffer and floor | Prior trend extreme, then next level |
| Range | Closed rejection at a clearly tested range boundary | Beyond that boundary plus buffer and floor | Midpoint first, opposite boundary second; skip if too narrow |
| Reversal | Major visible level, structural break and closed retest; divergence only if displayed | Beyond the invalidating extreme plus buffer and floor | Next opposing structure, then prior move origin |
| Chart pattern | Closed neckline/edge break or confirmed retest | Beyond internal invalidating pivot with buffer and floor | Nearer visible structure before a measured projection |

Counter to higher-timeframe structure: confidence stays low regardless of raw
score. A missing higher timeframe is not countertrend evidence: request it
and abstain. Do not confuse a forming breakout with confirmation.

NO TRADE: price in the middle of a range, no defensible stop, unconfirmed
trigger, conflicting or stale chart identity, unreadable price/timeframe,
missing context, insufficient observations or rejected numerical plan.
Always state one concrete condition that would justify reassessment.
