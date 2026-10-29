# Project 2 fund universe — draft

**Student-selected tickers:** VOO, BND, VGT.  
**Verified:** 29 October 2026 against [Vanguard's ETF list](https://investor.vanguard.com/investment-products/list/etfs).

| Ticker | Full fund name | Intended role |
|---|---|---|
| VOO | Vanguard S&P 500 ETF | Broad U.S. large-cap equity exposure |
| BND | Vanguard Total Bond Market ETF | Broad U.S. investment-grade fixed-income exposure |
| VGT | Vanguard Information Technology ETF | U.S. information-technology sector tilt |

The three tickers meet [Lab 14's three-to-six-fund universe count](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-09/lab-14-portfolio-baselines.md#before-thursday--your-own-universe-in-funds). VGT overlaps with the technology holdings already in VOO, so the portfolio's total technology exposure needs a look-through concentration check. BND is a broad bond fund, not a Treasury-bill or cash reserve fund. If the student's own mandate includes a dedicated reserve minimum, identify an eligible holding or revise the mandate transparently; do not silently count BND as cash.

**Still to define from the student's own mandate:** intended user, numeric objective, benchmark, horizon/rebalancing, reserve/liquidity rule, concentration limits, and other hard constraints. The Meridian Foundation rules are course training inputs, not this universe's mandate. [Project 2 requirements](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/projects/project-2-investment-management-application.md) require these fields.

**Still to source for Lab 15 / Project 2:** five years of monthly adjusted-close prices in `prices.csv`, with a source and download date for each ticker. No prices, returns, or portfolio weights are inferred here.
