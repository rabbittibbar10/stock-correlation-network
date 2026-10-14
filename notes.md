# Project notes

Working notes for the S&P 500 correlation network project: what I did, what I found,
and why I made each choice. Raw material for the README.

## Data (Stage 2)
- Source: S&P 500 constituents and GICS sectors from Wikipedia; adjusted daily closes
  from Yahoo Finance (yfinance), 2015-01-01 to 2025-12-31.
- 503 tickers (more than 500 because some companies have two share classes, e.g. GOOG/GOOGL).
- 11 GICS sectors, very uneven: Industrials 83 stocks, Energy 21.
- 2,765 trading days (about 252 per year).
- 3 tickers had no data at all (FDXF, VYLR, HONA): they started trading after the window ended.
- Adjusted prices (auto_adjust=True) so stock splits and dividends don't show up as fake crashes.

## Cleaning (Stage 3)
- Rule: keep only stocks with a complete price history; forward-fill gaps of up to 5 days
  (e.g. trading halts).
- Result: 457 stocks. 46 dropped, mostly IPOs (ABNB, UBER, PLTR, COIN, MRNA) and
  spin-offs (CARR, OTIS, KVUE, GEHC, GEV, DOW). PYPL and HPE listed during 2015, so they
  miss the start of the window.
- Trade-off: this keeps the full 2015-2025 window, including a normal year before COVID,
  at the cost of survivorship bias. The sample only contains companies in the index today.
- Duplicate share classes: dropped GOOG and NWS (correlations 0.99 and 0.97 with GOOGL and
  NWSA). The same company counted twice would double its weight in hub and degree counts.
  -> 455 stocks, 2,764 daily returns.
- Kept highly correlated *different* companies (MET/PRU 0.91, FITB/RF 0.91, FRT/REG 0.91,
  UDR/Vivmark 0.92): that similarity is real economic structure.
- Using log returns: they add up over time and are standard in quant finance.

## Sanity checks
- The largest one-day falls are all real events:
  - APA, OXY: 2020-03-09, Saudi-Russia oil price war (oil fell about 25% that day)
  - PCG: 2019-01-14, PG&E bankruptcy over wildfire liabilities
  - GL: 2024-04-11, short-seller report on Globe Life
  - SMCI: 2018-10-04, Bloomberg "The Big Hack" spy-chip story
  - FISV: 2025-10-29, guidance cut
- A log return of -0.77 means a price drop of about 54% (e^-0.77 = 0.46).

## Correlations (Stage 3)
- Mean pairwise correlation 0.349; same sector 0.458; different sectors 0.335.
- Being in the same sector adds only about 0.12. Most co-movement comes from the market
  as a whole (the market mode).
- Clear sector blocks: Energy, Financials, Real Estate, Utilities.
- Weak blocks: Health Care, Consumer Staples (defensive sectors). Communication Services
  is barely a block (Google, Meta, Netflix, telecoms and media are very different businesses).
- Prediction: community detection will struggle to recover Communication Services.

## Random matrix theory (Stage 4)
- Eigenvalues of the correlation matrix sum to N = 455 (the trace), as they must.
- Largest eigenvalue 165: the market mode explains 36.3% of all variance.
- The market eigenvector has a positive weight on every stock, and its returns correlate
  0.999 with an equal-weighted index, so eigenvector 1 *is* the market.
- Next eigenvalues: 24.6, 17.2, 8.5, 6.4, 6.2, ...
- 35 eigenvalues lie above the Marchenko-Pastur noise bound (1.26, using noise variance
  1 - lambda_1/N). The rest are indistinguishable from noise.
- The Marchenko-Pastur curve fits the bulk poorly: real returns have fat tails and
  time-varying volatility, and the other signal modes also take variance.
  Treat the bound as a guide, not an exact cutoff.
- Before removing duplicate share classes, the smallest eigenvalue was 0.004: GOOGL vs GOOG
  with weights +/- 1/sqrt(2), a long-short portfolio of two near-identical assets with almost
  no variance. After removing GOOG and NWS it rose to 0.05, confirming it was a duplicate
  artifact. The headline numbers (165, 36%, 35 modes) barely changed.
- Leading eigenvectors are known style factors:
  - eigenvector 2: Utilities (+) vs Information Technology (-) = defensive vs growth
  - eigenvector 3: Tech and Health Care (+) vs Energy and Financials (-) = growth vs value
- Other eigenvectors map onto single sectors: Real Estate (4), Energy (5), Health Care (8).
- After removing the market mode and noise: same-sector 0.087 vs different-sector -0.011
  (before: 0.458 vs 0.335). The sector signal is no longer buried under the market.
- Filtered heatmap shows a fault line: Utilities, Real Estate and Consumer Staples
  (rate-sensitive, "bond-like") are positively linked to each other and negatively to
  Tech, Energy and Financials. Hypothesis: interest rates move them in opposite directions.

