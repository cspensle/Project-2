---
name: cathie-wood-sec
description: Run the Lab 19 Cathie Wood growth and R&D screen on five annual SEC periods and write a memo from printed evidence. Use for the Legend Panel or a Wood-inspired business screen; excludes price targets.
---

# Cathie Wood SEC screen

Read [the FAskills philosophy](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/cathie_wood.md) as a reference for innovation, reinvestment and growth. Do not install it. Lab rules supersede its forecasts, price targets and paid data requests.

Run `python3 <Lab19>/panel.py TICKER --facts-file <raw-companyfacts.json>` using [the shared engine](../panel.py). Read the printed table, checks and provenance before judging. All panel members must use the same snapshot. Downloads use the existing Lab18 SEC downloader and the user's real name and email.

The default [config](config.json) requires revenue CAGR >= 15%; the [probe config](probe-config.json) sets 5% and is passed with `--wood-config`. CAGR is (last revenue / first revenue)^(1/4) - 1 over five consecutive annual periods. Latest R&D / revenue must be >= 5%. The code compares unrounded numbers. Annual USD flows must be 350–380 days, 10-K only, latest filing within the lab's ordered tags. R&D falls back to ResearchAndDevelopmentExpenseExcludingAcquiredInProcessCost. Missing inputs remain not known; never treat absent R&D as zero.

Write `<Lab19>/results/TICKER_wood_memo.md` in an innovation-focused first-person voice, labeled an AI simulation rather than Wood's actual view. Start with `**Verdict: ...**` and choose pursue research, watch it, or pass for this screen. Explain the growth and reinvestment evidence, gaps and what would change the judgment. Financial ratios do not prove disruption or future growth. Use only printed numbers, years, units and rounding; do not add price data, forecasts, market-size estimates or unsupported business claims. The model writes the verdict, never a mechanical vote.

Audit all memos with `panel.py TICKER --audit` using the same facts and configuration. Correct unsupported numbers and manually review their context. Record the retained threshold and rationale under the memo as an AI implementation choice until the student supplies their own decision. Keep personal judgments and no-AI partner work pending.
