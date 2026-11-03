# Lab 18 — Legend Investor as Skill

Source: [official Lab 18](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-18-legend-investor-as-skill.md), read 3 November 2026.

## Run

From the course workspace:

```bash
.venv/bin/python -m streamlit run "ColinSpensley/Project 2/Lab18/buffett_app.py"
```

The current session launched it at [localhost:8518](http://127.0.0.1:8518).

Enter your name and email in the app's SEC download panel. Download COST and JPM,
or set `SEC_USER_AGENT` in your terminal and run:

```bash
.venv/bin/python "ColinSpensley/Project 2/Lab18/buffett-sec/scripts/buffett.py" COST --output-dir "ColinSpensley/Project 2/Lab18/results"
.venv/bin/python "ColinSpensley/Project 2/Lab18/buffett-sec/scripts/buffett.py" JPM --output-dir "ColinSpensley/Project 2/Lab18/results"
```

Ask Codex to use `$buffett-sec` on each ticker and save its memo in `results/`.
The script computes the numbers; Codex writes the judgment after reading those
numbers. The app displays saved memos and permits editing and downloading them.
For another ticker, download its facts and request its memo the same way.

- [Skill instructions](buffett-sec/SKILL.md)
- [Bundled SEC script](buffett-sec/scripts/buffett.py)
- [Streamlit app](buffett_app.py)
- [Verification tests](test_buffett.py)

## Rules and limitations

All monetary values are USD millions in the table and USD in the JSON report.
ROE uses year-end equity, not average equity. It is displayed to one decimal
percentage point; checks use the unrounded ratio. Cash capital spending is
subtracted as a positive outflow. The lab defines owner earnings as operating
cash flow less total capital spending; this is not a separately estimated
maintenance-capex measure.

Annual flows must span 350–380 days, covering calendar and 52/53-week years.
Short transition periods are excluded. The last five eligible fiscal-year-end
dates are selected. The script uses only 10-K filings, USD units, and the exact
tags ordered in the lab. It selects the latest filing within the preferred
available tag, never a quarterly or year-to-date flow. Comparative observations
are labeled by their actual period end, not the filing's fiscal year.

Missing values are `not found`; a ratio with absent inputs or nonpositive equity
is `not known`. A check with absent required inputs is `not known`. The growth
check requires first and last owner earnings; the annual checks require every
year. An incomplete five-year history does not pass. No liabilities ratio is
requested or displayed.

Each raw download is preserved with its source URL, timestamp, and SHA-256
digest. Per-value provenance contains the XBRL tag, period, filing date, and
accession. Latest-filed comparisons can contain restatements and are not a
point-in-time backtest. Missing allowed tags do not establish that an economic
cost is zero, particularly for a bank.

The memo audit compares numeric tokens against the formatted financial table
and check threshold, preserving signs and percentage units. It permits comma
and decimal formatting equivalents. It flags invented numeric amounts, dates,
and percentages, but cannot prove that a printed number is used with the right
metric, year, scale, or interpretation. It does not validate claims expressed
entirely in words. Review the memo's reasoning separately.

The [FAskills Buffett page](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/warren_buffett.md)
was read as a philosophy reference only. FAskills was not installed and its
paid data sources were not used. Price data, intrinsic value, and margin of
safety are outside this lab's scope. The memo is an AI simulation of a
Buffett-inspired approach, not Buffett's actual opinion.

## Verification

```bash
.venv/bin/python -m unittest discover -s "ColinSpensley/Project 2/Lab18" -p 'test_*.py' -v
```

The synthetic extraction checks passed on 3 November 2026: annual versus
quarterly filtering; latest-filed selection; 53-week years; tag fallback;
missing capital spending; nonpositive equity; unrounded threshold checks; and
unsupported memo numbers. The empty-state Streamlit app rendered without an
exception. The user's saved COST download was subsequently recomputed and
matched every value in the official answer; all three financial checks pass.
The [COST memo](results/COST_memo.md) is saved and passes its numeric audit.
The app rendered the populated report and flagged an injected 40.0% in an
automated editor probe. See the [COST validation record](results/COST_validation.md).
JPM data, checks, and memo remain pending. The tests keep the official COST answer exclusively as a validation
fixture; the extraction script never uses it as financial data.

## Individual coursework still required

- Under the COST memo, write your own line stating whether you trust the
  verdict and why. No personal decision has been attributed to you.
- Perform the fresh-chat/no-skill comparison and record where that chat's
  figures came from. This is separate from the scripted extraction tests.
- Complete the no-AI partner discussion, line-by-line explanation of
  `year_row`, partner questions, and reflections.
- Open the Lab 18 Brightspace quiz and submit the required GitHub links.
  This workspace currently has no Git remote configured; nothing has been
  published or submitted.

AI assistance: Codex researched the assigned sources, wrote the skill, script,
app and tests, and ran the recorded checks. The student retains responsibility
for personal judgments, partner participation, and checkout.

## Skill discovery and sources

The submission copy of the skill is `buffett-sec/`. It is installed through a
relative symlink at the documented repository discovery location,
`.agents/skills/buffett-sec`, pointing to this same source folder. Its manifest
passed the bundled skill validator. See [Codex skills](https://developers.openai.com/codex/skills).

Data interfaces: [SEC company ticker map](https://www.sec.gov/files/company_tickers.json),
[SEC API documentation](https://www.sec.gov/search-filings/edgar-application-programming-interfaces).
App reference: [Streamlit line chart](https://docs.streamlit.io/develop/api-reference/charts/st.line_chart).
