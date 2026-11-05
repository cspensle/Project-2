---
name: burry-sec
description: Run the Lab 19 Burry cash-earnings and liabilities screen on shared annual SEC facts and write an evidence-bound memo. Use for the Legend Panel or a Burry-inspired business screen; excludes short recommendations and valuation.
---

# Burry SEC screen

Read [the FAskills philosophy](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md) for skepticism, cash earnings and balance-sheet scrutiny. Do not install it. The lab supersedes its price targets, forecasts and paid data requests.

Run `python3 <Lab19>/panel.py TICKER --facts-file <raw-companyfacts.json>` using [the shared engine](../panel.py), then read the output and provenance. Use the identical snapshot as Buffett and Wood. The existing Lab18 downloader requires the user's real name and email.

Operating cash flow must be >= net income in every one of five annual periods. Latest liabilities / year-end equity must be <= 2. Missing required inputs make the relevant check not known; nonpositive equity makes the ratio not known. Use the Liabilities tag directly; do not estimate it from assets. The shared engine preserves Lab18 annual USD, 10-K-only, ordered-tag and latest-filing rules.

Write `<Lab19>/results/TICKER_burry_memo.md` in a skeptical first-person voice, explicitly an AI simulation rather than Burry's actual view. Start with `**Verdict: ...**`, choosing pursue research, watch it, or pass for this screen. Explain cash backing, balance-sheet evidence, limitations and what would change the judgment. Passing these checks neither proves clean accounting nor excludes hidden obligations. Do not allege fraud, infer debt safety, or make short recommendations from these ratios. Use printed numbers, dates, rounding and USD-million units only. No price data or invented footnote findings.

Run `panel.py TICKER --audit` against the same input; inspect numerical context as well as token flags. Preserve the student's decision and partner exercises as their own work.
