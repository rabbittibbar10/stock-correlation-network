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

#random matrix theory:

“Dropped duplicate share classes GOOG and NWS (correlations 0.99 and 0.97 with GOOGL and NWSA): the same company counted twice would double its weight in hub and degree counts.”
“Kept highly correlated different companies (e.g. MET/PRU 0.91, FITB/RF 0.91) because that similarity is real economic structure.”


## Minimum spanning tree (Stage 5)
- Method: Mantegna distance d = sqrt(2(1 - rho)), then the minimum spanning tree (Kruskal's algorithm, via scipy).
  455 stocks, 454 links; checked it is a valid tree.
- Why a tree: it needs no threshold, is always connected, and is equivalent to single-linkage
  hierarchical clustering. Downside: it keeps only N - 1 links and throws away all loops.

### Strongest links (all same-sector, all economically sensible)
- UDR / Vivmark (apartment REITs) 0.92; FRT / REG (shopping-centre REITs) 0.91;
  FITB / RF (regional banks) 0.91; MET / PRU (life insurers) 0.91
- Also: Visa / Mastercard, AMAT / LRCX (chip equipment), DHI / LEN (housebuilders),
  a chain of regional banks (CFG-FITB-RF-KEY) and of Midwest utilities (CMS-LNT-WEC)

### Hubs
- Largest: Parker Hannifin (15), Prudential (15), Moody's (14), Illinois Tool Works (12), Ameriprise (10)
- Diversified industrial suppliers and market-linked financials: firms whose business is a slice of the whole economy
- 57% of stocks are leaves (only one link)

### Sector purity vs null model
- 80.8% of links join same-sector stocks; 11.1% +/- 1.6% expected with shuffled labels
  (1000 shuffles) -> z = 45
- The chance baseline is about sum of (sector share)^2: big sectors make same-sector pairs common by chance
- By sector: Energy 90%, Utilities 90%, Health Care 86% (one dominant driver each)
  ... Communication Services only 25% (prediction from Stage 3 confirmed),
  Consumer Discretionary and Materials about 54%

### Core-periphery
- Financials and Industrials form the core of the tree, where the hubs are
- Real Estate, Utilities, Consumer Staples, Energy and Tech branch off as separate arms
- Matches Onnela et al. (2003). Test properly with k-core in Stage 7

### Finding: Moody's links a "data and ratings" cluster that cuts across GICS sectors
- MCO's 14 neighbours: S&P Global, MSCI, FactSet, Nasdaq, BlackRock, Visa (Financials);
  Equifax, Broadridge, Cintas, Copart (Industrials); Fair Isaac, Verisign, Gen Digital (IT); IQVIA (Health Care)
- What they share is a business model, not a product: asset-light, recurring-revenue,
  high-margin businesses (ratings, indices, credit scores, financial data, payments, licensing)
- So returns group stocks by business model as well as by GICS sector.
  GICS classifies by what a company sells; the market prices how it makes money
- Prediction for Stage 6: Louvain may find a "data/quality" community that lowers ARI vs GICS
  but makes economic sense. A low ARI is not automatically a failure of the method.