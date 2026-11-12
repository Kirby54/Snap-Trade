# 📸 Snap & Trade

[![tests](https://github.com/Kirby54/Snap-Trade/actions/workflows/tests.yml/badge.svg)](https://github.com/Kirby54/Snap-Trade/actions/workflows/tests.yml)
![version](https://img.shields.io/badge/version-2.2.0-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![python](https://img.shields.io/badge/python-3.10%2B-blue)

An **all-in-one trading assistant** by [Kirby54](https://github.com/Kirby54).
Send a **screenshot of a chart**—stocks, crypto, forex, indices or futures,
on any timeframe—from TradingView, MT4/MT5, FX Replay, Binance or another
platform. Get a step-by-step analysis followed by a clear trade plan.

### Example: conditional SHORT · NDX · 5 min

**Confidence:** low (2/5) · **Reward-to-risk:** 1.8 / 2.4

| | Level | Details |
| --- | --- | --- |
| 🟢 **Entry** | **28,295** | Conditional limit entry after a closed rejection candle |
| 🔴 **Stop loss** | **28,375** | Above the latest swing high, with a buffer |
| 🎯 **TP1** | **28,150** | 1.8R |
| 🎯 **TP2** | **28,100** | 2.4R |
| ⛔ **Invalidation** | **28,375** | A 5-minute candle closes above this level |

Illustrative levels only. Until the trigger is confirmed, the decision is
**NO TRADE**. An index chart's levels are not directly executable on a
different futures or CFD instrument.

## ⚡ Installation

**Claude Code plugin:**

```text
/plugin marketplace add Kirby54/Snap-Trade
/plugin install snap-and-trade@snap-and-trade
```

**Manual installation:** copy `skills/snap-and-trade` to
`~/.claude/skills/` (Windows: `%USERPROFILE%\.claude\skills\`).

**Claude.ai:** zip the `skills/snap-and-trade` folder and import it through
*Settings > Capabilities > Skills*.

Requires Python 3.10+. The scripts use the standard library. Chart analysis
does not require a market-data API key; broker integrations require their
own account and credentials.

## 🧭 Features

**Screenshot mode:** chart reading → market structure → key levels → setup
→ confluence score out of 5 → numerical checks (minimum 1.5 reward-to-risk
and stop placement) → trade plan → position sizing when account capital
is supplied. The decision is **LONG, SHORT or NO TRADE**.

**Module mode:** the 11 tools from
[day-trader-skill](https://github.com/Jakeschincariol/day-trader-skill),
available through one skill:

| Module | Purpose |
| --- | --- |
| 🔎 scanner | Scan US stocks for breakouts, flags, oversold setups and opening ranges |
| 📰 news | Find new Yahoo headlines and SEC 8-K filings |
| 📊 analyst | Read SEC EDGAR quarterly revenue, margins and earnings per share |
| ⏱️ entry | Identify a candle closing above the opening range |
| 🚪 exit | Define the stop and target before entry |
| 🎲 timemachine | Simulate 10,000 sessions and inspect historical setup occurrences |
| 💰 budget | Size a position within account limits |
| 🛡️ risk | Return PASS or BLOCK against the configured risk rules |
| 🏦 broker | Prepare an Alpaca order ticket; paper trading by default, explicit approval required |
| 🔔 alerts | Track price, stop, target and market-opening alerts |
| 🏛️ pelosi | Read publicly disclosed congressional trades |

**Journal mode:** record signals and outcomes, then review win rate, average R,
profit factor and the longest losing streak. Group results by confidence,
setup or asset. Follow the
[replay testing protocol](skills/snap-and-trade/references/backtest.md)
to reduce selection and hindsight bias.

### Market coverage

| Mode or modules | US stocks / ETFs | Crypto, forex, indices, futures | Long | Short |
| --- | --- | --- | --- | --- |
| Screenshot + journal | ✅ | ✅ | ✅ | ✅ |
| news, analyst, scanner, pelosi | ✅ | ❌ | — | — |
| entry, exit, timemachine, budget | ✅ | ❌ | ✅ | ❌ |
| risk, broker (Alpaca), alerts | ✅ | ❌ | ✅ | Exits only |

Screenshot support does not imply that broker and data modules support
every market. Confirm the exact instrument, contract specifications,
account currency and broker constraints before using a calculated size.

## 💬 Usage

- Send a screenshot: “Long or short?”, “Give me SL and TP”, or
  “Analyze this chart; my account is $2,000 and I risk 1%.”
- Call a module: “Scan the market”, “Any news on TSLA?”,
  “Apple earnings”, or “What did Pelosi disclose?”
- Use the journal: “Log this trade”, “Trade #4 hit TP1”, or
  “Show my results by confidence.”

## 📈 Results

No verified profitability results are published yet. Use the
[testing protocol](skills/snap-and-trade/references/backtest.md)
and publish complete results, including losses and unfilled signals.
An initial sample of 30 closed trades is exploratory; it does not establish
a statistical trading edge.

## 🧪 Tests

```bash
python -m unittest discover -s tests
```

The suite runs on every push and pull request across Linux, Windows and
macOS with Python 3.10 and 3.13. The badge shows the actual workflow status.
See [CONTRIBUTING.md](CONTRIBUTING.md) for offline checks and conventions.

```bash
python tools/validate_repo.py
```

### Risk calculations (v2.2)

`plan.py` rejects non-finite numbers, invalid budgets and unordered targets.
It supports currency conversion (`--fx-rate`), estimated round-trip costs
per unit (`--cost-per-unit`), quantity steps (`--qty-step`), minimum size
(`--min-qty`) and a notional cap (`--max-notional`). Quantities are rounded
down. Risk above 2% requires an explicit user request and `--allow-high-risk`.

See [units, examples and limitations](skills/snap-and-trade/references/dimensionnement.md).
The journal accepts `--cost-r` to subtract realized costs from R statistics;
zero means gross results. Existing v2.1 CSV files remain compatible. Journal
access is exclusive and writes use atomic replacement.

### What is checked, and what still needs measurement

| Area | Status |
| --- | --- |
| Calculations, input validation and module behavior | Automated fixture-based tests |
| Repository metadata, manifests and local references | Automated offline checks |
| Model interpretation of chart screenshots | Requires a fixed image set and archived responses |
| Profitability after costs and stability out of sample | Not demonstrated |
| Live provider and broker integration | Depends on services and permissions; fixture tests are insufficient |

A green CI run does not validate a trading strategy. Contributing does not
require placing orders or testing with real money.

## ⚠️ Disclaimer

For technical analysis and education, **not investment advice**.
A screenshot shows past price action; a trade plan is an interpretation,
not a prediction. Stops do not guarantee an execution price or a maximum
loss. Test in a demo or paper account first.

## License

MIT. The day-trader modules are © 2026 Jake Schincariol and retain their
MIT attribution; see [LICENSE](LICENSE).
Release history: [CHANGELOG](CHANGELOG.md).
