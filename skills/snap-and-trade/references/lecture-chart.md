# Reading chart screenshots

Record observations, not guesses. Read the execution and context charts together.

## Price source and identity

1. Record exact ticker, instrument type, venue/provider and contract month if
   relevant. Cash indices, futures, CFDs and ETFs are different instruments.
2. Identify timeframe, date, timezone and last complete candle on each image.
   If any is unclear, request clarification rather than inventing context.
3. Prefer the **latest-price label on the price axis**, attached to the last
   traded price. Distinguish it from order, bid/ask, indicator and drawing labels.
4. The **header OHLC follows the cursor/crosshair** on many platforms: it may
   describe a historical candle. Never use it as the current price by default.
5. A watchlist/quote panel may show another instrument, a stale quote, a bid
   or the prior close. Note discrepancies explicitly. Example: header 8394,
   panel 8361, latest-price axis label 8372 → use 8372 and flag the other two.
6. If the axis label is unreadable or ambiguous, ask for a clearer image or
   a user-confirmed latest price. No executable signal from guessed digits.
7. Read multiple price-axis graduations; handle log scale and decimals.

## Structure and two timeframes

- Higher highs/lows indicate upward structure; lower highs/lows downward;
  repeated bounds a range. A single opening gap does not establish trend.
- Use a higher timeframe of the same instrument (5m + 1h is the default pair).
  Require overlapping dates and the same timezone reference. If it is missing,
  request it and keep the result conditional, with NO TRADE now.
- Confirm swing breaks with closed candles. Read support/resistance as zones,
  with visible pivots and retests. Do not invent levels hidden by a crop.

## Confirmation and volatility

- Exclude the forming candle from confirmation and averages.
- Estimate mean **high minus low** across 10–20 recent closed candles on the
  execution timeframe. Record sample count, units and approximation. This is
  not body size, an overnight gap or ATR; do not call it ATR.
- Stop: beyond structural invalidation plus a buffer, and entry-stop distance
  at least 1.5 times that mean range. If no defensible structure meets both
  that floor and the minimum R:R, abstain. The floor is an uncalibrated safety
  heuristic, not a guarantee against noise or a statistically optimal stop.
- An absent indicator is unavailable, not bearish or a zero point. A cash
  index with no meaningful volume has volume unavailable. Do not substitute
  futures volume without identifying that different instrument and limitation.

## Freshness and closed markets

Use the exact instrument's session/calendar. Do not infer that CAC 40 uses
NYSE hours. If the market is closed, return an opening plan with cancellation
bounds and a next-session recheck. If date/time/freshness is unknown, ask for
it and abstain. Never execute from an old screenshot or describe a delayed
provider quote as real time.
