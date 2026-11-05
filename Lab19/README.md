# Lab 19 — Legend Panel

Built and verified on 5 November 2026. [Official assignment](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-19-legend-panel.md); [saved instructions](sources/lab-19-legend-panel.md).

## What today’s lab teaches

The panel applies different decision rules to identical SEC facts. Buffett emphasizes profitability and owner earnings; Cathie Wood emphasizes revenue growth and research spending; Burry emphasizes cash backing of earnings and liabilities. Disagreement can follow from different objectives and thresholds without any disagreement about the underlying numbers.

Code performs the calculations and labels each check pass, fail or not known. The AI reads that printed evidence and writes each persona’s memo and verdict. The app displays the three perspectives together. These are simulated perspectives from one model, not three independent sources of evidence; agreement does not make their shared inputs or reasoning independently verified.

Revenue growth is `(last revenue / first revenue) ** (1/4) - 1`. Five consecutive annual observations contain four growth intervals. R&D intensity is annual R&D divided by same-year revenue. Liabilities/equity uses year-end balances. Checks use unrounded values; printed ratios are rounded for readability. The model does not assign a stock price or turn a majority vote into a trading instruction.

## Open and run

The existing app has been extended at [http://127.0.0.1:8518](http://127.0.0.1:8518). Refresh the page if the old Buffett title remains visible.

From the course workspace:

```bash
.venv/bin/python -m streamlit run "ColinSpensley/Project 2/Lab18/buffett_app.py" --server.port 8518 --server.address 127.0.0.1 --server.headless true
.venv/bin/python "ColinSpensley/Project 2/Lab19/panel.py" COST --audit
.venv/bin/python "ColinSpensley/Project 2/Lab19/panel.py" COST --wood-config "ColinSpensley/Project 2/Lab19/cathie-wood-sec/probe-config.json" --output-dir "ColinSpensley/Project 2/Lab19/results/probe_5pct"
```

Choose COST for the known answer. The threshold selector switches between 15% and 5%. It recomputes the checks immediately and warns that saved memos have not been regenerated for the probe. All three memo editors flag unprinted numbers and disable saving a flagged memo. The original chart, SEC downloader, Buffett checks, provenance, original output download, and memo editing/download capabilities remain available.

## Completed: Costco and threshold probe

| Investor | Check | Result |
|---|---|---|
| Buffett | ROE >= 15% every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew from first to last year | pass |
| Cathie Wood | Revenue CAGR >= 15% | fail: 7.51% |
| Cathie Wood | Latest R&D / revenue >= 5% | not known |
| Burry | Operating cash flow >= net income every year | pass |
| Burry | Latest liabilities / equity <= 2 | pass: 1.49 |

The liabilities/equity sequence is 2.11, 1.75, 1.96, 1.64, 1.49. R&D is not found in every year. Every new value and check matches the official answer when recomputed from the preserved SEC download; the answer key is used only for validation.

Lowering Wood’s threshold to 5% makes the growth check pass while R&D remains not known. The company and facts are identical. The implementation retains 15% because it preserves the intended demanding growth screen; this is an AI implementation choice awaiting the student's own rationale, recorded under [Wood's memo](results/COST_wood_memo.md).

- [Full table, checks and provenance](results/COST_output.txt)
- [Buffett memo](results/COST_buffett_memo.md)
- [Wood memo](results/COST_wood_memo.md)
- [Burry memo](results/COST_burry_memo.md)
- [5% probe output](results/probe_5pct/COST_output.txt)
- [Validation record](VALIDATION.md)

## Completed: fund-company run on NVIDIA

The existing Project 2 universe is VOO, BND and VGT. NVIDIA (NVDA) is selected from VGT. Vanguard's indexed holdings listing identifies NVIDIA at 17.15%, ahead of Apple at 16.24% and Microsoft at 10.96%, for its June 2026 portfolio snapshot, retrieved 5 November 2026. This is a dated holdings snapshot, not a claim about live fund weights. [Vanguard VGT portfolio](https://advisors.vanguard.com/investments/products/vgt/vanguard-information-technology-etf).

The user supplied the required SEC contact information, and NVIDIA's raw company facts were downloaded on 5 November 2026. The same verified snapshot feeds every investor. Enter `NVDA` in the app's SEC ticker field to view the populated panel and memos.

| Investor | Check | Result |
|---|---|---|
| Buffett | ROE >= 15% every year | pass |
| Buffett | Owner earnings positive every year | pass |
| Buffett | Owner earnings grew from first to last year | pass |
| Cathie Wood | Revenue CAGR >= 15% | pass: 68.30% |
| Cathie Wood | Latest R&D / revenue >= 5% | pass: 8.57% |
| Burry | Operating cash flow >= net income every year | fail |
| Burry | Latest liabilities / equity <= 2 | pass: 0.31 |

