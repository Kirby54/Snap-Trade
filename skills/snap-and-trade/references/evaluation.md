# Visual evaluation and reproducibility

The repository includes **synthetic development fixtures**, not a measured
vision benchmark and not a backtest. `assess.py` checks supplied observations;
it does not read screenshots. No visual accuracy or profitability number is
claimed. The illustrative GIF is drawn from synthetic inputs, not a recording
of a model session.

## Existing development cases

`evaluation/cases.json` pins images by SHA-256. Cases cover index price-source
conflicts, missing higher context, closed session, a tight stop and an
unreadable latest-price label. Each complete case includes 5m and 1h images
of a fictional instrument. Labels are openly visible: these are debugging
fixtures, not a hidden test. Check identity with:

```bash
python tools/benchmark.py --check-fixtures
```

To evaluate a model, start a fresh session per case, attach exactly its
images, use the same prompt/version/settings, archive the verbatim answer,
and record extracted `latest_price`, `signal`, `available`. Do not copy the
expected labels into the answer file. Record `model`, `model_version` and
`prompt_version`, then run:

```bash
python tools/benchmark.py --answers evaluation/answers.json --output evaluation/report.json
```

The report names unanswered cases and counts exact price matches, decision
matches, denominator matches and actions on cases labelled NO TRADE. Partial
results are marked incomplete. Repeat each case across independent sessions
and report disagreement; do not select the best run.

## Required next evidence

Collect consented real screenshots from multiple providers, markets and
regimes. Include cursor/header conflicts, cropping, log scale, overlapping
labels, stale data, missing context and forming candles. Have an independent
reviewer label readable prices, identity, timeframe and abstention conditions
before the model sees the case. Separate development and held-out cases.
Keep raw images, hashes, timestamps, prompts and verbatim outputs.

Measure price/identity errors, hallucinated levels, abstention failures,
repeatability and execution checks separately from profit/loss. A deterministic
unit test or a small synthetic set cannot establish real-image accuracy.
For trading outcomes use the separate replay protocol in `backtest.md`, with
costs, all losses and an untouched evaluation period. Do not claim that 30
trades, or 10,000 resampled paths, establish an edge or a win probability.

## Rebuild visual assets

Developer-only dependency: Pillow. `python tools/make_visual_assets.py`
rebuilds the fixtures, hashes and GIF. Runtime scripts and tests do not depend
on Pillow. Review changed images before committing a rebuilt manifest.
