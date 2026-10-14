# Project notes

## Data (Stage 2)
- Source: S&P 500 constituents and GICS sectors from Wikipedia; adjusted daily closes from Yahoo Finance (yfinance), 2015-01-01 to 2025-12-31.
- 503 tickers (more than 500 because some companies have two share classes, e.g. GOOG/GOOGL).
- 11 GICS sectors, very uneven: Industrials 83 stocks, Energy 21.
- 2,765 trading days (about 252 per year).
- 3 tickers had no data at all (FDXF, VYLR, HONA): they started trading after the window ended.

## Cleaning (Stage 3)
- Rule: keep only stocks with a complete price history; fill gaps of up to 5 days.
- Result: 457 stocks. 46 dropped, mostly IPOs (ABNB, UBER, PLTR, COIN) and spin-offs (CARR, OTIS, KVUE, GEHC, GEV).
- Trade-off: this keeps the full 2015–2025 window, including a normal year before COVID, at the cost of survivorship bias. The sample only contains companies that are in the index today.
- Using log returns because they add up over time and are standard in quant finance.

## Sanity checks
- The largest one-day falls are all real events:
  - APA, OXY: 2020-03-09, Saudi–Russia oil price war (oil fell about 25% that day)
  - PCG: 2019-01-14, PG&E bankruptcy over wildfire liabilities
  - GL: 2024-04-11, short-seller report on Globe Life
  - SMCI: 2018-10-04, Bloomberg "The Big Hack" spy-chip story
  - FISV: 2025-10-29, guidance cut
- A log return of -0.77 means a price drop of about 54%.

## Correlations (Stage 3)
- Mean pairwise correlation 0.349; same sector 0.458; different sectors 0.335.
- Being in the same sector adds only about 0.12. Most co-movement comes from the market as a whole (the market mode).
- Clear sector blocks: Energy, Financials, Real Estate, Utilities.
- Weak blocks: Health Care, Consumer Staples (defensive sectors). Communication Services is barely a block (Google, Meta, Netflix, telecoms and media are very different businesses).
- Prediction: community detection will struggle to recover Communication Services as one group.

## Open questions / ideas
-