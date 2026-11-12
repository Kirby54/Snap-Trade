# Replay and paper-trading evaluation

No measured trading edge is currently demonstrated. This protocol records
outcomes without changing a plan after seeing future prices. A green CI run,
a confluence score or resampled simulations cannot establish profitability.

## Freeze before starting

Record repository version, model/version, prompts/settings, instruments,
timeframes, date-selection method, scoring version and exit management.
Separate development and held-out evaluation periods. Choose observation
times before opening the charts. Keep every signal, loss and NO TRADE.

For each observation archive the original 5m + context images without future
bars, their timestamps/timezone, raw model response and numerical commands.
Keep evidence outside public Git until you have removed account information.
Read `evaluation.md` for visual-reading metrics separate from trading results.

## Record a signal

1. In FX Replay or another replay tool, stop at the selected timestamp.
2. Capture both timeframes and obtain the short card before advancing time.
3. Log the exact levels with `journal.py add`, including `--source replay`.
   For NO TRADE use `--side none`. Include `score=3/3; scoring=v2.3` in notes.
4. Do not rerun a losing analysis, adjust the historical entry, or remove it.
5. Advance without changing the fixed plan:
   - Entry never fills before expiry/invalidation → `nofill`.
   - Stop before TP1 → `sl` (idealized fill only).
   - TP1, then remaining position exits at entry → `tp1`.
   - TP2 → `tp2`; use only if TP2 existed in the original plan.
   - Realized slippage, manual/time exit → `exit --exit PRICE` using the
     volume-weighted exit price of the **whole** position, not just the remainder.
   - Stop and target in the same candle without lower-resolution evidence:
     conservatively count the stop first and disclose that assumption.
6. Use `journal.py result ID --outcome ... --cost-r VALUE`. Cost R is total
   monetary fees/spread/slippage costs not already reflected in fills divided
   by initial monetary risk. Avoid double counting; 0 means gross statistics.

## Report honestly

Publish anonymized signal/outcome data, sample sizes, costs, unfilled/open
counts and all losses. Report average net R, profit factor and losing streaks
by market, timeframe and confidence, separating replay, paper and live.
The initial 30 trades are exploratory. Positive average R in a short or
dependent sample is not proof of an edge. A held-out period and subsequent
paper observation are necessary to assess whether improvements generalize.

Confluence buckets are not calibrated odds. Fix the mapping for a series:
low=2, medium=3, high=4, NO TRADE=0, with raw numerator/denominator in notes.
Do not combine v2.1 fixed-/5 scores with v2.3 available-evidence scores without
labelling versions. A test of the evaluator is not a measured model result.

## Journal storage and calculations

One command at a time. A `.lock` file prevents concurrent readers/writers;
unique temporary files and atomic replacement protect writes. After a crash,
remove a stale lock only after checking no process uses the journal. Back up
before any correction and document its reason. Prefer a local disk.

Old CSVs without `cost_r` load as gross and migrate on the next write. Invalid
rows are rejected without overwriting. Losing streaks follow signal-recording
order, not closing order, and are not monetary drawdown. Without TP2, split
management exits the whole position at TP1. With TP2, the two columns compare
hypothetical exit policies; they are not two simultaneously executed results.
