---
name: buffett-sec
description: Analyze a public company with the Lab 18 Buffett business-quality framework using five annual SEC EDGAR reports, deterministic financial checks, and a saved evidence-bound memo. Use for Buffett-style business analysis or Lab 18; excludes stock-price targets and valuation.
---

# Buffett business analysis from SEC facts

Run the bundled `scripts/buffett.py` for the requested ticker before making any
numerical claim. It needs no API key. Set `SEC_USER_AGENT` to the user's real name
and email, or pass `--user-agent`. Ask for missing contact information; never
invent it. Use an output directory in the user's project.

```bash
python3 <skill-directory>/scripts/buffett.py COST --output-dir <project>/results
```

Read the printed table, checks, and provenance. The script saves raw SEC facts,
a JSON report, and the identical text output. An existing snapshot can be
recomputed offline with `--facts-file <raw-json>`. Do not replace missing values
with web research, an estimate, or the course answer key.

The script uses only USD facts from 10-K filings, annual flow periods of 350–380
days (including 52/53-week years), and the latest filing for the same period.
Rows are labeled by actual fiscal-year-end date, not the filing's `fy` field.
Revenue and capital spending use the lab's ordered fallback tags. ROE is net
income divided by year-end equity; owner earnings is operating cash flow minus
total capital spending. Missing inputs stay `not found`; checks with any missing
input and ratios with nonpositive equity stay `not known`. Do not silently
change these rules to make an answer key match.

Write `<output-dir>/<TICKER>_memo.md` after reading the actual output. Use a
short Buffett-inspired first-person voice and label it an AI learning
simulation, not a statement by Buffett. Choose **own the business**, **watch
it**, or **pass**. The model makes that judgment; no script assigns the verdict.
Explain the evidence, limitations, and what would change the judgment. For a
company with missing owner earnings, explicitly say it cannot be judged.

Use only numeric values and fiscal years printed in the table and checks;
copy the displayed units and rounding. Do not compute additional numbers in
prose. Do not infer a moat, management quality, or debt safety from these checks
alone. Do not include a market price, price target, investment return forecast,
intrinsic value, or margin of safety. Check the memo:

```bash
python3 <skill-directory>/scripts/buffett.py COST --output-dir <project>/results --facts-file <project>/results/COST_companyfacts.json --memo <project>/results/COST_memo.md
```

Repair flagged numbers before delivery. The checker verifies numeric presence,
not whether a number is attached to the right year, metric, or economic claim;
review that manually. Preserve the student's personal decision and no-AI
partner exercises as their own work.

## Sources and scope

- [Lab 18 rules and known answer](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md)
- [FAskills Buffett page](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md): philosophy reference only. Do not install FAskills or use its paid data services. The lab's cash-flow proxy supersedes that page's maintenance-capex estimates and price-based analysis.
- [SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [Codex skill discovery](https://developers.openai.com/codex/skills)