The cash-flow test fails in FY2022, FY2024, FY2025 and FY2026. Latest operating cash flow is 102,718 against net income of 120,067, in USD millions. These totals identify a reconciliation question; they do not establish its cause or prove accounting misconduct. All required inputs are present under the permitted tags for this company.

The model-written verdicts are Buffett **watch it**, Wood **pursue research**, and Burry **watch it**. Buffett's positive owner earnings and Wood's growth evidence can coexist with Burry's cash-conversion concern because their tests address different properties of the same business. These judgments do not assess the stock's price.

- [NVIDIA table, checks and provenance](results/NVDA_output.txt)
- [Buffett memo](results/NVDA_buffett_memo.md)
- [Wood memo](results/NVDA_wood_memo.md)
- [Burry memo](results/NVDA_burry_memo.md)

To reproduce from the saved snapshot:

```bash
.venv/bin/python "ColinSpensley/Project 2/Lab19/panel.py" NVDA --audit
```

To refresh later, set `SEC_USER_AGENT` to your actual name and email, then run:

```bash
.venv/bin/python "ColinSpensley/Project 2/Lab18/buffett-sec/scripts/buffett.py" NVDA --output-dir "ColinSpensley/Project 2/Lab18/results"
.venv/bin/python "ColinSpensley/Project 2/Lab19/panel.py" NVDA
```

After refreshing the facts, regenerate all three memos from the new printed output and audit with `panel.py NVDA --audit`. Current memos are already saved and audited. Personal decisions and the partner exercises below remain necessary before claiming the full lab floor is met.

## Skills and calculation files

- [Existing Buffett skill](../Lab18/buffett-sec/SKILL.md)
- [Cathie Wood skill](cathie-wood-sec/SKILL.md), [retained threshold](cathie-wood-sec/config.json), [probe threshold](cathie-wood-sec/probe-config.json)
- [Burry skill](burry-sec/SKILL.md)
- [Shared calculation engine](panel.py), [panel UI](panel_ui.py), [existing app entry point](../Lab18/buffett_app.py)
- [Financial and audit tests](test_panel.py)

The new skills are linked in the repository's `.agents/skills/` directory alongside Buffett. Both skill manifests passed the bundled validator. FAskills was read as a philosophy reference and was not installed. Its forecasts and paid data requirements do not apply to this lab.

## Your own work still required

1. Complete the no-screen opening discussion with your partner using the assigned philosophy pages.
2. Complete the six-minute, no-AI code explanation of `wood_checks` in `panel.py`; answer your partner's missing-input question yourself. No line-by-line answer is supplied here.
3. Use the completed NVIDIA panel to argue the bull and bear cases with your partner, two sentences each, and swap. Record what actually happened.
4. Write your own retained-threshold rationale and one-line decision: would you let this panel screen companies for Project 2, and under what condition?
5. Explain the panel's agreement/disagreement and the threshold lesson to your partner, then record your own reflection.
6. Open Brightspace → Quizzes → Lab 19 and submit GitHub links to the relevant files individually. No Git remote is configured in this workspace, so no files have been published and no checkout has been submitted.

The lab's no-AI instruction applies to the partner code explanation. The partner exchange and personal judgment have not been performed or attributed to the student.

## Sources and limitations

- [Official Lab 19](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/lab-19-legend-panel.md) and [week 11 handout](https://github.com/CinderZhang/FIN43900-Fall2026/blob/main/lessons/week-11/student-handout.md), retrieved 5 November 2026.
- [Cathie Wood philosophy](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/cathie_wood.md), [Burry philosophy](https://github.com/CinderZhang/FAskills/blob/main/financial-researcher/experts/michael_burry.md), read 5 November 2026.
- [SEC APIs](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) and [Streamlit columns](https://docs.streamlit.io/develop/api-reference/layout/st.columns).

Financial inputs are annual USD company-facts observations from 10-K filings under the lab's allowed tags; this is not a full reading of five filings and their footnotes. Existing Lab18 350–380-day annual-period filtering, ordered fallbacks and latest-filing selection remain in force. Missing inputs and nonpositive-equity ratios remain unknown. Latest-filed comparisons can include restatements and are not a point-in-time backtest. The memo audit checks token presence, not whether each figure is attached to the correct metric, scale, date or interpretation.

AI assistance: Codex implemented the skills, deterministic checks, panel UI, memos and verification. The student's personal choice, explanations, partner participation and submission remain pending.