## Minimum spanning tree (Stage 5)
- Method: Mantegna distance d = sqrt(2(1 - rho)), then the minimum spanning tree
  (Kruskal's algorithm, via scipy). 455 stocks, 454 links; checked it is a valid tree.
- Why a tree: it needs no threshold, is always connected, and is equivalent to
  single-linkage hierarchical clustering. Downside: keeps only N - 1 links, no loops.

### Strongest links (all same-sector, all economically sensible)
- UDR / Vivmark (apartment REITs) 0.92; FRT / REG (shopping-centre REITs) 0.91;
  FITB / RF (regional banks) 0.91; MET / PRU (life insurers) 0.91
- Also: Visa / Mastercard, AMAT / LRCX (chip equipment), DHI / LEN (housebuilders),
  a chain of regional banks (CFG-FITB-RF-KEY) and of Midwest utilities (CMS-LNT-WEC)

### Hubs
- Largest: Parker Hannifin (15), Prudential (15), Moody's (14), Illinois Tool Works (12),
  Ameriprise (10)
- Diversified industrial suppliers and market-linked financials: firms whose business is
  a slice of the whole economy
- 57% of stocks are leaves (only one link)

### Sector purity vs null model
- 80.8% of links join same-sector stocks; 11.1% +/- 1.6% expected with shuffled labels
  (1000 shuffles) -> z = 45
- The chance baseline is about sum of (sector share)^2: big sectors make same-sector
  pairs common by chance
- By sector: Energy 90%, Utilities 90%, Health Care 86% (one dominant driver each);
  Communication Services only 25% (prediction from Stage 3 confirmed);
  Consumer Discretionary and Materials about 54%

### Core-periphery
- Financials and Industrials form the core of the tree, where the hubs are
- Real Estate, Utilities, Consumer Staples, Energy and Tech branch off as separate arms
- Matches Onnela et al. (2003). Test properly with k-core in Stage 7

### Finding: Moody's links a "data and ratings" cluster across GICS sectors
- MCO's 14 neighbours: S&P Global, MSCI, FactSet, Nasdaq, BlackRock, Visa (Financials);
  Equifax, Broadridge, Cintas, Copart (Industrials); Fair Isaac, Verisign, Gen Digital (IT);
  IQVIA (Health Care)
- What they share is a business model, not a product: asset-light, recurring-revenue,
  high-margin businesses (ratings, indices, credit scores, financial data, payments)
- Returns group stocks by business model as well as by GICS sector. GICS classifies by
  what a company sells; the market prices how it makes money

## Communities vs GICS sectors (Stage 6)
- Louvain on the complete graph weighted by positive correlations (negative weights set
  to 0, because Louvain needs non-negative weights), swept over resolution 0.5-3.0.
  Scored against GICS with ARI, homogeneity and completeness.

| Method | ARI vs GICS |
|---|---|
| Hierarchical (average linkage), raw | 0.01 |
| Louvain, raw (resolution 1.25) | 0.32 +/- 0.01 (10 seeds) |
| Hierarchical, market mode removed | 0.40 (deterministic) |
| Louvain, market mode removed (resolution 2.0) | 0.52 +/- 0.04 (10 seeds) |

- Louvain is random: seed 0 gave 0.57, about one standard deviation above the mean,
  so I report the mean over 10 seeds.
- Removing the market mode is the key step: Louvain 0.32 -> 0.52, hierarchical 0.01 -> 0.40.
- On raw correlations at low resolution, ARI = 0: everything falls into one community
  (the market).
- At the best resolution Louvain found exactly 11 communities, matching the number of
  sectors without being told. Homogeneity and completeness balanced (0.68 each).
- Caveat: resolution was tuned against the labels, so this is a best case (same as thesis).

### What the communities are (seed 0, resolution 2.0)
- 0: "Steady fee businesses" (38 stocks): property & casualty insurers (Chubb, Travelers,
  Progressive, Allstate, Berkley), insurance brokers (Aon, Marsh McLennan, Gallagher,
  Willis Towers Watson), exchanges (CME, ICE, Cboe, Nasdaq), ratings and data (Moody's,
  S&P Global, FactSet, Verisk), payments and payroll (Visa, Fiserv, FIS, ADP, Paychex),
  plus waste (Waste Management, Republic), Cintas, Ecolab, Linde, McDonald's, Yum
- 1: "Market- and rate-sensitive financials" (42 stocks): banks (JPMorgan, Bank of America,
  Citi, Wells Fargo, regional banks), investment banks and brokers (Goldman Sachs, Morgan
  Stanley, Schwab), asset managers and custodians (BlackRock, T. Rowe Price, State Street,
  BNY Mellon), life insurers (MetLife, Prudential, Aflac), consumer credit (AmEx,
  Capital One, Synchrony)
- So Financials split by business model: community 1 earns from balance sheets and asset
  prices, so it rises and falls with interest rates, credit and markets; community 0 earns
  steady premiums, fees and subscriptions, and joins non-financial firms with the same
  recurring, low-cyclicality revenue
- 2: Tech (60 IT + some Communication Services and Financials, e.g. Mastercard, MSCI)
- 3: Retail (Costco, AutoZone, Best Buy, Casey's) - mixes Discretionary and Staples
- 4: Commodities: Energy + agriculture and chemicals (APA, Baker Hughes, ADM, Bunge, CF)
- 5: Industrial cyclicals + Materials
- 6: Consumer Staples
- 7: Travel and leisure (Boeing, Booking, Carnival, Aptiv)
- 8: Defence (Lockheed, General Dynamics, L3Harris, Huntington Ingalls, Leidos):
  driven by government budgets, not the economic cycle
- 9: Health Care (56 of 61 Health Care stocks: the cleanest sector)
- 10: Utilities + Real Estate (rate-sensitive, matches the filtered heatmap)
- Communication Services scattered across four communities (third confirmed prediction)
- The data-and-ratings cluster from the tree mostly lands in community 0 (Moody's,
  S&P Global, FactSet, Verisk, Visa); MSCI, Fair Isaac, Verisign and Mastercard went to Tech
- Most disagreements with GICS are economically meaningful groupings, so 0.52 understates
  how much real structure the method finds. Same lesson as the thesis.

## Open questions / ideas
- Empirical noise model: shuffle each stock's returns in time (keeps fat tails, destroys
  cross-correlation), recompute the largest eigenvalue 100 times, compare with Marchenko-Pastur.
- Spearman vs Pearson correlation: does a rank-based measure change the structure?
- Second crisis window: the 2022 rate-hike selloff vs the 2020 COVID crash.